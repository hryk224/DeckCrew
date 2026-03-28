"""Time-of-night resolution from venue timezone.

Resolves the current local time into a detailed time phase,
then maps it to the existing TimeOfNight type for backward
compatibility with Audience/Conductor code.

Detailed phases (internal):
  early_evening  (18:00-20:59) - doors open, warmup
  late_evening   (21:00-22:59) - building energy
  peak_early     (23:00-00:59) - peak begins
  peak_late      (01:00-02:59) - peak continues
  late           (03:00-04:59) - after hours
  closing        (05:00-05:59) - last sets
  early_morning  (06:00-09:59) - after-party / cleanup
  late_morning   (10:00-13:59) - daytime events (festival)
  daytime        (14:00-17:59) - daytime events

Mapped to existing TimeOfNight:
  early       <- early_evening, late_evening, early_morning, late_morning, daytime
  peak_hours  <- peak_early, peak_late
  late        <- late, closing
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from deckcrew.venue.models import TimeOfNight, VenueContext

DetailedTimePhase = Literal[
    "early_evening",
    "late_evening",
    "peak_early",
    "peak_late",
    "late",
    "closing",
    "early_morning",
    "late_morning",
    "daytime",
]

# Hour ranges for detailed phases
_PHASE_TABLE: list[tuple[int, int, DetailedTimePhase]] = [
    (18, 20, "early_evening"),
    (21, 22, "late_evening"),
    (23, 23, "peak_early"),
    (0, 0, "peak_early"),
    (1, 2, "peak_late"),
    (3, 4, "late"),
    (5, 5, "closing"),
    (6, 9, "early_morning"),
    (10, 13, "late_morning"),
    (14, 17, "daytime"),
]

# Mapping from detailed phase to existing TimeOfNight
_PHASE_TO_TIME_OF_NIGHT: dict[DetailedTimePhase, TimeOfNight] = {
    "early_evening": "early",
    "late_evening": "early",
    "peak_early": "peak_hours",
    "peak_late": "peak_hours",
    "late": "late",
    "closing": "late",
    "early_morning": "early",
    "late_morning": "early",
    "daytime": "early",
}


def _hour_to_detailed_phase(hour: int) -> DetailedTimePhase:
    """Map an hour (0-23) to a detailed time phase."""
    for start, end, phase in _PHASE_TABLE:
        if start <= hour <= end:
            return phase
    return "daytime"


def resolve_detailed_phase(venue: VenueContext) -> DetailedTimePhase | None:
    """Get detailed time phase from venue timezone.

    Returns None if timezone is not set or invalid (use preset instead).
    """
    if venue.timezone is None:
        return None
    try:
        local_now = datetime.now(ZoneInfo(venue.timezone))
    except (KeyError, Exception):
        # Invalid timezone or missing tzdata — fall back to preset
        return None
    return _hour_to_detailed_phase(local_now.hour)


def resolve_time_of_night(venue: VenueContext) -> TimeOfNight:
    """Resolve effective time_of_night for the venue.

    If timezone is set, derives from current local time.
    If timezone is None, returns the preset value.
    """
    phase = resolve_detailed_phase(venue)
    if phase is not None:
        return _PHASE_TO_TIME_OF_NIGHT[phase]
    return venue.time_of_night
