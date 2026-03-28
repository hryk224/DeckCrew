import asyncio
import logging
from collections import Counter

from deckcrew.agent.base import AudienceAgent, CriticAgent, DJAgent
from deckcrew.agent.models import (
    AgentInput,
    AudienceInput,
    CriticInput,
    Critique,
    Proposal,
    Reaction,
    SpeakingIntent,
    TurnVote,
)
from deckcrew.api.event_bus import EventBus
from deckcrew.api.events import (
    EVENT_DECISION,
    EVENT_FEEDBACK,
    EVENT_PROPOSALS,
    EVENT_STATE,
    AudienceFeedbackContent,
    CriticFeedbackContent,
    FeedbackItem,
    SSEEvent,
)
from deckcrew.memory.base import MemoryStore
from deckcrew.memory.models import InterventionRecord, PreferenceProfile
from deckcrew.memory.preference import apply_preference_bonus
from deckcrew.music.base import MusicBackend
from deckcrew.orchestrator.meeting import DialogueMode, MeetingContext
from deckcrew.orchestrator.models import Decision, DialogueMetadata, RejectionDetail, RoundInfo, TurnResult
from deckcrew.orchestrator.repetition import detect_repetition
from datetime import UTC, datetime

from deckcrew.state.models import (
    MAX_RECENT_CHANGES,
    ChangeKind,
    ChangeRecord,
    MusicParams,
    Section,
    SessionState,
    SectionState,
    TransitionIntent,
)
from deckcrew.venue.models import VenueContext
from deckcrew.state.store import SessionStore
from deckcrew.venue.time_resolver import resolve_time_of_night

from deckcrew.orchestrator.config import (
    AUDIENCE_DIR_THRESHOLD,
    AUDIENCE_ENERGY_BONUS,
    CRITIC_ENERGY_BONUS,
    MAX_MESSAGES_PER_TURN,
    MINOR_MAX_BPM_DELTA,
    MINOR_MAX_ENERGY_DELTA,
    PEAK_SUSTAIN_TURNS,
    VENUE_EARLY_BONUS,
    VENUE_ENERGY_BONUS,
)

logger = logging.getLogger(__name__)

# Section progression order
_SECTION_ORDER: list[Section] = ["intro", "build", "peak", "release"]


def _compute_change_score(current: MusicParams, proposed: MusicParams) -> float:
    """Score how much a proposal differs from the current state."""
    score = 0.0
    score += abs(current.bpm - proposed.bpm) / 200.0
    score += abs(current.energy - proposed.energy)
    if current.focus != proposed.focus:
        score += 0.3
    if current.texture != proposed.texture:
        score += 0.2
    return score


def _apply_feedback_bonus(
    base_score: float,
    proposed: MusicParams,
    current: MusicParams,
    critique: Critique,
    reactions: list[Reaction],
    venue: VenueContext | None = None,
) -> tuple[float, list[str]]:
    """Adjust score based on feedback and venue. Returns (adjusted_score, bonus_notes).

    - Critic severity medium or high: bonus for proposals that raise energy.
    - Audience energy_delta sum > 0: bonus for proposals that raise energy.
    - Audience majority direction: small bonus when most audiences agree.
    - Venue room_size / time_of_night: small bonus aligned with setting.
    """
    score = base_score
    notes: list[str] = []

    proposes_more_energy = proposed.energy > current.energy
    proposes_less_energy = proposed.energy < current.energy

    # Critic bonus
    if critique.severity in ("medium", "high") and proposes_more_energy:
        score += CRITIC_ENERGY_BONUS
        notes.append(f"critic flagged: {critique.issue}")

    # Audience bonus (sum of energy_delta across all audiences)
    total_delta = sum(r.energy_delta for r in reactions)
    if total_delta > 0 and proposes_more_energy:
        score += AUDIENCE_ENERGY_BONUS

    # Audience majority direction
    up_count = sum(1 for r in reactions if r.energy_delta > AUDIENCE_DIR_THRESHOLD)
    down_count = sum(1 for r in reactions if r.energy_delta < -AUDIENCE_DIR_THRESHOLD)
    total_count = len(reactions)

    if total_count > 0:
        if up_count > total_count / 2 and proposes_more_energy:
            score += 0.05
            # Short audience breakdown
            breakdown = ", ".join(
                f"{r.audience_name}:{r.energy_delta:+.2f}" for r in reactions
            )
            notes.append(
                f"audience majority ({up_count}/{total_count}) wants more energy "
                f"[{breakdown}]"
            )
        elif down_count > total_count / 2 and proposes_less_energy:
            score += 0.05
            breakdown = ", ".join(
                f"{r.audience_name}:{r.energy_delta:+.2f}" for r in reactions
            )
            notes.append(
                f"audience majority ({down_count}/{total_count}) wants less energy "
                f"[{breakdown}]"
            )

    # Venue bonuses
    if venue:
        if venue.room_size == "festival" and proposes_more_energy:
            score += VENUE_ENERGY_BONUS
            notes.append("festival setting favors energy")
        elif venue.room_size == "intimate" and proposes_less_energy:
            score += VENUE_ENERGY_BONUS
            notes.append("intimate setting favors restraint")

        effective_time = resolve_time_of_night(venue)
        if effective_time == "late" and proposes_less_energy:
            score += VENUE_ENERGY_BONUS
            notes.append("late night favors winding down")
        elif effective_time == "early" and proposes_less_energy:
            score += VENUE_EARLY_BONUS
            notes.append("early set favors restraint")

    return score, notes


def _clamp_minor(
    current: MusicParams, adopted: MusicParams
) -> tuple[MusicParams, list[str]]:
    """Clamp adopted params to minor change limits.

    Returns the clamped params and a list of what was suppressed.
    Minor turns do not change mood.
    """
    suppressions: list[str] = []

    # Mood: locked to current
    mood = current.mood
    if adopted.mood != current.mood:
        suppressions.append(f"mood change suppressed ({adopted.mood})")

    # BPM: clamp delta
    bpm_delta = adopted.bpm - current.bpm
    if abs(bpm_delta) > MINOR_MAX_BPM_DELTA:
        clamped_bpm = current.bpm + (
            MINOR_MAX_BPM_DELTA if bpm_delta > 0 else -MINOR_MAX_BPM_DELTA
        )
        suppressions.append(
            f"bpm clamped ({adopted.bpm} -> {clamped_bpm})"
        )
    else:
        clamped_bpm = adopted.bpm

    # Energy: clamp delta
    energy_delta = adopted.energy - current.energy
    if abs(energy_delta) > MINOR_MAX_ENERGY_DELTA:
        clamped_energy = round(
            current.energy
            + (MINOR_MAX_ENERGY_DELTA if energy_delta > 0 else -MINOR_MAX_ENERGY_DELTA),
            2,
        )
        suppressions.append(
            f"energy clamped ({adopted.energy:.2f} -> {clamped_energy:.2f})"
        )
    else:
        clamped_energy = adopted.energy

    clamped = MusicParams(
        mood=mood,
        bpm=max(60, min(200, clamped_bpm)),
        energy=max(0.0, min(1.0, clamped_energy)),
        texture=adopted.texture,
        focus=adopted.focus,
    )
    return clamped, suppressions


def _infer_minor_intent(
    current_energy: float, new_energy: float
) -> str:
    """Infer transition_intent from energy change direction in a minor turn."""
    if new_energy > current_energy:
        return "lift"
    if new_energy < current_energy:
        return "cool_down"
    return "hold"


def _step_section(current: Section, direction: int) -> Section:
    """Move section forward (+1) or backward (-1) within bounds."""
    idx = _SECTION_ORDER.index(current)
    new_idx = max(0, min(len(_SECTION_ORDER) - 1, idx + direction))
    return _SECTION_ORDER[new_idx]


def _resolve_major_section(
    section: SectionState,
    applied_energy: float,
    critique: Critique,
    reactions: list[Reaction],
    turn_count: int,
) -> tuple[Section, TransitionIntent, str]:
    """Determine section transition and intent for a major turn.

    Returns (new_section, new_intent, transition_reason).

    Rules:
    - Critic severity "high": step back one section (floor at intro)
    - intro: advance to build when energy >= 0.5
    - build: advance to peak when energy >= 0.7
    - peak: move to release when energy < 0.5 or sustained for N turns
    - release: rebuild to build when energy >= 0.5
    - Audience energy_delta sum > 0.2: nudges toward forward transition

    Section may stay the same if no condition triggers.
    Intent is determined after section resolution.
    """
    current = section.current_section
    turns_since_major = turn_count - section.last_major_turn
    audience_push = sum(r.energy_delta for r in reactions)

    # Critic high severity: step back (intro stays at intro)
    if critique.severity == "high":
        new_section = _step_section(current, -1)
        if new_section != current:
            intent: TransitionIntent = "cool_down"
            return new_section, intent, f"Critic flagged high severity — stepping back from {current} to {new_section}"
        # Already at intro, can't go back further
        return current, "hold", "Critic flagged high severity but already at intro — holding"

    # Section-specific transition rules
    new_section = current
    reason = "No transition triggered"

    if current == "intro":
        if applied_energy >= 0.5:
            new_section = "build"
            reason = f"Energy reached {applied_energy:.0%} — transitioning from intro to build"

    elif current == "build":
        threshold = 0.65 if audience_push > 0.2 else 0.7
        if applied_energy >= threshold:
            new_section = "peak"
            reason = f"Energy reached {applied_energy:.0%} — transitioning from build to peak"
            if audience_push > 0.2:
                reason += " (audience push lowered threshold)"

    elif current == "peak":
        if applied_energy < 0.5:
            new_section = "release"
            reason = f"Energy dropped to {applied_energy:.0%} — transitioning from peak to release"
        elif turns_since_major >= PEAK_SUSTAIN_TURNS:
            new_section = "release"
            reason = f"Peak sustained for {turns_since_major} turns — transitioning to release"

    elif current == "release":
        if applied_energy >= 0.5:
            new_section = "build"
            reason = f"Energy recovered to {applied_energy:.0%} — rebuilding from release to build"

    # Determine intent after section is resolved
    if new_section != current:
        idx_diff = _SECTION_ORDER.index(new_section) - _SECTION_ORDER.index(current)
        intent = "intensify" if idx_diff > 0 else "cool_down"
    else:
        # No section change: infer from energy
        if applied_energy >= 0.7:
            intent = "intensify"
        elif applied_energy <= 0.3:
            intent = "cool_down"
        elif critique.severity == "medium":
            intent = "lift"
        else:
            intent = "hold"

    return new_section, intent, reason


class Conductor:
    """Orchestrates a single turn of the DJ meeting.

    Collects proposals and feedback, selects one proposal based on
    adoption rules (with feedback influence), updates session state,
    and publishes SSE events. Supports minor and major turn kinds.
    """

    def __init__(
        self,
        agents: list[DJAgent],
        critic: CriticAgent,
        audiences: list[AudienceAgent],
        store: SessionStore,
        bus: EventBus,
        music: MusicBackend,
        memory: MemoryStore,
    ) -> None:
        self._agents = agents
        self._critic = critic
        self._audiences = audiences
        self._store = store
        self._bus = bus
        self._music = music
        self._memory = memory

    async def run_turn(
        self, session: SessionState, kind: ChangeKind = "major",
        max_rounds: int = 1,
        dialogue_mode: DialogueMode = "structured",
    ) -> TurnResult:
        """Execute one turn with conversational deliberation.

        dialogue_mode="structured": fixed DJ order (parallel), M6-04 behavior.
        dialogue_mode="semi_free": DJ order determined dynamically per round,
          later DJs read earlier DJs' proposals via context.

        Each round: DJs propose/revise → Critic evaluates → Audiences react.
        All messages accumulate in a shared MeetingContext.
        Decision and state update happen once after the final round.

        max_rounds=1: traditional 1-shot behavior.
        max_rounds>1: multi-round deliberation with shared context.
        """
        # 0. Setup
        user_request_text = session.last_user_request
        profile = await self._memory.get_profile()
        context = MeetingContext(current_round=1, total_rounds=max_rounds, mode=dialogue_mode)

        locale = session.locale

        agent_input = AgentInput(
            current_params=session.current_params,
            last_change=session.last_change,
            user_request=session.last_user_request,
            locale=locale,
        )
        critic_input = CriticInput(
            current_params=session.current_params,
            last_change=session.last_change,
            turn_count=session.turn_count,
            locale=locale,
        )
        audience_input = AudienceInput(
            current_params=session.current_params,
            last_change=session.last_change,
            turn_count=session.turn_count,
            venue=session.venue,
            locale=locale,
        )

        # Deliberation loop
        proposals: list[Proposal] = []
        critique: Critique | None = None
        reactions: list[Reaction] = []
        feedback_items: list[FeedbackItem] = []
        last_speaker_order: list[str] | None = None
        all_speaker_orders: list[list[str]] = []
        all_intents: list[SpeakingIntent] = []
        all_votes: list[TurnVote] = []
        prev_agent_summaries: dict[str, str] = {}
        early_stop = False
        rounds_executed = 0
        vote_result: str | None = None

        for round_num in range(1, max_rounds + 1):
            # Safety: stop if message count exceeds limit
            if len(context.messages) >= MAX_MESSAGES_PER_TURN:
                logger.warning(
                    "[deliberation] message limit reached (%d), stopping early",
                    MAX_MESSAGES_PER_TURN,
                )
                early_stop = True
                break

            context.current_round = round_num
            round_info = RoundInfo(round=round_num, total_rounds=max_rounds)
            rounds_executed = round_num

            # 0. Query speaking intents (M7.3-02)
            intents = await asyncio.gather(
                *(agent.should_speak(context, agent_input) for agent in self._agents)
            )
            all_intents = list(intents)
            speakers = [i for i in intents if i.intent == "speak"]

            # Safety: at least 1 agent must speak
            if not speakers:
                # Force the agent with highest energy distance to speak
                energy = agent_input.current_params.energy
                best = max(self._agents, key=lambda a: abs(0.5 - energy))
                forced = SpeakingIntent(agent_name=best.name, intent="speak", reason="Forced (no volunteers)")
                speakers = [forced]
                all_intents = [forced if i.agent_name == best.name else i for i in all_intents]

            speaking_names = {s.agent_name for s in speakers}
            speaking_agents = [a for a in self._agents if a.name in speaking_names]

            # 1. DJ proposals (only from agents who want to speak)
            if dialogue_mode == "semi_free":
                proposals, last_speaker_order = await self._collect_semi_free(
                    round_num, agent_input, context, critique, reactions,
                    user_request_text,
                )
            elif round_num == 1:
                proposals = list(
                    await asyncio.gather(
                        *(agent.propose(agent_input) for agent in speaking_agents)
                    )
                )
            else:
                proposals = list(
                    await asyncio.gather(
                        *(agent.revise(agent_input, context) for agent in speaking_agents)
                    )
                )

            # Add DJ messages to context (semi_free adds during collection)
            if dialogue_mode != "semi_free":
                for p in proposals:
                    context.add(
                        speaker=p.agent_name,
                        role="dj",
                        content=f"{p.summary} (perspective: {p.perspective})",
                        data=p.model_dump(),
                    )

            # 2. Critic + Audience feedback
            feedback_results = await asyncio.gather(
                self._critic.evaluate(critic_input),
                *(a.react(audience_input) for a in self._audiences),
            )
            critique = feedback_results[0]  # type: ignore[assignment]
            reactions = [
                r for r in feedback_results[1:] if isinstance(r, Reaction)
            ]

            # Add feedback to context
            assert critique is not None
            context.add(
                speaker="critic",
                role="critic",
                content=f"{critique.issue} — {critique.suggestion}",
                data=critique.model_dump(),
            )
            for r in reactions:
                context.add(
                    speaker=r.audience_name,
                    role="audience",
                    content=f"{r.reaction} (energy_delta: {r.energy_delta:+.2f})",
                    data=r.model_dump(),
                )

            # 3. Build feedback items for SSE
            feedback_items = self._build_feedback_items(critique, reactions)

            # 4. SSE: proposals + feedback for this round
            await self._bus.publish(
                SSEEvent(
                    event=EVENT_PROPOSALS,
                    data={
                        "round": round_info.round,
                        "total_rounds": round_info.total_rounds,
                        "proposals": [p.model_dump() for p in proposals],
                    },
                )
            )
            await self._bus.publish(
                SSEEvent(
                    event=EVENT_FEEDBACK,
                    data={
                        "round": round_info.round,
                        "total_rounds": round_info.total_rounds,
                        "items": [fi.model_dump() for fi in feedback_items],
                    },
                )
            )

            # Track speaker order for this round
            if last_speaker_order:
                all_speaker_orders.append(last_speaker_order)
            else:
                all_speaker_orders.append([s.agent_name for s in speakers])

            # Repetition detection: exact agent→summary match with previous round
            current_agent_summaries = {p.agent_name: p.summary for p in proposals}
            if round_num > 1 and current_agent_summaries == prev_agent_summaries:
                early_stop = True
                logger.info(
                    "[deliberation] round=%d early_stop=true (identical per-agent summaries)",
                    round_num,
                )
                break

            prev_agent_summaries = current_agent_summaries

            # 5. Voting (M7.3-03) — DJ agents only, skip round 1 (safety: always continue)
            if round_num >= 2:
                votes = list(await asyncio.gather(
                    *(agent.vote(context, agent_input) for agent in self._agents)
                ))
                all_votes = votes

                # Tally votes
                adopt_votes = [v for v in votes if v.vote == "adopt"]
                stop_votes = [v for v in votes if v.vote == "stop"]
                total = len(votes)

                if len(adopt_votes) > total / 2:
                    # Majority adopt — find the most adopted agent
                    adopt_counts = Counter(v.adopt_agent for v in adopt_votes if v.adopt_agent)
                    if adopt_counts:
                        winner = adopt_counts.most_common(1)[0]
                        vote_result = f"adopt:{winner[0]} ({winner[1]}/{total})"
                        early_stop = True
                        logger.info("[deliberation] vote consensus: %s", vote_result)
                        break
                elif len(stop_votes) > total / 2:
                    vote_result = f"stop ({len(stop_votes)}/{total})"
                    early_stop = True
                    logger.info("[deliberation] vote consensus: %s", vote_result)
                    break

            logger.info(
                "[deliberation] round=%d/%d speakers=%s order=%s",
                round_num, max_rounds,
                [s.agent_name for s in speakers],
                last_speaker_order or "parallel",
            )

        # --- Post-deliberation: Decision and state update (once) ---
        assert critique is not None
        final_round_info = RoundInfo(round=rounds_executed, total_rounds=max_rounds)

        # 5. Select the adopted proposal
        decision = self._select(session, proposals, critique, reactions, profile)

        # 6. Inherit genre_group from session (agents don't propose it)
        applied_params = decision.applied_params.model_copy(
            update={"genre_group": session.current_params.genre_group},
        )
        suppressions: list[str] = []
        if kind == "minor":
            applied_params, suppressions = _clamp_minor(
                session.current_params, decision.applied_params
            )
            decision = Decision(
                adopted_proposal=decision.adopted_proposal,
                reason=decision.reason,
                applied_params=applied_params,
                rejections=decision.rejections,
            )

        # 7. Build change summary
        change_summary = (
            f"{decision.adopted_proposal.agent_name}: "
            f"{decision.adopted_proposal.summary}"
        )
        if suppressions:
            change_summary += f" [minor: {', '.join(suppressions)}]"

        # 8. Build dialogue metadata (shared by SSE and TurnResult)
        from deckcrew.orchestrator.models import IntentSummary, VoteSummary
        intent_summaries = [
            IntentSummary(agent_name=i.agent_name, intent=i.intent, reason=i.reason)
            for i in all_intents
        ] if all_intents else None
        vote_summaries = [
            VoteSummary(agent_name=v.agent_name, vote=v.vote, adopt_agent=v.adopt_agent, reason=v.reason)
            for v in all_votes
        ] if all_votes else None

        dialogue_meta = DialogueMetadata(
            mode=dialogue_mode,
            total_messages=len(context.messages),
            rounds_executed=rounds_executed,
            early_stop=early_stop,
            speaker_orders=all_speaker_orders,
            intents=intent_summaries,
            votes=vote_summaries,
            vote_result=vote_result,
        )

        # 9. SSE: decision
        decision_data: dict[str, object] = {
            "kind": kind,
            "round": final_round_info.round,
            "total_rounds": final_round_info.total_rounds,
            "adopted": decision.adopted_proposal.agent_name,
            "reason": decision.reason,
            "applied_params": applied_params.model_dump(),
            "rejections": [r.model_dump() for r in decision.rejections],
        }
        decision_data["dialogue"] = dialogue_meta.model_dump()
        await self._bus.publish(
            SSEEvent(event=EVENT_DECISION, data=decision_data)
        )

        # 10. Update section state
        new_section = self._update_section(
            session, kind, change_summary, applied_params,
            critique, reactions,
        )

        # 11. Update session state (once, after all rounds)
        updated = session.model_copy(
            update={
                "current_params": applied_params,
                "section": new_section,
                "last_change": change_summary,
                "last_turn_kind": kind,
                "turn_count": session.turn_count + 1,
                "last_user_request": None,
            }
        )
        self._store.update(updated)

        # 12. Apply to music backend (with full context for genre/mood derivation)
        assert critique is not None
        await self._music.apply(
            updated.current_params,
            section=new_section.current_section,
            intent=new_section.transition_intent,
            time_of_night=resolve_time_of_night(session.venue) if session.venue else "peak_hours",
            event_vibe=session.venue.event_vibe if session.venue else "underground",
            critic_severity=critique.severity,
            user_request=user_request_text,
        )

        # 13. SSE: state
        await self._bus.publish(
            SSEEvent(event=EVENT_STATE, data=updated.model_dump())
        )

        # 14. Record intervention
        if user_request_text:
            await self._memory.add_intervention(
                InterventionRecord(
                    session_id=session.session_id,
                    turn=session.turn_count + 1,
                    text=user_request_text,
                    adopted_agent=decision.adopted_proposal.agent_name,
                    timestamp=datetime.now(UTC).isoformat(),
                )
            )

        # 15. Log turn summary
        prev_section = session.section.current_section
        new_section_name = new_section.current_section
        transition_str = (
            f"{prev_section}→{new_section_name}"
            if prev_section != new_section_name
            else f"{prev_section}→{new_section_name} (hold)"
        )

        logger.info(
            "[turn] kind=%s turn=%d rounds=%d/%d mode=%s section=%s adopted=%s early_stop=%s messages=%d",
            kind, updated.turn_count, rounds_executed, max_rounds,
            dialogue_mode, transition_str,
            decision.adopted_proposal.agent_name,
            early_stop, len(context.messages),
        )

        return TurnResult(
            kind=kind,
            round_info=final_round_info,
            speaker_order=last_speaker_order,
            dialogue=dialogue_meta,
            proposals=proposals,
            feedback=feedback_items,
            decision=decision,
            state=updated,
        )

    async def _collect_semi_free(
        self,
        round_num: int,
        agent_input: AgentInput,
        context: MeetingContext,
        prev_critique: Critique | None,
        prev_reactions: list[Reaction],
        user_request: str | None,
    ) -> tuple[list[Proposal], list[str]]:
        """Collect DJ proposals with dynamic speaker order.

        - First DJ: propose() (round 1) or revise() (round 2+)
        - Subsequent DJs: revise(context) — can read prior DJ's proposal
        - Order is determined by _determine_dj_order()
        """
        ordered_agents = self._determine_dj_order(
            prev_critique, prev_reactions, user_request,
            agent_input.current_params.energy,
        )
        order_names = [a.name for a in ordered_agents]

        proposals: list[Proposal] = []
        for idx, agent in enumerate(ordered_agents):
            if round_num == 1 and idx == 0:
                # First DJ in round 1: propose from scratch
                proposal = await agent.propose(agent_input)
            else:
                # All others: revise with context (can see prior speakers)
                proposal = await agent.revise(agent_input, context)

            proposals.append(proposal)
            # Add to context immediately so next DJ can read it
            context.add(
                speaker=proposal.agent_name,
                role="dj",
                content=f"{proposal.summary} (perspective: {proposal.perspective})",
                data=proposal.model_dump(),
            )

        logger.info(
            "[semi_free] round=%d order=%s",
            round_num, order_names,
        )
        return proposals, order_names

    def _determine_dj_order(
        self,
        prev_critique: Critique | None,
        prev_reactions: list[Reaction],
        user_request: str | None,
        current_energy: float,
    ) -> list[DJAgent]:
        """Determine DJ speaking order for semi-free mode.

        Priority rules:
        1. user_request present → Crowd first
        2. Audience energy_delta sum > 0.2 → Crowd first
        3. Critic severity medium+ → DJ whose energy_affinity is
           farthest from current energy goes first (most change)
        4. Default → order by distance from current energy (desc)
        """
        agents = list(self._agents)

        # Rule 1: user request → Crowd first
        if user_request:
            crowd = [a for a in agents if a.name == "crowd"]
            others = [a for a in agents if a.name != "crowd"]
            return crowd + others

        # Rule 2: audience wants more energy → Crowd first
        if prev_reactions:
            total_delta = sum(r.energy_delta for r in prev_reactions)
            if total_delta > 0.2:
                crowd = [a for a in agents if a.name == "crowd"]
                others = [a for a in agents if a.name != "crowd"]
                return crowd + others

        # Rule 3: Critic medium+ → sort by name variety (non-adopted first)
        # Rule 4: Default → sort by typical energy distance
        # Use a simple heuristic: groove=high energy, harmony=mid, crowd=varies
        _ENERGY_TENDENCY: dict[str, float] = {
            "groove": 0.7,
            "harmony": 0.5,
            "crowd": 0.5,
        }
        agents.sort(
            key=lambda a: abs(_ENERGY_TENDENCY.get(a.name, 0.5) - current_energy),
            reverse=True,
        )
        return agents

    def _update_section(
        self,
        session: SessionState,
        kind: ChangeKind,
        summary: str,
        applied_params: MusicParams,
        critique: Critique,
        reactions: list[Reaction],
    ) -> SectionState:
        """Update section state based on turn kind."""
        section = session.section

        # Add change record (cap at MAX_RECENT_CHANGES)
        record = ChangeRecord(
            turn=session.turn_count + 1,
            kind=kind,
            summary=summary,
        )
        recent = list(section.recent_changes) + [record]
        if len(recent) > MAX_RECENT_CHANGES:
            recent = recent[-MAX_RECENT_CHANGES:]

        if kind == "minor":
            # Minor: preserve section, adjust intent based on energy direction
            new_intent = _infer_minor_intent(
                session.current_params.energy, applied_params.energy
            )
            return SectionState(
                current_section=section.current_section,
                transition_intent=new_intent,  # type: ignore[arg-type]
                last_major_turn=section.last_major_turn,
                recent_changes=recent,
            )

        # Major: resolve section transition and intent
        new_section_name, new_intent, _transition_reason = _resolve_major_section(
            section,
            applied_params.energy,
            critique,
            reactions,
            session.turn_count + 1,
        )
        return SectionState(
            current_section=new_section_name,
            transition_intent=new_intent,
            last_major_turn=session.turn_count + 1,
            recent_changes=recent,
        )

    def _select(
        self,
        session: SessionState,
        proposals: list[Proposal],
        critique: Critique,
        reactions: list[Reaction],
        profile: PreferenceProfile,
    ) -> Decision:
        """Pick the best proposal, influenced by feedback and preferences."""

        if session.last_user_request:
            # User request takes priority; preferences not applied
            return self._select_with_user_request(
                proposals, critique, reactions
            )

        return self._select_by_score(
            session, proposals, critique, reactions, profile
        )

    def _select_with_user_request(
        self,
        proposals: list[Proposal],
        critique: Critique,
        reactions: list[Reaction],
    ) -> Decision:
        """User request present: Crowd's proposal is adopted."""
        crowd = next(
            (p for p in proposals if p.agent_name == "crowd"), proposals[0]
        )
        adopted = crowd

        reason_parts = [
            f"User request present — adopting {adopted.agent_name}'s "
            f"proposal to reflect audience input"
        ]
        if critique.severity in ("medium", "high"):
            reason_parts.append(f"(critic noted: {critique.issue})")

        rejections = [
            RejectionDetail(
                agent_name=p.agent_name,
                summary=p.summary,
                reason="User request prioritized Crowd's proposal",
            )
            for p in proposals
            if p.agent_name != adopted.agent_name
        ]

        return Decision(
            adopted_proposal=adopted,
            reason=" ".join(reason_parts),
            applied_params=adopted.suggested_params,
            rejections=rejections,
        )

    def _select_by_score(
        self,
        session: SessionState,
        proposals: list[Proposal],
        critique: Critique,
        reactions: list[Reaction],
        profile: PreferenceProfile,
    ) -> Decision:
        """No user request: pick by change score + feedback + repetition + preference."""
        scored: list[tuple[Proposal, float, list[str]]] = []
        for p in proposals:
            base = _compute_change_score(
                session.current_params, p.suggested_params
            )
            adjusted, notes = _apply_feedback_bonus(
                base, p.suggested_params, session.current_params,
                critique, reactions, venue=session.venue,
            )
            # Anti-repetition penalties
            penalties = detect_repetition(
                session.current_params,
                p.suggested_params,
                list(session.section.recent_changes),
                session.turn_count,
            )
            for pen in penalties:
                adjusted += pen.penalty
                notes.append(pen.reason)

            # Preference bonuses from memory
            pref_bonuses = apply_preference_bonus(profile, p.suggested_params)
            for pb in pref_bonuses:
                adjusted += pb.bonus
                notes.append(pb.reason)

            scored.append((p, adjusted, notes))

        scored.sort(key=lambda x: x[1], reverse=True)
        best, best_score, best_notes = scored[0]

        reason_parts = [
            f"Adopting {best.agent_name}'s proposal "
            f"(score: {best_score:.2f})"
        ]
        if best_notes:
            reason_parts.append("influenced by " + ", ".join(best_notes))

        rejections = [
            RejectionDetail(
                agent_name=p.agent_name,
                summary=p.summary,
                reason=f"Score {s:.2f} was lower than adopted ({best_score:.2f})",
            )
            for p, s, _ in scored[1:]
        ]

        return Decision(
            adopted_proposal=best,
            reason=" — ".join(reason_parts),
            applied_params=best.suggested_params,
            rejections=rejections,
        )

    @staticmethod
    def _build_feedback_items(
        critique: Critique, reactions: list[Reaction]
    ) -> list[FeedbackItem]:
        """Convert agent outputs to FeedbackEvent-compatible items."""
        items: list[FeedbackItem] = []

        items.append(
            FeedbackItem(
                source="critic",
                name="critic",
                content=CriticFeedbackContent(
                    issue=critique.issue,
                    severity=critique.severity,
                    suggestion=critique.suggestion,
                ).model_dump(),
            )
        )

        for r in reactions:
            items.append(
                FeedbackItem(
                    source="audience",
                    name=r.audience_name,
                    content=AudienceFeedbackContent(
                        reaction=r.reaction,
                        energy_delta=r.energy_delta,
                        reason=r.reason,
                    ).model_dump(),
                )
            )

        return items
