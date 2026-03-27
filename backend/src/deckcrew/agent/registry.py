from deckcrew.agent.base import DJAgent
from deckcrew.agent.mock import MockCrowd, MockGroove, MockHarmony


def create_agents() -> list[DJAgent]:
    """Create the default set of DJ agents.

    Replace mock implementations with LLM-backed agents here
    when ready (e.g. swap MockGroove for LLMGroove).
    """
    return [MockGroove(), MockHarmony(), MockCrowd()]
