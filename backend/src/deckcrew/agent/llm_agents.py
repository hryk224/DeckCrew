"""LLM-backed agent implementations.

Each agent wraps LLMProvider.complete() with the appropriate
prompt templates and a mock fallback for resilience.
"""

from __future__ import annotations

import logging

from deckcrew.agent.audience_persona import AudiencePersona
from deckcrew.agent.base import AudienceAgent, CriticAgent, DJAgent
from deckcrew.agent.models import (
    AgentInput,
    AudienceInput,
    CriticInput,
    Critique,
    Proposal,
    Reaction,
    SpeakingIntent,
    TurnVote,
)
from deckcrew.agent.prompt_builder import (
    build_audience_user_prompt,
    build_critic_user_prompt,
    build_dj_revise_prompt,
    build_dj_user_prompt,
    load_system_prompt,
)
from deckcrew.orchestrator.meeting import MeetingContext
from deckcrew.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class LLMDJAgent:
    """LLM-backed DJ agent with mock fallback."""

    def __init__(
        self,
        agent_name: str,
        provider: LLMProvider,
        mock_fallback: DJAgent,
    ) -> None:
        self._name = agent_name
        self._provider = provider
        self._mock = mock_fallback
        self._last_proposal: Proposal | None = None

    @property
    def name(self) -> str:
        return self._name

    async def propose(self, agent_input: AgentInput) -> Proposal:
        system = load_system_prompt(self._name, agent_input.locale)
        user = build_dj_user_prompt(self._name, agent_input)
        try:
            result = await self._provider.complete(
                system, user, Proposal
            )
            if result.agent_name != self._name:
                result = result.model_copy(update={"agent_name": self._name})
        except Exception:
            logger.warning("[llm] %s.propose() failed, using mock", self._name)
            result = await self._mock.propose(agent_input)
        self._last_proposal = result
        return result

    async def revise(
        self, agent_input: AgentInput, context: MeetingContext
    ) -> Proposal:
        """Revise proposal considering the shared meeting context.

        On failure, returns the Round 1 proposal (not a re-generation).
        """
        system = load_system_prompt(self._name, agent_input.locale)
        user = build_dj_revise_prompt(self._name, agent_input, context)
        try:
            result = await self._provider.complete(
                system, user, Proposal
            )
            if result.agent_name != self._name:
                result = result.model_copy(update={"agent_name": self._name})
            self._last_proposal = result
            return result
        except Exception:
            logger.warning("[llm] %s.revise() failed, reusing round 1 proposal", self._name)
            if self._last_proposal is not None:
                return self._last_proposal
            return await self._mock.propose(agent_input)

    async def should_speak(
        self, context: MeetingContext, agent_input: AgentInput
    ) -> SpeakingIntent:
        # Delegate to mock for now; LLM-based intent is a future enhancement
        return await self._mock.should_speak(context, agent_input)

    async def vote(
        self, context: MeetingContext, agent_input: AgentInput
    ) -> TurnVote:
        # Delegate to mock for now; LLM-based voting is a future enhancement
        return await self._mock.vote(context, agent_input)


class LLMCritic:
    """LLM-backed Critic agent with mock fallback."""

    def __init__(self, provider: LLMProvider, mock_fallback: CriticAgent) -> None:
        self._provider = provider
        self._mock = mock_fallback

    @property
    def name(self) -> str:
        return "critic"

    async def evaluate(self, critic_input: CriticInput) -> Critique:
        system = load_system_prompt("critic", critic_input.locale)
        user = build_critic_user_prompt(critic_input)
        try:
            return await self._provider.complete(
                system, user, Critique
            )
        except Exception:
            logger.warning("[llm] critic.evaluate() failed, using mock")
            return await self._mock.evaluate(critic_input)


class LLMAudience:
    """LLM-backed Audience agent with mock fallback."""

    def __init__(
        self,
        persona: AudiencePersona,
        provider: LLMProvider,
        mock_fallback: AudienceAgent,
    ) -> None:
        self._persona = persona
        self._provider = provider
        self._mock = mock_fallback

    @property
    def name(self) -> str:
        return self._persona.name

    async def react(self, audience_input: AudienceInput) -> Reaction:
        system = load_system_prompt("audience", audience_input.locale)
        user = build_audience_user_prompt(audience_input, self._persona)
        try:
            result = await self._provider.complete(
                system, user, Reaction
            )
            # Ensure audience_name matches persona
            if result.audience_name != self._persona.name:
                result = result.model_copy(
                    update={"audience_name": self._persona.name}
                )
            return result
        except Exception:
            logger.warning(
                "[llm] %s.react() failed, using mock", self._persona.name
            )
            return await self._mock.react(audience_input)
