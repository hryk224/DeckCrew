"""Lyria Realtime API backend via google-genai SDK.

Connects to models/lyria-realtime-exp through the Gemini Live API
WebSocket. All Lyria-specific protocol details are contained here.
"""

import logging
from typing import Any

from google import genai

from deckcrew.music.params import LyriaCommand, build_command
from deckcrew.state.models import MusicParams

logger = logging.getLogger(__name__)

_MODEL = "models/lyria-realtime-exp"


class LyriaMusicBackend:
    """Live connection to Lyria Realtime API.

    Requires LYRIA_API_KEY to be passed at construction time.
    """

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError(
                "MUSIC_BACKEND=lyria requires LYRIA_API_KEY to be set. "
                "Set the environment variable or switch to MUSIC_BACKEND=mock."
            )
        self._client = genai.Client(api_key=api_key)
        self._session: Any = None
        self._last_bpm: int | None = None

    async def start(self) -> None:
        """Open a WebSocket session and start playback."""
        self._session = await self._client.aio.live.music.connect(
            model=_MODEL
        ).__aenter__()
        await self._session.play()
        logger.info("[lyria] Session started, playback active")

    async def apply(self, params: MusicParams) -> None:
        """Send updated parameters to the Lyria session."""
        if self._session is None:
            logger.warning("[lyria] apply() called but session is not started")
            return

        command = build_command(params, previous_bpm=self._last_bpm)

        # BPM change requires context reset before re-applying
        if command.needs_reset:
            logger.info(
                "[lyria] BPM changed (%s -> %s), resetting context",
                self._last_bpm,
                params.bpm,
            )
            await self._session.reset_context()

        await self._send_command(command)
        self._last_bpm = params.bpm

    async def stop(self) -> None:
        """Stop playback and close the session."""
        if self._session is not None:
            await self._session.stop()
            await self._session.__aexit__(None, None, None)
            self._session = None
            logger.info("[lyria] Session stopped and closed")

    async def _send_command(self, command: LyriaCommand) -> None:
        """Translate LyriaCommand into SDK calls."""
        assert self._session is not None

        # Set weighted prompts
        prompts = [
            {"text": p.text, "weight": p.weight} for p in command.prompts
        ]
        await self._session.set_weighted_prompts(prompts=prompts)

        # Set music generation config
        config: dict[str, Any] = {"bpm": command.config.bpm}
        if command.config.density is not None:
            config["density"] = command.config.density
        if command.config.brightness is not None:
            config["brightness"] = command.config.brightness
        config["mute_bass"] = command.config.mute_bass
        config["mute_drums"] = command.config.mute_drums
        config["only_bass_and_drums"] = command.config.only_bass_and_drums

        await self._session.set_music_generation_config(config=config)
        logger.info("[lyria] Command applied: %d prompts, bpm=%d", len(prompts), command.config.bpm)
