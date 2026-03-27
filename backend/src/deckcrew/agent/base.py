from typing import Protocol

from deckcrew.agent.models import AgentInput, CriticInput, Critique, Proposal


class DJAgent(Protocol):
    """Interface for DJ agents.

    Implement this protocol to create a new agent backend (mock, LLM, etc.).
    """

    @property
    def name(self) -> str: ...

    async def propose(self, agent_input: AgentInput) -> Proposal: ...


class CriticAgent(Protocol):
    """Interface for critic agents.

    Evaluates the current session flow and returns a critique,
    separate from DJ proposals.
    """

    @property
    def name(self) -> str: ...

    async def evaluate(self, critic_input: CriticInput) -> Critique: ...
