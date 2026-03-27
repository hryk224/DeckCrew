"""Mock Audience agents with persona-based reactions.

Each persona reacts differently to the same session state,
producing distinct energy_delta and reaction text based on
their preferred energy, BPM, and change sensitivity.
"""

from deckcrew.agent.audience_persona import AudiencePersona
from deckcrew.agent.models import AudienceInput, Reaction


class MockPersonaAudience:
    """Mock Audience driven by a persona's preferences.

    Reaction rules per persona attribute:
    - Energy gap: difference between current and preferred energy
      drives energy_delta direction and magnitude.
    - BPM gap: large deviation from preferred BPM triggers discomfort.
    - Change sensitivity: high sensitivity personas react negatively
      when nothing has changed recently (turn_count > 0, no last_change).
    """

    def __init__(self, persona: AudiencePersona) -> None:
        self._persona = persona

    @property
    def name(self) -> str:
        return self._persona.name

    async def react(self, audience_input: AudienceInput) -> Reaction:
        params = audience_input.current_params
        p = self._persona

        energy_gap = p.preferred_energy - params.energy
        bpm_gap = abs(params.bpm - p.preferred_bpm)

        # High change sensitivity + stale session = boredom
        if (
            p.change_sensitivity >= 0.6
            and audience_input.turn_count >= 3
            and audience_input.last_change is None
        ):
            return Reaction(
                audience_name=self.name,
                reaction="Getting bored, want something new",
                energy_delta=0.2,
                reason=(
                    f"{p.label} craves change but nothing shifted recently"
                ),
            )

        # Energy too low for this persona
        if energy_gap > 0.25:
            return Reaction(
                audience_name=self.name,
                reaction="Needs more energy!",
                energy_delta=min(energy_gap * 0.6, 0.4),
                reason=(
                    f"{p.label} prefers energy around "
                    f"{p.preferred_energy:.0%}, currently too low"
                ),
            )

        # Energy too high for this persona
        if energy_gap < -0.25:
            return Reaction(
                audience_name=self.name,
                reaction="Too intense, dial it back",
                energy_delta=max(energy_gap * 0.6, -0.4),
                reason=(
                    f"{p.label} prefers energy around "
                    f"{p.preferred_energy:.0%}, currently too high"
                ),
            )

        # BPM far from preference
        if bpm_gap > 30:
            direction = "fast" if params.bpm > p.preferred_bpm else "slow"
            return Reaction(
                audience_name=self.name,
                reaction=f"Tempo feels too {direction}",
                energy_delta=-0.1 if direction == "fast" else 0.1,
                reason=(
                    f"{p.label} prefers around {p.preferred_bpm} BPM, "
                    f"current {params.bpm} is {bpm_gap} off"
                ),
            )

        # Comfortable zone
        return Reaction(
            audience_name=self.name,
            reaction="Enjoying this",
            energy_delta=0.0,
            reason=f"{p.label} is comfortable with the current vibe",
        )
