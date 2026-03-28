from asyncio import Queue
from typing import Protocol

from deckcrew.state.models import MusicParams


class MusicBackend(Protocol):
    """Abstract interface for music generation backends.

    Conductor calls only these methods. Lyria-specific details
    must not leak beyond music/ implementations.
    """

    @property
    def audio_queue(self) -> Queue[bytes] | None:
        """Queue of raw audio chunks for browser relay.

        Returns None if the backend does not produce audio
        (e.g. mock backend). The audio WebSocket endpoint
        reads from this queue to stream to the browser.
        """
        ...

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
