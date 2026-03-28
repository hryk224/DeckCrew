from deckcrew.agent.models import AgentInput, Proposal
from deckcrew.state.models import MusicParams


class MockGroove:
    """Groove agent: prioritizes rhythm, BPM, and danceability."""

    @property
    def name(self) -> str:
        return "groove"

    async def propose(self, agent_input: AgentInput) -> Proposal:
        params = agent_input.current_params
        new_bpm = min(params.bpm + 4, 200)
        new_energy = min(params.energy + 0.1, 1.0)
        return Proposal(
            agent_name=self.name,
            summary="Push the kick harder, raise tempo slightly for drive",
            perspective="rhythmic momentum",
            suggested_params=MusicParams(
                mood=params.mood,
                bpm=new_bpm,
                energy=round(new_energy, 2),
                texture=params.texture,
                focus="drums",
            ),
        )

    async def revise(self, agent_input: AgentInput, feedback: str) -> Proposal:
        return await self.propose(agent_input)


class MockHarmony:
    """Harmony agent: prioritizes melody, chords, and musical structure."""

    @property
    def name(self) -> str:
        return "harmony"

    async def propose(self, agent_input: AgentInput) -> Proposal:
        params = agent_input.current_params
        texture = "wide" if params.texture == "layered" else "layered"
        return Proposal(
            agent_name=self.name,
            summary="Widen the chord voicing, add floating pad layers",
            perspective="harmonic depth",
            suggested_params=MusicParams(
                mood=params.mood,
                bpm=params.bpm,
                energy=params.energy,
                texture=texture,
                focus="pad",
            ),
        )

    async def revise(self, agent_input: AgentInput, feedback: str) -> Proposal:
        return await self.propose(agent_input)


class MockCrowd:
    """Crowd agent: prioritizes audience reception and user requests."""

    @property
    def name(self) -> str:
        return "crowd"

    async def propose(self, agent_input: AgentInput) -> Proposal:
        params = agent_input.current_params

        if agent_input.user_request:
            return Proposal(
                agent_name=self.name,
                summary=f"Audience wants: {agent_input.user_request}",
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
            summary="Current direction feels right, maintain the vibe",
            perspective="audience reception",
            suggested_params=MusicParams(
                mood=params.mood,
                bpm=params.bpm,
                energy=params.energy,
                texture=params.texture,
                focus=params.focus,
            ),
        )

    async def revise(self, agent_input: AgentInput, feedback: str) -> Proposal:
        return await self.propose(agent_input)
