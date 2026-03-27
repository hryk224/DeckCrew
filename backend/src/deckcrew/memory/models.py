"""Memory layer models.

Tracks user intervention history and preference profiles across
sessions. Separate from session state (state/), which holds
the current turn's transient data.

Memory scope: In the current implementation, memory is scoped to
the local process context (no user ID). When authentication is
introduced, memory should be keyed per user.
"""

from pydantic import BaseModel, Field


class InterventionRecord(BaseModel):
    """A single user intervention recorded for memory."""

    session_id: str
    turn: int
    text: str
    adopted_agent: str
    timestamp: str  # ISO 8601


class PreferenceProfile(BaseModel):
    """Aggregated user preferences derived from intervention history.

    Updated incrementally as interventions accumulate.
    Initial values represent no preference (neutral defaults).
    """

    preferred_mood: str | None = None
    min_energy: float = 0.3
    max_energy: float = 0.7
    preferred_focus: str | None = None
    intervention_count: int = 0


class MemoryState(BaseModel):
    """Complete memory context.

    Scope: local process context (single user, no auth).
    When user IDs are introduced, this becomes per-user.
    """

    interventions: list[InterventionRecord] = Field(default_factory=list)
    profile: PreferenceProfile = Field(default_factory=PreferenceProfile)
