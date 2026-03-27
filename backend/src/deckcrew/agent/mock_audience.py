from deckcrew.agent.models import AudienceInput, Reaction


class MockAudience:
    """Mock Audience agent that returns virtual listener reactions.

    Uses deterministic rules based on current state. Reflects
    reception and energy demand, not evaluation or proposals.

    Rules (evaluated in order, first match wins):
    1. energy <= 0.3 → crowd wants more excitement
    2. energy >= 0.7 → crowd is feeling the energy
    3. bpm >= 140    → pace is too intense for some
    4. otherwise     → comfortable vibe, no strong push
    """

    @property
    def name(self) -> str:
        return "audience"

    async def react(self, audience_input: AudienceInput) -> Reaction:
        params = audience_input.current_params

        if params.energy <= 0.3:
            return Reaction(
                audience_name=self.name,
                reaction="Losing interest...",
                energy_delta=0.3,
                reason="Energy is too low, the crowd needs more excitement",
            )

        if params.energy >= 0.7:
            return Reaction(
                audience_name=self.name,
                reaction="Feeling the energy!",
                energy_delta=0.1,
                reason="The crowd is responding well to the intensity",
            )

        if params.bpm >= 140:
            return Reaction(
                audience_name=self.name,
                reaction="The pace is intense!",
                energy_delta=-0.1,
                reason="Some in the crowd are struggling to keep up",
            )

        return Reaction(
            audience_name=self.name,
            reaction="Vibing along",
            energy_delta=0.0,
            reason="The mood is comfortable, no strong push either way",
        )
