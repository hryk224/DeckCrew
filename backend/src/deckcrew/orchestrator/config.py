"""Orchestrator tuning parameters.

Centralized configuration for Conductor, section transitions,
repetition penalties, and minor turn constraints. Values that
are likely to need adjustment can be overridden via environment
variables.
"""

import os

# --- Feedback bonuses (fixed, rarely adjusted) ---
CRITIC_ENERGY_BONUS = 0.15
AUDIENCE_ENERGY_BONUS = 0.1
VENUE_ENERGY_BONUS = 0.05
VENUE_EARLY_BONUS = 0.03
AUDIENCE_DIR_THRESHOLD = 0.05

# --- Minor turn constraints (env-overridable) ---
MINOR_MAX_BPM_DELTA = int(os.environ.get("MINOR_MAX_BPM_DELTA", "4"))
MINOR_MAX_ENERGY_DELTA = float(os.environ.get("MINOR_MAX_ENERGY_DELTA", "0.1"))

# --- Section transitions (env-overridable) ---
PEAK_SUSTAIN_TURNS = int(os.environ.get("PEAK_SUSTAIN_TURNS", "3"))

# --- Repetition penalties (env-overridable thresholds, fixed amounts) ---
REPETITION_MIN_TURNS = int(os.environ.get("REPETITION_MIN_TURNS", "3"))
FOCUS_REPETITION_PENALTY = -0.2
BPM_STAGNATION_PENALTY = -0.15
ENERGY_STAGNATION_PENALTY = -0.1
LOW_ENERGY_DELTA = 0.05

# --- Deliberation ---
MAX_DELIBERATION_ROUNDS = int(os.environ.get("MAX_DELIBERATION_ROUNDS", "2"))


def get_all_config() -> dict[str, float | int]:
    """Return all tuning parameters as a flat dict (for debug API)."""
    return {
        "critic_energy_bonus": CRITIC_ENERGY_BONUS,
        "audience_energy_bonus": AUDIENCE_ENERGY_BONUS,
        "venue_energy_bonus": VENUE_ENERGY_BONUS,
        "venue_early_bonus": VENUE_EARLY_BONUS,
        "audience_dir_threshold": AUDIENCE_DIR_THRESHOLD,
        "minor_max_bpm_delta": MINOR_MAX_BPM_DELTA,
        "minor_max_energy_delta": MINOR_MAX_ENERGY_DELTA,
        "peak_sustain_turns": PEAK_SUSTAIN_TURNS,
        "repetition_min_turns": REPETITION_MIN_TURNS,
        "focus_repetition_penalty": FOCUS_REPETITION_PENALTY,
        "bpm_stagnation_penalty": BPM_STAGNATION_PENALTY,
        "energy_stagnation_penalty": ENERGY_STAGNATION_PENALTY,
        "low_energy_delta": LOW_ENERGY_DELTA,
        "max_deliberation_rounds": MAX_DELIBERATION_ROUNDS,
    }
