"""Venue context model.

Represents the virtual event space and its characteristics.
Separate from session state (transient) and memory (user-level).
Venue is set at session start and is generally stable during a
session, but not immutable — future features may allow mid-session
venue transitions.
"""

from typing import Literal

from pydantic import BaseModel, Field

RoomSize = Literal["intimate", "club", "festival"]
TimeOfNight = Literal["early", "peak_hours", "late"]
EventVibe = Literal["underground", "mainstream", "experimental"]


class VenueContext(BaseModel):
    """Virtual event space configuration.

    Influences Audience reactions and Conductor decisions by
    providing environmental context (room size, density, timing,
    atmosphere).
    """

    room_size: RoomSize = "club"
    crowd_density: float = Field(default=0.7, ge=0.0, le=1.0)
    time_of_night: TimeOfNight = "peak_hours"
    event_vibe: EventVibe = "underground"
    timezone: str | None = None  # e.g. "Asia/Tokyo". None = use preset time_of_night
