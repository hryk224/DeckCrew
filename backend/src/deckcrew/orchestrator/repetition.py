"""Anti-repetition rules for the Conductor's adoption scoring.

Detects when proposals maintain the current state without change
and applies score penalties to encourage variation. This is a
control rule layer, separate from Critic's evaluation:
- Critic: evaluates "is the current state problematic?"
- Repetition: adjusts "should we adopt a proposal that keeps things the same?"

Rules use current_params vs proposed_params only. No summary
string parsing. recent_changes is accepted for future use but
not parsed in this initial version.
"""

from __future__ import annotations

from dataclasses import dataclass

from deckcrew.orchestrator.config import (
    BPM_STAGNATION_PENALTY,
    ENERGY_STAGNATION_PENALTY,
    FOCUS_REPETITION_PENALTY,
    LOW_ENERGY_DELTA,
    REPETITION_MIN_TURNS,
)
from deckcrew.state.models import ChangeRecord, MusicParams


@dataclass
class RepetitionPenalty:
    """A single penalty applied to a proposal's score."""

    penalty: float
    reason: str


def detect_repetition(
    current: MusicParams,
    proposed: MusicParams,
    recent_changes: list[ChangeRecord],  # reserved for future use
    turn_count: int,
) -> list[RepetitionPenalty]:
    """Check if a proposal maintains the status quo too closely.

    Returns a list of penalties (may be empty). Each penalty has a
    negative value and a short reason string.

    Only applies after REPETITION_MIN_TURNS turns to let the session
    develop before penalizing.
    """
    if turn_count < REPETITION_MIN_TURNS:
        return []

    penalties: list[RepetitionPenalty] = []

    # Same focus as current
    if proposed.focus == current.focus:
        penalties.append(
            RepetitionPenalty(
                penalty=FOCUS_REPETITION_PENALTY,
                reason="same focus repeated",
            )
        )

    # Same BPM as current
    if proposed.bpm == current.bpm:
        penalties.append(
            RepetitionPenalty(
                penalty=BPM_STAGNATION_PENALTY,
                reason="bpm unchanged",
            )
        )

    # Energy barely changing
    if abs(proposed.energy - current.energy) < LOW_ENERGY_DELTA:
        penalties.append(
            RepetitionPenalty(
                penalty=ENERGY_STAGNATION_PENALTY,
                reason="energy stagnant",
            )
        )

    return penalties
