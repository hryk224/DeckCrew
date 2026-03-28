from typing import Protocol

from deckcrew.state.models import MusicParams


class MusicBackend(Protocol):
    """Abstract interface for music generation backends.

    Conductor calls only these methods. Lyria-specific details
    must not leak beyond music/ implementations.
    """

    async def start(self) -> None:
        """Start music generation / playback."""
        ...

    async def apply(
        self,
        params: MusicParams,
        *,
        section: str = "intro",
        intent: str = "hold",
        time_of_night: str = "peak_hours",
        event_vibe: str = "underground",
        critic_severity: str | None = None,
        user_request: str | None = None,
    ) -> None:
        """Apply updated control parameters to the running session.

        Context arguments (section, intent, etc.) are used by
        build_command() for genre resolution and mood derivation.
        """
        ...

    async def stop(self) -> None:
        """Stop music generation / playback."""
        ...
