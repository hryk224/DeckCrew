"""Convert MusicParams to Lyria-compatible prompts and config.

Uses genre resolution and prompt composition to build WeightedPrompts.
Falls back to simple prompt construction if genre_group is not found.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from deckcrew.music.genres import GROUPS_BY_ID, HOUSE_PARTY, resolve_genre
from deckcrew.music.mood_derivation import derive_mood
from deckcrew.music.prompt_composer import compose_prompts
from deckcrew.state.models import MusicParams

# Focus values that map to specific Lyria mute flags
_RHYTHM_FOCUS = {"drums", "bass", "percussion"}


@dataclass
class LyriaPrompt:
    """A single weighted prompt for Lyria."""

    text: str
    weight: float = 1.0


@dataclass
class LyriaConfig:
    """Lyria MusicGenerationConfig parameters."""

    bpm: int = 120
    density: float | None = None
    brightness: float | None = None
    mute_bass: bool = False
    mute_drums: bool = False
    only_bass_and_drums: bool = False


@dataclass
class LyriaCommand:
    """Complete command to send to Lyria: prompts + config."""

    prompts: list[LyriaPrompt] = field(default_factory=list)
    config: LyriaConfig = field(default_factory=LyriaConfig)
    needs_reset: bool = False


def build_command(
    params: MusicParams,
    previous_bpm: int | None = None,
    section: str = "intro",
    intent: str = "hold",
    time_of_night: str = "peak_hours",
    event_vibe: str = "underground",
    critic_severity: str | None = None,
    user_request: str | None = None,
) -> LyriaCommand:
    """Convert MusicParams into a LyriaCommand.

    Uses genre group resolution and mood derivation to compose prompts.
    BPM changes require a context reset (Lyria constraint).
    """
    # Resolve genre from group
    group = GROUPS_BY_ID.get(params.genre_group, HOUSE_PARTY)
    genre = resolve_genre(
        group,
        energy=params.energy,
        time_of_night=time_of_night,  # type: ignore[arg-type]
        section=section,  # type: ignore[arg-type]
        event_vibe=event_vibe,  # type: ignore[arg-type]
    )

    # Derive mood from context
    mood = derive_mood(
        genre=genre,
        section=section,  # type: ignore[arg-type]
        intent=intent,  # type: ignore[arg-type]
        time_of_night=time_of_night,  # type: ignore[arg-type]
        critic_severity=critic_severity,  # type: ignore[arg-type]
        user_request=user_request,
    )

    # Compose weighted prompts
    prompts_raw = compose_prompts(
        genre=genre,
        mood=mood,
        focus=params.focus,
        free_text=user_request,
    )
    prompts = [LyriaPrompt(text=p.text, weight=p.weight) for p in prompts_raw]

    # Config
    config = LyriaConfig(
        bpm=params.bpm,
        density=params.energy,
        mute_bass=False,
        mute_drums=False,
        only_bass_and_drums=False,
    )

    # Focus-based mute adjustments
    if params.focus in _RHYTHM_FOCUS:
        config.only_bass_and_drums = True
    elif params.focus in {"synth", "melody", "pad"}:
        config.mute_drums = True

    # Detect BPM change requiring context reset
    needs_reset = previous_bpm is not None and previous_bpm != params.bpm

    return LyriaCommand(
        prompts=prompts,
        config=config,
        needs_reset=needs_reset,
    )
