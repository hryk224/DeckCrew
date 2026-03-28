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
from deckcrew.venue.time_resolver import resolve_time_of_night

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

    # Time of night adjustment (resolved from timezone if set)
    effective_time = resolve_time_of_night(venue)
    if effective_time == "peak_hours":
        energy += 0.05
    elif effective_time == "early":
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
        loc = audience_input.locale

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

        # Persona-specific voice lines (locale-aware)
        raw_lines = _PERSONA_LINES.get(p.name, _DEFAULT_LINES)
        lines = {k: v.get(loc, v["en"]) for k, v in raw_lines.items()}

        def _reason(key: str, **kwargs: object) -> str:
            tpl = _REASONS[key]
            return tpl.get(loc, tpl["en"]).format(**kwargs)

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
                reason=_reason("bored", label=p.label),
            )

        # Energy too low for this persona
        if energy_gap > 0.25:
            delta = min(energy_gap * 0.6 * density_mult, 0.4)
            return Reaction(
                audience_name=self.name,
                reaction=lines["low_energy"],
                energy_delta=round(delta, 2),
                reason=_reason("low_energy", label=p.label, energy=f"{pref_energy:.0%}"),
            )

        # Energy too high for this persona
        if energy_gap < -0.25:
            delta = max(energy_gap * 0.6 * density_mult, -0.4)
            return Reaction(
                audience_name=self.name,
                reaction=lines["high_energy"],
                energy_delta=round(delta, 2),
                reason=_reason("high_energy", label=p.label, energy=f"{pref_energy:.0%}"),
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
                reason=_reason("bpm_off", label=p.label, pref_bpm=pref_bpm, bpm=params.bpm, gap=bpm_gap),
            )

        # Comfortable zone
        return Reaction(
            audience_name=self.name,
            reaction=lines["happy"],
            energy_delta=0.0,
            reason=_reason("happy", label=p.label),
        )


# Persona-specific voice lines per locale
_PERSONA_LINES: dict[str, dict[str, dict[str, str]]] = {
    "clubber": {
        "bored": {"en": "Yo, switch it up! This floor's going dead.", "ja": "おい、なんか変えてくれ！フロア冷めてきてるぞ！"},
        "low_energy": {"en": "C'mon, turn it up! We came here to dance!", "ja": "もっと上げてくれよ！踊りに来たんだから！"},
        "high_energy": {"en": "Whoa, even I need a breather... ease off a bit.", "ja": "うわ、さすがにちょっと休憩…少し落としてくれ。"},
        "too_fast": {"en": "The tempo's wild, I can't keep up!", "ja": "テンポ速すぎ、ついていけない！"},
        "too_slow": {"en": "Pick up the pace, let's get moving!", "ja": "もっとペース上げて、動きたいんだよ！"},
        "happy": {"en": "Yeah, this is it! Keep it rolling!", "ja": "最高！このまま回し続けてくれ！"},
    },
    "chiller": {
        "bored": {"en": "Hmm, I wouldn't mind a little change of scenery.", "ja": "うーん、ちょっと景色が変わってもいいかな。"},
        "low_energy": {"en": "Could use a touch more warmth, actually.", "ja": "もう少し温かみがあるといいんだけど。"},
        "high_energy": {"en": "Whoa, way too much... I need some space to breathe.", "ja": "うわ、ちょっと激しすぎ…息つく隙間がほしい。"},
        "too_fast": {"en": "This is rushing... can we slow it down?", "ja": "急ぎすぎてない？もう少しゆっくりでいいよ。"},
        "too_slow": {"en": "The pace is fine, but a little more movement would be nice.", "ja": "ペースは悪くないけど、もう少し動きがほしいかな。"},
        "happy": {"en": "This is perfect. Just floating along.", "ja": "これ最高。ずっとこのまま漂っていたい。"},
    },
    "explorer": {
        "bored": {"en": "We've been here before. Show me something I haven't heard.", "ja": "この展開、前にも聴いたよ。まだ聴いたことない音を聴かせて。"},
        "low_energy": {"en": "Interesting direction, but it needs more push.", "ja": "面白い方向だけど、もうひと押し欲しい。"},
        "high_energy": {"en": "The energy's great, but let's try something unexpected.", "ja": "エネルギーはいいけど、もっと予想外の展開が欲しい。"},
        "too_fast": {"en": "Fast is fine, but it's getting predictable at this tempo.", "ja": "速いのはいいけど、このテンポだとワンパターンになりそう。"},
        "too_slow": {"en": "Slow can work if it goes somewhere new.", "ja": "遅くても新しいところに行くならアリ。"},
        "happy": {"en": "Ooh, I like where this is going. Keep exploring.", "ja": "おっ、この展開いいね。もっと攻めて。"},
    },
}

_DEFAULT_LINES: dict[str, dict[str, str]] = {
    "bored": {"en": "Getting bored, want something new.", "ja": "飽きてきた、何か新しいの頼む。"},
    "low_energy": {"en": "Needs more energy!", "ja": "もっとエネルギーが欲しい！"},
    "high_energy": {"en": "Too intense, dial it back.", "ja": "激しすぎ、少し落として。"},
    "too_fast": {"en": "Tempo feels too fast.", "ja": "テンポが速すぎる。"},
    "too_slow": {"en": "Tempo feels too slow.", "ja": "テンポが遅すぎる。"},
    "happy": {"en": "Enjoying this.", "ja": "いい感じ。"},
}

# Reason templates per locale
_REASONS: dict[str, dict[str, str]] = {
    "bored": {"en": "{label} craves change but nothing shifted recently", "ja": "{label} は変化を求めているが、最近動きがない"},
    "low_energy": {"en": "{label} prefers energy around {energy}, currently too low", "ja": "{label} の好みは energy {energy} 付近、今は低すぎる"},
    "high_energy": {"en": "{label} prefers energy around {energy}, currently too high", "ja": "{label} の好みは energy {energy} 付近、今は高すぎる"},
    "bpm_off": {"en": "{label} prefers around {pref_bpm} BPM, current {bpm} is {gap} off", "ja": "{label} の好みは {pref_bpm} BPM 付近、現在 {bpm} で {gap} 離れている"},
    "happy": {"en": "{label} is comfortable with the current vibe", "ja": "{label} は今の雰囲気に満足している"},
}

