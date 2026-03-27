import os

from deckcrew.music.base import MusicBackend
from deckcrew.music.lyria import LyriaMusicBackend
from deckcrew.music.mock import MockMusicBackend


def create_music_backend() -> MusicBackend:
    """Create a music backend based on the MUSIC_BACKEND env var.

    - "mock" (default): logs operations, no external connection
    - "lyria": connects to Lyria Realtime API (requires LYRIA_API_KEY)
    """
    backend_type = os.environ.get("MUSIC_BACKEND", "mock").lower()

    if backend_type == "lyria":
        api_key = os.environ.get("LYRIA_API_KEY", "")
        return LyriaMusicBackend(api_key=api_key)

    return MockMusicBackend()


# Singleton instance. Created once at import time.
# Session API calls start() / stop() on this instance.
music_backend: MusicBackend = create_music_backend()
