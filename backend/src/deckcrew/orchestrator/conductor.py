import asyncio

from deckcrew.agent.base import AudienceAgent, CriticAgent, DJAgent
from deckcrew.agent.models import (
    AgentInput,
    AudienceInput,
    CriticInput,
    Critique,
    Proposal,
    Reaction,
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
from deckcrew.music.base import MusicBackend
from deckcrew.orchestrator.models import Decision, RejectionDetail, TurnResult
from deckcrew.orchestrator.repetition import detect_repetition
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
from deckcrew.state.store import SessionStore

# Bonus applied to change score when feedback indicates stagnation
_CRITIC_ENERGY_BONUS = 0.15
_AUDIENCE_ENERGY_BONUS = 0.1

# Minor turn constraints
_MINOR_MAX_BPM_DELTA = 4
_MINOR_MAX_ENERGY_DELTA = 0.1

# Major section transition thresholds
_SECTION_ORDER: list[Section] = ["intro", "build", "peak", "release"]
_PEAK_SUSTAIN_TURNS = 3  # max turns at peak before release


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
) -> tuple[float, list[str]]:
    """Adjust score based on feedback. Returns (adjusted_score, bonus_notes).

    - Critic severity medium or high: bonus for proposals that raise energy.
      (In M2, medium and high are treated equally.)
    - Audience energy_delta sum > 0: bonus for proposals that raise energy.
      (Sum across all audiences to support future multi-audience.)
    """
    score = base_score
    notes: list[str] = []

    proposes_more_energy = proposed.energy > current.energy

    # Critic bonus
    if critique.severity in ("medium", "high") and proposes_more_energy:
        score += _CRITIC_ENERGY_BONUS
        notes.append(f"critic flagged: {critique.issue}")

    # Audience bonus (sum of energy_delta across all audiences)
    total_delta = sum(r.energy_delta for r in reactions)
    if total_delta > 0 and proposes_more_energy:
        score += _AUDIENCE_ENERGY_BONUS
        notes.append("audience wanted more energy")

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
    if abs(bpm_delta) > _MINOR_MAX_BPM_DELTA:
        clamped_bpm = current.bpm + (
            _MINOR_MAX_BPM_DELTA if bpm_delta > 0 else -_MINOR_MAX_BPM_DELTA
        )
        suppressions.append(
            f"bpm clamped ({adopted.bpm} -> {clamped_bpm})"
        )
    else:
        clamped_bpm = adopted.bpm

    # Energy: clamp delta
    energy_delta = adopted.energy - current.energy
    if abs(energy_delta) > _MINOR_MAX_ENERGY_DELTA:
        clamped_energy = round(
            current.energy
            + (_MINOR_MAX_ENERGY_DELTA if energy_delta > 0 else -_MINOR_MAX_ENERGY_DELTA),
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
        elif turns_since_major >= _PEAK_SUSTAIN_TURNS:
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
    ) -> None:
        self._agents = agents
        self._critic = critic
        self._audiences = audiences
        self._store = store
        self._bus = bus
        self._music = music

    async def run_turn(
        self, session: SessionState, kind: ChangeKind = "major"
    ) -> TurnResult:
        """Execute one turn: collect, decide, update, broadcast.

        kind="minor" clamps parameter changes and preserves section.
        kind="major" allows full changes (default, M1/M2 behavior).
        """
        # 1. Build inputs
        agent_input = AgentInput(
            current_params=session.current_params,
            last_change=session.last_change,
            user_request=session.last_user_request,
        )
        critic_input = CriticInput(
            current_params=session.current_params,
            last_change=session.last_change,
            turn_count=session.turn_count,
        )
        audience_input = AudienceInput(
            current_params=session.current_params,
            last_change=session.last_change,
            turn_count=session.turn_count,
        )

        # 2. Collect proposals in parallel
        proposals: list[Proposal] = list(
            await asyncio.gather(
                *(agent.propose(agent_input) for agent in self._agents)
            )
        )

        # 3. Collect feedback in parallel
        feedback_results = await asyncio.gather(
            self._critic.evaluate(critic_input),
            *(a.react(audience_input) for a in self._audiences),
        )
        critique: Critique = feedback_results[0]  # type: ignore[assignment]
        reactions: list[Reaction] = [
            r for r in feedback_results[1:] if isinstance(r, Reaction)
        ]

        # 4. Build feedback items for SSE
        feedback_items = self._build_feedback_items(critique, reactions)

        # 5. SSE: proposals
        await self._bus.publish(
            SSEEvent(
                event=EVENT_PROPOSALS,
                data={"proposals": [p.model_dump() for p in proposals]},
            )
        )

        # 6. SSE: feedback
        await self._bus.publish(
            SSEEvent(
                event=EVENT_FEEDBACK,
                data={"items": [fi.model_dump() for fi in feedback_items]},
            )
        )

        # 7. Select the adopted proposal
        decision = self._select(session, proposals, critique, reactions)

        # 8. Apply minor clamping if needed
        applied_params = decision.applied_params
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

        # 9. Build change summary
        change_summary = (
            f"{decision.adopted_proposal.agent_name}: "
            f"{decision.adopted_proposal.summary}"
        )
        if suppressions:
            change_summary += f" [minor: {', '.join(suppressions)}]"

        # 10. SSE: decision
        await self._bus.publish(
            SSEEvent(
                event=EVENT_DECISION,
                data={
                    "adopted": decision.adopted_proposal.agent_name,
                    "reason": decision.reason,
                    "applied_params": applied_params.model_dump(),
                    "rejections": [r.model_dump() for r in decision.rejections],
                },
            )
        )

        # 11. Update section state
        new_section = self._update_section(
            session, kind, change_summary, applied_params,
            critique, reactions,
        )

        # 12. Update session state
        updated = session.model_copy(
            update={
                "current_params": applied_params,
                "section": new_section,
                "last_change": change_summary,
                "turn_count": session.turn_count + 1,
                "last_user_request": None,
            }
        )
        self._store.update(updated)

        # 13. Apply to music backend
        await self._music.apply(updated.current_params)

        # 14. SSE: state
        await self._bus.publish(
            SSEEvent(event=EVENT_STATE, data=updated.model_dump())
        )

        return TurnResult(
            kind=kind,
            proposals=proposals,
            feedback=feedback_items,
            decision=decision,
            state=updated,
        )

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
    ) -> Decision:
        """Pick the best proposal, influenced by feedback."""

        if session.last_user_request:
            return self._select_with_user_request(
                proposals, critique, reactions
            )

        return self._select_by_score(
            session, proposals, critique, reactions
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
    ) -> Decision:
        """No user request: pick by change score + feedback bonus - repetition penalty."""
        scored: list[tuple[Proposal, float, list[str]]] = []
        for p in proposals:
            base = _compute_change_score(
                session.current_params, p.suggested_params
            )
            adjusted, notes = _apply_feedback_bonus(
                base, p.suggested_params, session.current_params,
                critique, reactions,
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
