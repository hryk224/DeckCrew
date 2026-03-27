from deckcrew.agent.models import CriticInput, Critique


class MockCritic:
    """Mock Critic agent that evaluates session flow.

    Uses deterministic rules based on current state. Evaluates
    only what is directly observable from CriticInput fields,
    without parsing last_change text.

    Rules (evaluated in order, first match wins):
    1. turn_count < 1  → too early to evaluate
    2. turn_count >= 3 and energy <= 0.55 → energy stagnation
    3. turn_count >= 3 and bpm <= 118 → tempo stagnation
    4. otherwise → flow is progressing well
    """

    @property
    def name(self) -> str:
        return "critic"

    async def evaluate(self, critic_input: CriticInput) -> Critique:
        params = critic_input.current_params
        turn = critic_input.turn_count

        if turn < 1:
            return Critique(
                issue="No prior changes to evaluate",
                severity="low",
                suggestion="Let the session develop before critiquing",
            )

        if turn >= 3 and params.energy <= 0.55:
            return Critique(
                issue="Energy has been low for several turns",
                severity="medium",
                suggestion="Consider a bigger energy shift to avoid flatness",
            )

        if turn >= 3 and params.bpm <= 118:
            return Critique(
                issue="Tempo has stayed low for several turns",
                severity="medium",
                suggestion="A tempo increase would break the monotony",
            )

        return Critique(
            issue="Flow is progressing well",
            severity="low",
            suggestion="No immediate changes needed",
        )
