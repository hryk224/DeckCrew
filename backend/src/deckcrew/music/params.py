"""Convert MusicParams to Lyria-compatible prompts and config."""

from __future__ import annotations

from dataclasses import dataclass, field

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
    params: MusicParams, previous_bpm: int | None = None
) -> LyriaCommand:
    """Convert MusicParams into a LyriaCommand.

    Mapping rules:
    - mood  → prompt text ("mood: {mood}")
    - bpm   → config.bpm (integer, 60-200)
    - energy → config.density (0.0-1.0)
    - texture → prompt text ("texture: {texture}")
    - focus → prompt text with higher weight + mute flags for emphasis

    BPM changes require a context reset (Lyria constraint).
    """
    prompts: list[LyriaPrompt] = []

    # Mood prompt
    prompts.append(LyriaPrompt(text=f"mood: {params.mood}", weight=1.0))

    # Texture prompt
    prompts.append(LyriaPrompt(text=f"texture: {params.texture}", weight=0.8))

    # Focus: featured instrument gets higher weight
    prompts.append(LyriaPrompt(text=f"focus on {params.focus}", weight=1.2))

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
        # De-emphasize rhythm to let melodic elements stand out
        config.mute_drums = True

    # Detect BPM change requiring context reset
    needs_reset = previous_bpm is not None and previous_bpm != params.bpm

    return LyriaCommand(
        prompts=prompts,
        config=config,
        needs_reset=needs_reset,
    )
