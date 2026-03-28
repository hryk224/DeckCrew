"""LLM provider factory.

Creates the appropriate LLM provider based on environment variables.
Returns None when LLM_API_KEY is not set (agents stay on mock).

Environment variables:
- LLM_API_KEY: API key for OpenAI-compatible endpoint
- LLM_BASE_URL: Optional base URL (for Gemini compat, Ollama, etc.)
- LLM_MODEL_NAME: Model identifier (e.g. gemini-2.5-flash, gpt-4o-mini)
"""

import os

from deckcrew.llm.provider import LLMProvider, OpenAICompatProvider


def create_llm_provider() -> LLMProvider | None:
    """Create an LLM provider if configured, else return None.

    When None, agents should fall back to mock implementations.
    """
    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key:
        return None

    model = os.environ.get("LLM_MODEL_NAME", "")
    if not model:
        return None

    base_url = os.environ.get("LLM_BASE_URL") or None

    return OpenAICompatProvider(
        api_key=api_key,
        model=model,
        base_url=base_url,
    )


# Singleton: None means "use mock agents"
llm_provider: LLMProvider | None = create_llm_provider()
