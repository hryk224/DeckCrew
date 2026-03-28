"""Agent factory.

Creates mock or LLM-backed agents based on whether an LLM provider
is configured. When LLM is unavailable or fails, agents fall back
to mock implementations internally.
"""

from deckcrew.agent.audience_persona import DEFAULT_PERSONAS
from deckcrew.agent.base import AudienceAgent, CriticAgent, DJAgent
from deckcrew.agent.llm_agents import LLMAudience, LLMCritic, LLMDJAgent
from deckcrew.agent.mock import MockCrowd, MockGroove, MockHarmony
from deckcrew.agent.mock_audience import MockPersonaAudience
from deckcrew.agent.mock_critic import MockCritic
from deckcrew.llm.registry import llm_provider

_MOCK_DJS: dict[str, type[MockGroove] | type[MockHarmony] | type[MockCrowd]] = {
    "groove": MockGroove,
    "harmony": MockHarmony,
    "crowd": MockCrowd,
}


def create_agents() -> list[DJAgent]:
    """Create the DJ agent set.

    Uses LLM agents with mock fallback when provider is configured.
    Falls back to pure mock when provider is None.
    """
    if llm_provider:
        return [
            LLMDJAgent(name, llm_provider, mock_cls())
            for name, mock_cls in _MOCK_DJS.items()
        ]
    return [MockGroove(), MockHarmony(), MockCrowd()]


def create_critic() -> CriticAgent:
    """Create the Critic agent."""
    if llm_provider:
        return LLMCritic(llm_provider, MockCritic())
    return MockCritic()


def create_audiences() -> list[AudienceAgent]:
    """Create the Audience agent set (one per persona)."""
    if llm_provider:
        return [
            LLMAudience(persona, llm_provider, MockPersonaAudience(persona))
            for persona in DEFAULT_PERSONAS
        ]
    return [MockPersonaAudience(persona) for persona in DEFAULT_PERSONAS]
