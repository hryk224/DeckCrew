from deckcrew.agent.base import CriticAgent, DJAgent
from deckcrew.agent.mock import MockCrowd, MockGroove, MockHarmony
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
