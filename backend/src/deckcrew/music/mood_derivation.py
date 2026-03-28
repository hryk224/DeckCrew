"""Mood derivation from context.

Mood is not user-selected. It is derived from:
1. genre default mood (base)
2. section + transition_intent (overlay)
3. time_of_night (shift)
4. critic severity (mild correction — NOT the primary driver)
5. user_request mood keywords (override if present)

Returns a short mood descriptor suitable for Lyria prompts.
"""

from __future__ import annotations

from deckcrew.agent.models import Severity
from deckcrew.music.genres import GenreEntry
from deckcrew.state.models import Section, TransitionIntent
from deckcrew.venue.models import TimeOfNight

# Section-based mood overlays
_SECTION_MOOD: dict[tuple[Section, TransitionIntent], str] = {
    ("intro", "hold"): "Warm",
    ("intro", "lift"): "Building",
    ("build", "lift"): "Rising",
    ("build", "intensify"): "Driving",
    ("peak", "intensify"): "Euphoric",
    ("peak", "hold"): "Energetic",
    ("release", "cool_down"): "Mellow",
    ("release", "hold"): "Reflective",
}

# Time-of-night mood shifts
_TIME_SHIFT: dict[TimeOfNight, str | None] = {
    "early": "Warm",
    "peak_hours": None,  # no shift, keep genre/section mood
    "late": "Mellow",
}

# User request mood keywords
_USER_MOOD_KEYWORDS: dict[str, str] = {
    "dark": "Dark",
    "bright": "Bright",
    "chill": "Chill",
    "energy": "Energetic",
    "heavy": "Heavy",
    "mellow": "Mellow",
    "dreamy": "Dreamy",
    "aggressive": "Aggressive",
    "happy": "Upbeat",
    "sad": "Emotional",
}


def derive_mood(
    genre: GenreEntry,
    section: Section,
    intent: TransitionIntent,
    time_of_night: TimeOfNight,
    critic_severity: Severity | None = None,
    user_request: str | None = None,
) -> str:
    """Derive a mood descriptor from the current context.

    Priority: user_request keywords > section overlay > time shift > genre default.
    Critic severity is a mild correction, not the primary driver.
    """
    # 1. Check user request for explicit mood keywords
    if user_request:
        lower = user_request.lower()
        for keyword, user_mood in _USER_MOOD_KEYWORDS.items():
            if keyword in lower:
                return user_mood

    # 2. Section + intent overlay
    result: str | None = _SECTION_MOOD.get((section, intent))

    # 3. Time-of-night shift (only if section didn't produce a mood)
    if result is None:
        result = _TIME_SHIFT.get(time_of_night)

    # 4. Fall back to genre default
    mood: str = result if result is not None else genre.default_mood

    # 5. Critic mild correction: if stagnation flagged, nudge toward change
    if critic_severity in ("medium", "high") and mood in ("Warm", "Chill", "Mellow"):
        mood = "Driving"

    return mood
