"""Mock Audience agents with persona-based reactions.

Each persona reacts differently to the same session state,
producing distinct energy_delta and reaction text based on
their preferred energy, BPM, and change sensitivity.

When venue context is provided, persona preferences are adjusted
to reflect the environment (room size, density, time, vibe).
"""

from __future__ import annotations

from dataclasses import dataclass

from deckcrew.agent.audience_persona import AudiencePersona
from deckcrew.agent.models import AudienceInput, Reaction
from deckcrew.venue.models import VenueContext

# Crowd density amplification range: 1.0 (empty) to 1.3 (packed)
_MAX_DENSITY_MULTIPLIER = 1.3


@dataclass
class _AdjustedPrefs:
    """Persona preferences after venue adjustment."""

    preferred_energy: float
    preferred_bpm: int
    change_sensitivity: float
    density_multiplier: float


def _adjust_persona_for_venue(
    persona: AudiencePersona, venue: VenueContext
) -> _AdjustedPrefs:
    """Pure function: adjust persona preferences based on venue context.

    - room_size: festival raises energy tolerance, intimate lowers it
    - time_of_night: peak_hours raises energy preference, early lowers it
    - event_vibe: experimental boosts Explorer's change_sensitivity,
      mainstream boosts Clubber's energy preference
    - crowd_density: amplifies energy_delta (1.0 to 1.3)
    """
    energy = persona.preferred_energy
    bpm = persona.preferred_bpm
    sensitivity = persona.change_sensitivity

    # Room size adjustment
    if venue.room_size == "festival":
        energy += 0.1
    elif venue.room_size == "intimate":
        energy -= 0.05

    # Time of night adjustment
    if venue.time_of_night == "peak_hours":
        energy += 0.05
    elif venue.time_of_night == "early":
        energy -= 0.05

    # Event vibe adjustment (persona-specific effects)
    if venue.event_vibe == "experimental" and persona.change_sensitivity >= 0.6:
        sensitivity = min(sensitivity + 0.15, 1.0)
    elif venue.event_vibe == "mainstream" and persona.preferred_energy >= 0.7:
        energy += 0.05

    # Clamp
    energy = max(0.0, min(1.0, energy))
    sensitivity = max(0.0, min(1.0, sensitivity))

    # Density multiplier: linear from 1.0 (density=0) to 1.3 (density=1)
    density_mult = 1.0 + venue.crowd_density * (_MAX_DENSITY_MULTIPLIER - 1.0)

    return _AdjustedPrefs(
        preferred_energy=energy,
        preferred_bpm=bpm,
        change_sensitivity=sensitivity,
        density_multiplier=density_mult,
    )


class MockPersonaAudience:
    """Mock Audience driven by a persona's preferences.

    When venue is provided, preferences are adjusted before evaluation.
    When venue is None, raw persona preferences are used (M1-M4 compat).
    """

    def __init__(self, persona: AudiencePersona) -> None:
        self._persona = persona

    @property
    def name(self) -> str:
        return self._persona.name

    async def react(self, audience_input: AudienceInput) -> Reaction:
        params = audience_input.current_params
        p = self._persona

        # Adjust preferences for venue, or use raw persona values
        if audience_input.venue:
            adj = _adjust_persona_for_venue(p, audience_input.venue)
            pref_energy = adj.preferred_energy
            pref_bpm = adj.preferred_bpm
            sensitivity = adj.change_sensitivity
            density_mult = adj.density_multiplier
        else:
            pref_energy = p.preferred_energy
            pref_bpm = p.preferred_bpm
            sensitivity = p.change_sensitivity
            density_mult = 1.0

        energy_gap = pref_energy - params.energy
        bpm_gap = abs(params.bpm - pref_bpm)

        # Persona-specific voice lines
        lines = _PERSONA_LINES.get(p.name, _DEFAULT_LINES)

        # High change sensitivity + stale session = boredom
        if (
            sensitivity >= 0.6
            and audience_input.turn_count >= 3
            and audience_input.last_change is None
        ):
            return Reaction(
                audience_name=self.name,
                reaction=lines["bored"],
                energy_delta=round(0.2 * density_mult, 2),
                reason=(
                    f"{p.label} craves change but nothing shifted recently"
                ),
            )

        # Energy too low for this persona
        if energy_gap > 0.25:
            delta = min(energy_gap * 0.6 * density_mult, 0.4)
            return Reaction(
                audience_name=self.name,
                reaction=lines["low_energy"],
                energy_delta=round(delta, 2),
                reason=(
                    f"{p.label} prefers energy around "
                    f"{pref_energy:.0%}, currently too low"
                ),
            )

        # Energy too high for this persona
        if energy_gap < -0.25:
            delta = max(energy_gap * 0.6 * density_mult, -0.4)
            return Reaction(
                audience_name=self.name,
                reaction=lines["high_energy"],
                energy_delta=round(delta, 2),
                reason=(
                    f"{p.label} prefers energy around "
                    f"{pref_energy:.0%}, currently too high"
                ),
            )

        # BPM far from preference
        if bpm_gap > 30:
            direction = "fast" if params.bpm > pref_bpm else "slow"
            return Reaction(
                audience_name=self.name,
                reaction=lines[f"too_{direction}"],
                energy_delta=round(
                    (-0.1 if direction == "fast" else 0.1) * density_mult, 2
                ),
                reason=(
                    f"{p.label} prefers around {pref_bpm} BPM, "
                    f"current {params.bpm} is {bpm_gap} off"
                ),
            )

        # Comfortable zone
        return Reaction(
            audience_name=self.name,
            reaction=lines["happy"],
            energy_delta=0.0,
            reason=f"{p.label} is comfortable with the current vibe",
        )


# Persona-specific voice lines for conversational tone
_PERSONA_LINES: dict[str, dict[str, str]] = {
    "clubber": {
        "bored": "Yo, switch it up! This floor's going dead.",
        "low_energy": "C'mon, turn it up! We came here to dance!",
        "high_energy": "Whoa, even I need a breather... ease off a bit.",
        "too_fast": "The tempo's wild, I can't keep up!",
        "too_slow": "Pick up the pace, let's get moving!",
        "happy": "Yeah, this is it! Keep it rolling!",
    },
    "chiller": {
        "bored": "Hmm, I wouldn't mind a little change of scenery.",
        "low_energy": "Could use a touch more warmth, actually.",
        "high_energy": "Whoa, way too much... I need some space to breathe.",
        "too_fast": "This is rushing... can we slow it down?",
        "too_slow": "The pace is fine, but a little more movement would be nice.",
        "happy": "This is perfect. Just floating along.",
    },
    "explorer": {
        "bored": "We've been here before. Show me something I haven't heard.",
        "low_energy": "Interesting direction, but it needs more push.",
        "high_energy": "The energy's great, but let's try something unexpected.",
        "too_fast": "Fast is fine, but it's getting predictable at this tempo.",
        "too_slow": "Slow can work if it goes somewhere new.",
        "happy": "Ooh, I like where this is going. Keep exploring.",
    },
}

_DEFAULT_LINES: dict[str, str] = {
    "bored": "Getting bored, want something new.",
    "low_energy": "Needs more energy!",
    "high_energy": "Too intense, dial it back.",
    "too_fast": "Tempo feels too fast.",
    "too_slow": "Tempo feels too slow.",
    "happy": "Enjoying this.",
}

