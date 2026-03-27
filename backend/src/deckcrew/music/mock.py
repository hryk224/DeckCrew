import logging

from deckcrew.music.params import build_command
from deckcrew.state.models import MusicParams

logger = logging.getLogger(__name__)


class MockMusicBackend:
    """Mock music backend for local development.

    Logs all operations instead of connecting to Lyria.
    """

    def __init__(self) -> None:
        self._playing = False
        self._last_bpm: int | None = None

    async def start(self) -> None:
        self._playing = True
        logger.info("[mock-music] Started playback")

    async def apply(self, params: MusicParams) -> None:
        command = build_command(params, previous_bpm=self._last_bpm)
        if command.needs_reset:
            logger.info(
                "[mock-music] BPM changed (%s -> %s), would reset context",
                self._last_bpm,
                params.bpm,
            )
        prompt_strs = [f'"{p.text}" (w={p.weight})' for p in command.prompts]
        logger.info("[mock-music] Prompts: %s", ", ".join(prompt_strs))
        logger.info(
            "[mock-music] Config: bpm=%d density=%s mute_drums=%s "
            "mute_bass=%s only_bass_and_drums=%s",
            command.config.bpm,
            command.config.density,
            command.config.mute_drums,
            command.config.mute_bass,
            command.config.only_bass_and_drums,
        )
        self._last_bpm = params.bpm

    async def stop(self) -> None:
        self._playing = False
        logger.info("[mock-music] Stopped playback")
