from pydantic import BaseModel

from deckcrew.state.models import MusicParams


class AgentInput(BaseModel):
    """Input passed to each DJ agent for proposal generation."""

    current_params: MusicParams
    last_change: str | None = None
    user_request: str | None = None


class Proposal(BaseModel):
    """A single DJ agent's proposal for the next music direction."""

    agent_name: str
    summary: str
    perspective: str
    suggested_params: MusicParams
