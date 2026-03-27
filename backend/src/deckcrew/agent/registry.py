from deckcrew.agent.audience_persona import DEFAULT_PERSONAS
from deckcrew.agent.base import AudienceAgent, CriticAgent, DJAgent
from deckcrew.agent.mock import MockCrowd, MockGroove, MockHarmony
from deckcrew.agent.mock_audience import MockPersonaAudience
from deckcrew.agent.mock_critic import MockCritic


def create_agents() -> list[DJAgent]:
    """Create the default set of DJ agents.

    Replace mock implementations with LLM-backed agents here
    when ready (e.g. swap MockGroove for LLMGroove).
    """
    return [MockGroove(), MockHarmony(), MockCrowd()]


def create_critic() -> CriticAgent:
    """Create the Critic agent.

    Replace MockCritic with an LLM-backed implementation when ready.
    """
    return MockCritic()


def create_audiences() -> list[AudienceAgent]:
    """Create the default set of Audience agents.

    Returns one agent per persona (clubber, chiller, explorer).
    Replace MockPersonaAudience with LLM-backed implementations when ready.
    """
    return [MockPersonaAudience(persona) for persona in DEFAULT_PERSONAS]
