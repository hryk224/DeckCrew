from pydantic import BaseModel, Field


class MusicParams(BaseModel):
    """Current music control parameters."""

    mood: str = "neutral"
    bpm: int = Field(default=120, ge=60, le=200)
    energy: float = Field(default=0.5, ge=0.0, le=1.0)
    texture: str = "layered"
    focus: str = "melody"


class SessionState(BaseModel):
    """Full session state, used as the API response schema."""

    session_id: str
    status: str = "idle"  # idle | running | stopped
    current_params: MusicParams = Field(default_factory=MusicParams)
    last_change: str | None = None
    last_user_request: str | None = None
    turn_count: int = 0
