from deckcrew.agent.models import CriticInput, Critique

_CRITIQUES: dict[str, dict[str, dict[str, str]]] = {
    "early": {
        "issue": {
            "en": "Still warming up — let's see where this goes.",
            "ja": "まだ序盤だ、もう少し様子を見よう。",
        },
        "suggestion": {
            "en": "Give the set a few turns to develop.",
            "ja": "数ターン回してからセットの方向性を判断する。",
        },
    },
    "low_energy": {
        "issue": {
            "en": "The energy's been flat for a while now. The floor's losing interest.",
            "ja": "エネルギーが停滞してる。フロアの関心が薄れてきた。",
        },
        "suggestion": {
            "en": "Push the energy up — try a bigger shift or a tempo change.",
            "ja": "もっとエネルギーを上げろ。大きめの変化かテンポチェンジを試せ。",
        },
    },
    "slow_tempo": {
        "issue": {
            "en": "The tempo's been dragging. It's starting to feel sluggish.",
            "ja": "テンポが重い。もたつき始めてる。",
        },
        "suggestion": {
            "en": "Pick up the pace. A BPM bump would break the monotony.",
            "ja": "ペースを上げろ。BPM を上げて単調さを壊せ。",
        },
    },
    "good": {
        "issue": {
            "en": "The set's moving nicely. No complaints from me.",
            "ja": "セットはうまく流れてる。文句なし。",
        },
        "suggestion": {
            "en": "Keep the momentum going.",
            "ja": "この勢いを維持しろ。",
        },
    },
}


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
        loc = critic_input.locale

        if turn < 1:
            c = _CRITIQUES["early"]
            return Critique(issue=c["issue"].get(loc, c["issue"]["en"]), severity="low", suggestion=c["suggestion"].get(loc, c["suggestion"]["en"]))

        if turn >= 3 and params.energy <= 0.55:
            c = _CRITIQUES["low_energy"]
            return Critique(issue=c["issue"].get(loc, c["issue"]["en"]), severity="medium", suggestion=c["suggestion"].get(loc, c["suggestion"]["en"]))

        if turn >= 3 and params.bpm <= 118:
            c = _CRITIQUES["slow_tempo"]
            return Critique(issue=c["issue"].get(loc, c["issue"]["en"]), severity="medium", suggestion=c["suggestion"].get(loc, c["suggestion"]["en"]))

        c = _CRITIQUES["good"]
        return Critique(issue=c["issue"].get(loc, c["issue"]["en"]), severity="low", suggestion=c["suggestion"].get(loc, c["suggestion"]["en"]))
