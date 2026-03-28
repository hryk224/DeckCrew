"""Compose WeightedPrompts from genre, mood, and instruments.

Assembles the final prompt list for Lyria from:
1. Resolved genre (primary, highest weight)
2. Derived mood
3. Genre default instruments (adjusted by focus)
4. Optional free text from user request (supplement)
"""

from __future__ import annotations

from dataclasses import dataclass

from deckcrew.music.genres import GenreEntry


@dataclass
class PromptEntry:
    """A prompt with weight, to be converted to LyriaPrompt in params.py."""

    text: str
    weight: float = 1.0


def compose_prompts(
    genre: GenreEntry,
    mood: str,
    focus: str | None = None,
    free_text: str | None = None,
) -> list[PromptEntry]:
    """Build WeightedPrompt list for Lyria.

    - genre prompt: weight 2.0 (primary musical direction)
    - mood: weight 1.0 (emotional color)
    - instruments: weight 1.5 (timbral character)
    - free_text: weight 0.8 (user supplement, optional)
    """
    prompts: list[PromptEntry] = []

    # 1. Genre (primary)
    prompts.append(PromptEntry(text=genre.lyria_prompt, weight=2.0))

    # 2. Mood
    prompts.append(PromptEntry(text=mood, weight=1.0))

    # 3. Instruments
    instruments = list(genre.default_instruments)
    # If focus specifies an instrument not in defaults, add it
    if focus and focus not in [i.lower() for i in instruments]:
        instruments.append(focus.capitalize())
    if instruments:
        prompts.append(
            PromptEntry(text=", ".join(instruments), weight=1.5)
        )

    # 4. Free text supplement (user request that isn't a mood keyword)
    if free_text and free_text.strip():
        prompts.append(PromptEntry(text=free_text.strip(), weight=0.8))

    return prompts
