"""Prompt construction for LLM-backed agents.

System prompts are loaded from Markdown files in agent/prompts/.
User prompts are built dynamically from session state.

Locale switching:
  Currently English only. To add another language:
  1. Create agent/prompts/<locale>/ with the same filenames
  2. Set PROMPT_LOCALE=<locale> environment variable
  3. _load_system_prompt() will read from the locale subdirectory
"""

from __future__ import annotations

import functools
from pathlib import Path

from typing import TYPE_CHECKING

from deckcrew.agent.audience_persona import AudiencePersona
from deckcrew.agent.models import AgentInput, AudienceInput, CriticInput

if TYPE_CHECKING:
    from deckcrew.orchestrator.meeting import MeetingContext

_PROMPTS_DIR = Path(__file__).parent / "prompts"


@functools.lru_cache(maxsize=16)
def load_system_prompt(name: str) -> str:
    """Load a system prompt from agent/prompts/<name>.md.

    Cached after first read. All file I/O is centralized here.
    """
    path = _PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8").strip()


# --- DJ agents ---


def build_dj_user_prompt(agent_name: str, agent_input: AgentInput) -> str:
    """Build user prompt for a DJ agent (Groove / Harmony / Crowd)."""
    p = agent_input.current_params
    parts = [
        f"Current state: mood={p.mood}, bpm={p.bpm}, energy={p.energy:.2f}, "
        f"texture={p.texture}, focus={p.focus}",
    ]
    if agent_input.last_change:
        parts.append(f"Last change: {agent_input.last_change}")
    if agent_input.user_request:
        parts.append(f"User request: {agent_input.user_request}")
    parts.append(
        f"You are {agent_name}. Propose your next direction as a JSON object."
    )
    return "\n".join(parts)


def build_dj_revise_prompt(
    agent_name: str, agent_input: AgentInput, context: MeetingContext
) -> str:
    """Build user prompt for a DJ agent revising after reading the meeting."""
    base = build_dj_user_prompt(agent_name, agent_input)
    meeting_log = context.format_log()
    return (
        f"{base}\n\n"
        f"Previous meeting discussion:\n{meeting_log}\n\n"
        f"Considering the above discussion, revise your proposal. "
        f"Respond as a JSON object."
    )


# --- Critic ---


def build_critic_user_prompt(critic_input: CriticInput) -> str:
    """Build user prompt for the Critic agent."""
    p = critic_input.current_params
    parts = [
        f"Current state: mood={p.mood}, bpm={p.bpm}, energy={p.energy:.2f}, "
        f"texture={p.texture}, focus={p.focus}",
        f"Turn count: {critic_input.turn_count}",
    ]
    if critic_input.last_change:
        parts.append(f"Last change: {critic_input.last_change}")
    parts.append("Evaluate the current flow and respond as a JSON object.")
    return "\n".join(parts)


# --- Audience ---


def _describe_persona(persona: AudiencePersona) -> str:
    """Convert persona attributes to natural language."""
    sensitivity = (
        "You crave change and novelty."
        if persona.change_sensitivity >= 0.6
        else "You prefer consistency and gradual shifts."
    )
    return (
        f"You are {persona.label}, a listener who prefers "
        f"energy around {persona.preferred_energy:.0%} "
        f"and tempo around {persona.preferred_bpm} BPM. "
        f"{sensitivity}"
    )


def build_audience_user_prompt(
    audience_input: AudienceInput, persona: AudiencePersona
) -> str:
    """Build user prompt for an Audience agent."""
    p = audience_input.current_params
    parts = [
        _describe_persona(persona),
        "",
        f"Current state: mood={p.mood}, bpm={p.bpm}, energy={p.energy:.2f}, "
        f"texture={p.texture}, focus={p.focus}",
        f"Turn count: {audience_input.turn_count}",
    ]
    if audience_input.last_change:
        parts.append(f"Last change: {audience_input.last_change}")

    # Venue context
    if audience_input.venue:
        v = audience_input.venue
        parts.append(
            f"Venue: {v.room_size} room, crowd density {v.crowd_density:.0%}, "
            f"{v.time_of_night.replace('_', ' ')}, {v.event_vibe} vibe"
        )

    parts.append("React to the current music as a JSON object.")
    return "\n".join(parts)
