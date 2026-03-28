from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

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

if TYPE_CHECKING:
    from deckcrew.orchestrator.meeting import MeetingContext


class DJAgent(Protocol):
    """Interface for DJ agents.

    Implement this protocol to create a new agent backend (mock, LLM, etc.).
    """

    @property
    def name(self) -> str: ...

    async def propose(self, agent_input: AgentInput) -> Proposal: ...

    async def revise(
        self, agent_input: AgentInput, context: MeetingContext
    ) -> Proposal:
        """Revise a proposal considering the shared meeting context."""
        ...

    async def should_speak(
        self, context: MeetingContext, agent_input: AgentInput
    ) -> SpeakingIntent:
        """Declare intent to speak or pass in the current round."""
        ...

    async def vote(
        self, context: MeetingContext, agent_input: AgentInput
    ) -> TurnVote:
        """Vote on whether to continue deliberation or adopt a proposal."""
        ...


class CriticAgent(Protocol):
    """Interface for critic agents.

    Evaluates the current session flow and returns a critique,
    separate from DJ proposals.
    """

    @property
    def name(self) -> str: ...

    async def evaluate(self, critic_input: CriticInput) -> Critique: ...


class AudienceAgent(Protocol):
    """Interface for audience agents.

    Returns a listener's reaction to the current session flow.
    Separate from DJ proposals (what to do next) and Critic
    evaluations (what's wrong). Audience reflects reception,
    mood, and energy demand.
    """

    @property
    def name(self) -> str: ...

    async def react(self, audience_input: AudienceInput) -> Reaction: ...
