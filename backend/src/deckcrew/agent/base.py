from typing import Protocol

from deckcrew.agent.models import AgentInput, Proposal


class DJAgent(Protocol):
    """Interface for DJ agents.

    Implement this protocol to create a new agent backend (mock, LLM, etc.).
    """

    @property
    def name(self) -> str: ...

    async def propose(self, agent_input: AgentInput) -> Proposal: ...
