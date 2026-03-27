"""Preference-based scoring adjustments.

Pure functions that compare a proposal against the user's
preference profile and return bonus/notes for the Conductor.
"""

from __future__ import annotations

from dataclasses import dataclass

from deckcrew.memory.models import PreferenceProfile
from deckcrew.state.models import MusicParams

_MOOD_BONUS = 0.1
_FOCUS_BONUS = 0.1
_ENERGY_RANGE_BONUS = 0.05


@dataclass
class PreferenceBonus:
    bonus: float
    reason: str


def apply_preference_bonus(
    profile: PreferenceProfile,
    proposed: MusicParams,
) -> list[PreferenceBonus]:
    """Score adjustments based on user preference profile.

    Returns a list of bonuses (may be empty). Only applies when
    intervention_count > 0 (i.e. preferences have been observed).

    Rules:
    - preferred_mood match: +0.1
    - preferred_focus match: +0.1
    - energy within min..max range: +0.05
    - None preferences are skipped (no bonus)
    """
    if profile.intervention_count == 0:
        return []

    bonuses: list[PreferenceBonus] = []

    if (
        profile.preferred_mood is not None
        and proposed.mood == profile.preferred_mood
    ):
        bonuses.append(
            PreferenceBonus(bonus=_MOOD_BONUS, reason="matches preferred mood")
        )

    if (
        profile.preferred_focus is not None
        and proposed.focus == profile.preferred_focus
    ):
        bonuses.append(
            PreferenceBonus(
                bonus=_FOCUS_BONUS, reason="matches preferred focus"
            )
        )

    if profile.min_energy <= proposed.energy <= profile.max_energy:
        bonuses.append(
            PreferenceBonus(
                bonus=_ENERGY_RANGE_BONUS,
                reason="within preferred energy range",
            )
        )

    return bonuses
