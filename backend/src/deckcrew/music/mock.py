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
        command = build_command(
            params,
            previous_bpm=self._last_bpm,
            section=section,
            intent=intent,
            time_of_night=time_of_night,
            event_vibe=event_vibe,
            critic_severity=critic_severity,
            user_request=user_request,
        )
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
