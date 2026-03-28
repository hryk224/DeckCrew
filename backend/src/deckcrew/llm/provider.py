"""LLM provider abstraction.

Defines the interface for calling LLMs and a provider implementation
that works with OpenAI-compatible API endpoints (Gemini, OpenAI,
Ollama, etc.). Agent-specific prompts are NOT defined here.

This module handles:
- Sending system + user prompts
- Receiving structured JSON output (json_schema with prompt fallback)
- Parsing into Pydantic models
- Timeout, retry, and error handling

The json_schema fallback exists because some providers (e.g. Ollama,
older API versions) don't support response_format with json_schema.
When detected, the provider falls back to prompt-based JSON instruction.
"""

from __future__ import annotations

import json
import logging
from typing import Protocol, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Defaults
_DEFAULT_TIMEOUT = 10.0
_MAX_RETRIES = 1


class LLMProvider(Protocol):
    """Abstract interface for LLM calls.

    Sends a system prompt and user prompt, returns a parsed
    Pydantic model instance. Implementations handle structured
    output, parsing, and retries internally.
    """

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        response_type: type[T],
    ) -> T:
        """Call the LLM and return a parsed response.

        Generic over T: the return type matches response_type.
        """
        ...


class OpenAICompatProvider:
    """OpenAI-compatible API provider.

    Works with OpenAI, Gemini (via OpenAI compat endpoint),
    Ollama, and other OpenAI-compatible servers.

    Tries structured output (response_format=json_schema) first.
    Falls back to prompt-based JSON instruction if the API does
    not support json_schema format.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._model = model
        self._timeout = timeout
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        response_type: type[T],
    ) -> T:
        """Send prompts and parse structured JSON response."""
        for attempt in range(_MAX_RETRIES + 1):
            try:
                return await self._try_structured(
                    system_prompt, user_prompt, response_type
                )
            except _StructuredOutputNotSupported:
                logger.info("[llm] json_schema not supported, falling back to prompt-based JSON")
                return await self._try_prompt_based(
                    system_prompt, user_prompt, response_type
                )
            except Exception:
                if attempt < _MAX_RETRIES:
                    logger.warning("[llm] Attempt %d failed, retrying", attempt + 1)
                    continue
                raise

        # Unreachable, but satisfies type checker
        msg = "LLM call failed after retries"
        raise RuntimeError(msg)

    async def _try_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_type: type[T],
    ) -> T:
        """Attempt structured output via response_format=json_schema."""
        schema = response_type.model_json_schema()
        try:
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_type.__name__,
                        "schema": schema,
                    },
                },
                timeout=self._timeout,
            )
        except Exception as e:
            # Some APIs return 400/422 for unsupported response_format
            err_str = str(e).lower()
            if "response_format" in err_str or "json_schema" in err_str:
                raise _StructuredOutputNotSupported from e
            raise
        content = resp.choices[0].message.content or ""
        return response_type.model_validate_json(content)

    async def _try_prompt_based(
        self,
        system_prompt: str,
        user_prompt: str,
        response_type: type[T],
    ) -> T:
        """Fallback: instruct JSON output via prompt text."""
        schema = response_type.model_json_schema()
        json_instruction = (
            f"\n\nRespond with ONLY a JSON object matching this schema:\n"
            f"{json.dumps(schema, indent=2)}\n"
            f"No markdown, no explanation, just the JSON."
        )
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt + json_instruction},
                {"role": "user", "content": user_prompt},
            ],
            timeout=self._timeout,
        )
        content = resp.choices[0].message.content or ""
        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        return response_type.model_validate_json(content)


class _StructuredOutputNotSupported(Exception):
    """Raised when the API does not support json_schema response_format."""
