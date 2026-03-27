from typing import Literal

from pydantic import BaseModel, Field


class MusicParams(BaseModel):
    """Current music control parameters."""

    mood: str = "neutral"
    bpm: int = Field(default=120, ge=60, le=200)
    energy: float = Field(default=0.5, ge=0.0, le=1.0)
    texture: str = "layered"
    focus: str = "melody"


# --- Section state for M3 two-layer loop ---

Section = Literal["intro", "build", "peak", "release"]
TransitionIntent = Literal["hold", "lift", "intensify", "cool_down", "reset"]
ChangeKind = Literal["minor", "major"]

# Maximum number of recent changes to retain
MAX_RECENT_CHANGES = 10


class ChangeRecord(BaseModel):
    """A single recorded change from a completed turn."""

    turn: int
    kind: ChangeKind
    summary: str


class SectionState(BaseModel):
    """Tracks DJ set progression: current section, intent, and history.

    - `current_section`: where we are in the set arc (intro → build → peak → release)
    - `transition_intent`: what direction the set should move next
    - `last_major_turn`: turn_count when the last major change occurred
    - `recent_changes`: rolling window of turn records (capped at MAX_RECENT_CHANGES)
    """

    current_section: Section = "intro"
    transition_intent: TransitionIntent = "hold"
    last_major_turn: int = 0
    recent_changes: list[ChangeRecord] = Field(default_factory=list)


class SessionState(BaseModel):
    """Full session state, used as the API response schema."""

    session_id: str
    status: str = "idle"  # idle | running | stopped
    current_params: MusicParams = Field(default_factory=MusicParams)
    section: SectionState = Field(default_factory=SectionState)
    last_change: str | None = None
    last_user_request: str | None = None
    turn_count: int = 0
