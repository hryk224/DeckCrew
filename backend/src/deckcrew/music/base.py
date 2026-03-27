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

    async def apply(self, params: MusicParams) -> None:
        """Apply updated control parameters to the running session.

        Does NOT implicitly call start(). The caller is responsible
        for ensuring playback is active before calling apply().
        """
        ...

    async def stop(self) -> None:
        """Stop music generation / playback."""
        ...
