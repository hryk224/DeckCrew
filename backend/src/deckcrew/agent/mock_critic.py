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
                issue="Still warming up — let's see where this goes.",
                severity="low",
                suggestion="Give the set a few turns to develop.",
            )

        if turn >= 3 and params.energy <= 0.55:
            return Critique(
                issue="The energy's been flat for a while now. The floor's losing interest.",
                severity="medium",
                suggestion="Push the energy up — try a bigger shift or a tempo change.",
            )

        if turn >= 3 and params.bpm <= 118:
            return Critique(
                issue="The tempo's been dragging. It's starting to feel sluggish.",
                severity="medium",
                suggestion="Pick up the pace. A BPM bump would break the monotony.",
            )

        return Critique(
            issue="The set's moving nicely. No complaints from me.",
            severity="low",
            suggestion="Keep the momentum going.",
        )
