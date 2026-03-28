from typing import Protocol

from deckcrew.agent.models import (
    AgentInput,
    AudienceInput,
    CriticInput,
    Critique,
    Proposal,
    Reaction,
)


class DJAgent(Protocol):
    """Interface for DJ agents.

    Implement this protocol to create a new agent backend (mock, LLM, etc.).
    """

    @property
    def name(self) -> str: ...

    async def propose(self, agent_input: AgentInput) -> Proposal: ...

    async def revise(self, agent_input: AgentInput, feedback: str) -> Proposal:
        """Revise a proposal based on feedback from other agents.

        Default: delegates to propose() (ignores feedback).
        M6-04 will add feedback-aware implementations.
        """
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
