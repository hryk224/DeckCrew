import asyncio

from deckcrew.agent.base import DJAgent
from deckcrew.agent.models import AgentInput, Proposal
from deckcrew.api.event_bus import EventBus
from deckcrew.api.events import (
    EVENT_DECISION,
    EVENT_PROPOSALS,
    EVENT_STATE,
    SSEEvent,
)
from deckcrew.orchestrator.models import Decision, TurnResult
from deckcrew.state.models import MusicParams, SessionState
from deckcrew.state.store import SessionStore


def _compute_change_score(current: MusicParams, proposed: MusicParams) -> float:
    """Score how much a proposal differs from the current state.

    Higher score = more change. Used to pick the most impactful proposal
    when no user request is present (to avoid stagnation).
    """
    score = 0.0
    score += abs(current.bpm - proposed.bpm) / 200.0
    score += abs(current.energy - proposed.energy)
    if current.focus != proposed.focus:
        score += 0.3
    if current.texture != proposed.texture:
        score += 0.2
    return score


class Conductor:
    """Orchestrates a single turn of the DJ meeting.

    Collects proposals from all agents, selects one based on adoption
    rules, updates session state, and publishes SSE events.
    """

    def __init__(
        self,
        agents: list[DJAgent],
        store: SessionStore,
        bus: EventBus,
    ) -> None:
        self._agents = agents
        self._store = store
        self._bus = bus

    async def run_turn(self, session: SessionState) -> TurnResult:
        """Execute one turn: collect, decide, update, broadcast."""
        # 1. Build agent input
        agent_input = AgentInput(
            current_params=session.current_params,
            last_change=session.last_change,
            user_request=session.last_user_request,
        )

        # 2. Collect proposals in parallel
        proposals: list[Proposal] = list(
            await asyncio.gather(
                *(agent.propose(agent_input) for agent in self._agents)
            )
        )

        # 3. Publish proposals via SSE
        await self._bus.publish(
            SSEEvent(
                event=EVENT_PROPOSALS,
                data={"proposals": [p.model_dump() for p in proposals]},
            )
        )

        # 4. Select the adopted proposal
        decision = self._select(session, proposals)

        # 5. Publish decision via SSE
        await self._bus.publish(
            SSEEvent(
                event=EVENT_DECISION,
                data={
                    "adopted": decision.adopted_proposal.agent_name,
                    "reason": decision.reason,
                    "applied_params": decision.applied_params.model_dump(),
                },
            )
        )

        # 6. Update session state
        updated = session.model_copy(
            update={
                "current_params": decision.applied_params,
                "last_change": (
                    f"{decision.adopted_proposal.agent_name}: "
                    f"{decision.adopted_proposal.summary}"
                ),
                "turn_count": session.turn_count + 1,
                "last_user_request": None,  # consumed
            }
        )
        self._store.update(updated)

        # 7. Publish updated state via SSE
        await self._bus.publish(
            SSEEvent(event=EVENT_STATE, data=updated.model_dump())
        )

        return TurnResult(
            proposals=proposals,
            decision=decision,
            state=updated,
        )

    def _select(
        self, session: SessionState, proposals: list[Proposal]
    ) -> Decision:
        """Pick the best proposal.

        Rules:
        - If user request exists, adopt Crowd's proposal (Crowd reflects
          user intent).
        - Otherwise, adopt the proposal with the largest change score
          to avoid stagnation.
        """
        if session.last_user_request:
            # Prefer Crowd when user has spoken
            crowd = next(
                (p for p in proposals if p.agent_name == "crowd"), proposals[0]
            )
            return Decision(
                adopted_proposal=crowd,
                reason=(
                    f"User request present — adopting {crowd.agent_name}'s "
                    f"proposal to reflect audience input"
                ),
                applied_params=crowd.suggested_params,
            )

        # No user request: pick highest change score
        scored = [
            (p, _compute_change_score(session.current_params, p.suggested_params))
            for p in proposals
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        best, best_score = scored[0]

        return Decision(
            adopted_proposal=best,
            reason=(
                f"No user request — adopting {best.agent_name}'s proposal "
                f"for maximum impact (change score: {best_score:.2f})"
            ),
            applied_params=best.suggested_params,
        )
