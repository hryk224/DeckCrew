from __future__ import annotations

from typing import TYPE_CHECKING

from deckcrew.agent.models import AgentInput, Proposal, SpeakingIntent, TurnVote
from deckcrew.state.models import MusicParams

if TYPE_CHECKING:
    from deckcrew.orchestrator.meeting import MeetingContext

# Localized utterance text
_TEXT: dict[str, dict[str, str]] = {
    "groove_summary": {
        "en": "Push the kick harder, raise tempo slightly for drive",
        "ja": "キックをもっと前に出して、テンポ少し上げて攻めよう",
    },
    "harmony_summary": {
        "en": "Widen the chord voicing, add floating pad layers",
        "ja": "コードの広がりを出して、浮遊感のあるパッドを重ねたい",
    },
    "crowd_request": {
        "en": "Audience wants: {request}",
        "ja": "フロアの声: {request}",
    },
    "crowd_default": {
        "en": "Current direction feels right, maintain the vibe",
        "ja": "今の方向性はいい感じ、このまま維持しよう",
    },
}


def _t(key: str, locale: str, **kwargs: str) -> str:
    text = _TEXT[key].get(locale, _TEXT[key]["en"])
    return text.format(**kwargs) if kwargs else text


def _mock_should_speak(
    name: str, context: MeetingContext, agent_input: AgentInput
) -> SpeakingIntent:
    """Rule-based speaking intent for mock agents."""
    # Round 1: always speak
    if context.current_round <= 1:
        return SpeakingIntent(agent_name=name, intent="speak", reason="First round")
    # Speak if user request present
    if agent_input.user_request:
        return SpeakingIntent(agent_name=name, intent="speak", reason="User request present")
    # Speak if energy gap is significant
    energy = agent_input.current_params.energy
    if energy < 0.3 or energy > 0.8:
        return SpeakingIntent(agent_name=name, intent="speak", reason="Energy needs adjustment")
    # Otherwise pass
    return SpeakingIntent(agent_name=name, intent="pass", reason="No strong opinion")


def _mock_vote(
    name: str, context: MeetingContext, _agent_input: AgentInput
) -> TurnVote:
    """Rule-based vote for mock agents."""
    # Round 1: always continue
    if context.current_round <= 1:
        return TurnVote(agent_name=name, vote="continue", reason="Need more discussion")
    # Round 2+: adopt the first DJ who spoke
    dj_names = ["groove", "harmony", "crowd"]
    for msg in reversed(context.messages):
        if msg.role == "dj" and msg.speaker in dj_names:
            return TurnVote(
                agent_name=name, vote="adopt", adopt_agent=msg.speaker,
                reason=f"Agree with {msg.speaker}'s direction",
            )
    return TurnVote(agent_name=name, vote="stop", reason="No strong preference")


class MockGroove:
    """Groove agent: prioritizes rhythm, BPM, and danceability."""

    @property
    def name(self) -> str:
        return "groove"

    async def should_speak(self, context: MeetingContext, agent_input: AgentInput) -> SpeakingIntent:
        return _mock_should_speak(self.name, context, agent_input)

    async def vote(self, context: MeetingContext, agent_input: AgentInput) -> TurnVote:
        return _mock_vote(self.name, context, agent_input)

    async def propose(self, agent_input: AgentInput) -> Proposal:
        params = agent_input.current_params
        new_bpm = min(params.bpm + 4, 200)
        new_energy = min(params.energy + 0.1, 1.0)
        return Proposal(
            agent_name=self.name,
            summary=_t("groove_summary", agent_input.locale),
            perspective="rhythmic momentum",
            suggested_params=MusicParams(
                mood=params.mood,
                bpm=new_bpm,
                energy=round(new_energy, 2),
                texture=params.texture,
                focus="drums",
            ),
        )

    async def revise(self, agent_input: AgentInput, context: object) -> Proposal:
        return await self.propose(agent_input)


class MockHarmony:
    """Harmony agent: prioritizes melody, chords, and musical structure."""

    @property
    def name(self) -> str:
        return "harmony"

    async def should_speak(self, context: MeetingContext, agent_input: AgentInput) -> SpeakingIntent:
        return _mock_should_speak(self.name, context, agent_input)

    async def vote(self, context: MeetingContext, agent_input: AgentInput) -> TurnVote:
        return _mock_vote(self.name, context, agent_input)

    async def propose(self, agent_input: AgentInput) -> Proposal:
        params = agent_input.current_params
        texture = "wide" if params.texture == "layered" else "layered"
        return Proposal(
            agent_name=self.name,
            summary=_t("harmony_summary", agent_input.locale),
            perspective="harmonic depth",
            suggested_params=MusicParams(
                mood=params.mood,
                bpm=params.bpm,
                energy=params.energy,
                texture=texture,
                focus="pad",
            ),
        )

    async def revise(self, agent_input: AgentInput, context: object) -> Proposal:
        return await self.propose(agent_input)


class MockCrowd:
    """Crowd agent: prioritizes audience reception and user requests."""

    @property
    def name(self) -> str:
        return "crowd"

    async def should_speak(self, context: MeetingContext, agent_input: AgentInput) -> SpeakingIntent:
        intent = _mock_should_speak(self.name, context, agent_input)
        # Crowd always speaks if there's a user request
        if agent_input.user_request:
            return SpeakingIntent(agent_name=self.name, intent="speak", reason="User request present")
        return intent

    async def vote(self, context: MeetingContext, agent_input: AgentInput) -> TurnVote:
        return _mock_vote(self.name, context, agent_input)

    async def propose(self, agent_input: AgentInput) -> Proposal:
        params = agent_input.current_params

        if agent_input.user_request:
            return Proposal(
                agent_name=self.name,
                summary=_t("crowd_request", agent_input.locale, request=agent_input.user_request),
                perspective="user request",
                suggested_params=MusicParams(
                    mood=params.mood,
                    bpm=params.bpm,
                    energy=min(params.energy + 0.15, 1.0),
                    texture=params.texture,
                    focus="synth",
                ),
            )

        return Proposal(
            agent_name=self.name,
            summary=_t("crowd_default", agent_input.locale),
            perspective="audience reception",
            suggested_params=MusicParams(
                mood=params.mood,
                bpm=params.bpm,
                energy=params.energy,
                texture=params.texture,
                focus=params.focus,
            ),
        )

    async def revise(self, agent_input: AgentInput, context: object) -> Proposal:
        return await self.propose(agent_input)
