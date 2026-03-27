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
from deckcrew.state.models import MusicParams, SessionState
from deckcrew.state.store import SessionStore

# Bonus applied to change score when feedback indicates stagnation
_CRITIC_ENERGY_BONUS = 0.15
_AUDIENCE_ENERGY_BONUS = 0.1


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


class Conductor:
    """Orchestrates a single turn of the DJ meeting.

    Collects proposals and feedback, selects one proposal based on
    adoption rules (with feedback influence), updates session state,
    and publishes SSE events.
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

    async def run_turn(self, session: SessionState) -> TurnResult:
        """Execute one turn: collect, decide, update, broadcast."""
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
        decision = self._select(
            session, proposals, critique, reactions
        )

        # 8. SSE: decision
        await self._bus.publish(
            SSEEvent(
                event=EVENT_DECISION,
                data={
                    "adopted": decision.adopted_proposal.agent_name,
                    "reason": decision.reason,
                    "applied_params": decision.applied_params.model_dump(),
                    "rejections": [r.model_dump() for r in decision.rejections],
                },
            )
        )

        # 9. Update session state
        updated = session.model_copy(
            update={
                "current_params": decision.applied_params,
                "last_change": (
                    f"{decision.adopted_proposal.agent_name}: "
                    f"{decision.adopted_proposal.summary}"
                ),
                "turn_count": session.turn_count + 1,
                "last_user_request": None,
            }
        )
        self._store.update(updated)

        # 10. Apply to music backend
        await self._music.apply(updated.current_params)

        # 11. SSE: state
        await self._bus.publish(
            SSEEvent(event=EVENT_STATE, data=updated.model_dump())
        )

        return TurnResult(
            proposals=proposals,
            feedback=feedback_items,
            decision=decision,
            state=updated,
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

        # Build reason with feedback context
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
        """No user request: pick by change score + feedback bonus."""
        scored: list[tuple[Proposal, float, list[str]]] = []
        for p in proposals:
            base = _compute_change_score(
                session.current_params, p.suggested_params
            )
            adjusted, notes = _apply_feedback_bonus(
                base, p.suggested_params, session.current_params,
                critique, reactions,
            )
            scored.append((p, adjusted, notes))

        scored.sort(key=lambda x: x[1], reverse=True)
        best, best_score, best_notes = scored[0]

        # Build reason with feedback influence
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
