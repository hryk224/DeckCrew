"""LLM provider factory.

Creates the LLM provider based on environment variables.
Returns None when no API key is available (agents stay on mock).

Primary path (recommended):
  GOOGLE_API_KEY is set → uses Gemini via OpenAI-compatible endpoint.
  No extra config needed; model defaults to gemini-2.5-flash.

Advanced override:
  LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_NAME override the primary
  path for custom providers (OpenAI, Ollama, etc.).
"""

import os

from deckcrew.llm.provider import LLMProvider, OpenAICompatProvider

_GEMINI_COMPAT_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
_GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"


def create_llm_provider() -> LLMProvider | None:
    """Create an LLM provider if configured, else return None.

    Priority:
    1. LLM_API_KEY + LLM_MODEL_NAME → custom provider (advanced)
    2. GOOGLE_API_KEY → Gemini via compat endpoint (recommended)
    3. Neither → None (mock agents)
    """
    # Advanced override
    llm_key = os.environ.get("LLM_API_KEY", "")
    llm_model = os.environ.get("LLM_MODEL_NAME", "")
    if llm_key and llm_model:
        base_url = os.environ.get("LLM_BASE_URL") or None
        return OpenAICompatProvider(
            api_key=llm_key,
            model=llm_model,
            base_url=base_url,
        )

    # Primary path: Google API key → Gemini
    google_key = os.environ.get("GOOGLE_API_KEY", "")
    if google_key:
        return OpenAICompatProvider(
            api_key=google_key,
            model=_GEMINI_DEFAULT_MODEL,
            base_url=_GEMINI_COMPAT_URL,
        )

    return None


# Singleton: None means "use mock agents"
llm_provider: LLMProvider | None = create_llm_provider()
