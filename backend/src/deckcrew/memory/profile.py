"""Preference profile update logic.

Pure functions that derive profile changes from intervention text.
No LLM or embedding — keyword-based extraction only.
"""

from __future__ import annotations

from deckcrew.memory.models import InterventionRecord, PreferenceProfile

# Energy shift per intervention (parallel move of min/max)
_ENERGY_STEP = 0.05

# --- Keyword dictionaries (minimal, extend as needed) ---

_MOOD_KEYWORDS: dict[str, list[str]] = {
    "dark": ["dark", "darker", "heavy", "heavier"],
    "bright": ["bright", "brighter", "light", "lighter"],
    "deep": ["deep", "deeper"],
    "chill": ["chill", "relaxed", "mellow"],
}

_ENERGY_UP_KEYWORDS: list[str] = [
    "energy",
    "louder",
    "harder",
    "intense",
    "pump",
    "hype",
]

_ENERGY_DOWN_KEYWORDS: list[str] = [
    "calm",
    "quiet",
    "softer",
    "chill",
    "gentle",
    "ease",
]

_FOCUS_KEYWORDS: dict[str, list[str]] = {
    "bass": ["bass"],
    "drums": ["drums", "kick", "percussion"],
    "synth": ["synth", "synthesizer"],
    "melody": ["melody", "melodic"],
    "pad": ["pad", "pads"],
}


def _extract_mood_hint(text: str) -> str | None:
    """Extract mood from intervention text. Returns last match or None."""
    lower = text.lower()
    for mood, keywords in _MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return mood
    return None


def _extract_energy_direction(text: str) -> int:
    """Extract energy direction: +1 (up), -1 (down), or 0 (neutral)."""
    lower = text.lower()
    for kw in _ENERGY_UP_KEYWORDS:
        if kw in lower:
            return 1
    for kw in _ENERGY_DOWN_KEYWORDS:
        if kw in lower:
            return -1
    return 0


def _extract_focus_hint(text: str) -> str | None:
    """Extract focus instrument from text. Returns last match or None."""
    lower = text.lower()
    for focus, keywords in _FOCUS_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return focus
    return None


def update_profile(
    current: PreferenceProfile,
    record: InterventionRecord,
) -> PreferenceProfile:
    """Update preference profile based on a new intervention.

    Rules:
    - preferred_mood: set to explicitly mentioned mood, or keep current
    - min_energy / max_energy: parallel shift ±0.05 based on energy keywords, clamp 0..1
    - preferred_focus: set to explicitly mentioned instrument, or keep current
    - intervention_count: increment
    - adopted_agent is not used for profile update in this version
    """
    mood = _extract_mood_hint(record.text) or current.preferred_mood
    direction = _extract_energy_direction(record.text)
    focus = _extract_focus_hint(record.text) or current.preferred_focus

    min_e = current.min_energy + direction * _ENERGY_STEP
    max_e = current.max_energy + direction * _ENERGY_STEP
    min_e = max(0.0, min(1.0, min_e))
    max_e = max(0.0, min(1.0, max_e))

    return PreferenceProfile(
        preferred_mood=mood,
        min_energy=round(min_e, 2),
        max_energy=round(max_e, 2),
        preferred_focus=focus,
        intervention_count=current.intervention_count + 1,
    )
