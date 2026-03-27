from typing import Literal

from pydantic import BaseModel, Field

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


# --- Critic agent schemas ---

Severity = Literal["low", "medium", "high"]


class CriticInput(BaseModel):
    """Input passed to the Critic agent for evaluation."""

    current_params: MusicParams
    last_change: str | None = None
    turn_count: int = 0


class Critique(BaseModel):
    """Critic agent's evaluation of the current session flow."""

    issue: str
    severity: Severity
    suggestion: str


# --- Audience agent schemas ---


class AudienceInput(BaseModel):
    """Input passed to the Audience agent for reaction."""

    current_params: MusicParams
    last_change: str | None = None
    turn_count: int = 0


class Reaction(BaseModel):
    """Audience agent's reaction to the current session flow."""

    audience_name: str
    reaction: str
    energy_delta: float = Field(default=0.0, ge=-1.0, le=1.0)
    reason: str
