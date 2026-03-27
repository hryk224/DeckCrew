"""Lyria Realtime API backend via google-genai SDK.

Connects to models/lyria-realtime-exp through the Gemini Live API
WebSocket. All Lyria-specific protocol details are contained here.

Requires api_version='v1alpha' for the Lyria Realtime endpoint.
"""

import logging
import os
from typing import Any

from google import genai

from deckcrew.music.params import LyriaCommand, build_command
from deckcrew.state.models import MusicParams

logger = logging.getLogger(__name__)

_DEFAULT_LYRIA_MODEL = "models/lyria-realtime-exp"


class LyriaMusicBackend:
    """Live connection to Lyria Realtime API.

    Requires GOOGLE_API_KEY (or LYRIA_API_KEY for backward compat).
    """

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError(
                "MUSIC_BACKEND=lyria requires GOOGLE_API_KEY to be set. "
                "LYRIA_API_KEY is also accepted for backward compatibility. "
                "Set the environment variable or switch to MUSIC_BACKEND=mock."
            )
        self._client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1alpha"},
        )
        self._model = os.environ.get("LYRIA_MODEL", _DEFAULT_LYRIA_MODEL)
        self._session: Any = None
        self._last_bpm: int | None = None

    async def start(self) -> None:
        """Open a WebSocket session and start playback."""
        self._session = await self._client.aio.live.music.connect(
            model=self._model
        ).__aenter__()
        await self._session.play()
        logger.info("[lyria] Session started, playback active")

    async def apply(self, params: MusicParams) -> None:
        """Send updated parameters to the Lyria session.

        If the WebSocket has been disconnected (idle timeout etc.),
        automatically reconnects before sending commands.
        """
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
            try:
                await self._session.reset_context()
            except Exception:
                logger.info("[lyria] reset_context failed, reconnecting")
                await self._reconnect()

        try:
            await self._send_command(command)
        except Exception:
            logger.info("[lyria] _send_command failed, reconnecting and retrying")
            await self._reconnect()
            await self._send_command(command)
        self._last_bpm = params.bpm

    async def _reconnect(self) -> None:
        """Close stale session and open a fresh one."""
        if self._session is not None:
            try:
                await self._session.close()
            except Exception:
                pass
            self._session = None
        self._session = await self._client.aio.live.music.connect(
            model=self._model
        ).__aenter__()
        await self._session.play()
        logger.info("[lyria] Reconnected and playback resumed")

    async def stop(self) -> None:
        """Stop playback and close the session."""
        if self._session is not None:
            try:
                await self._session.stop()
            except Exception:
                logger.warning("[lyria] stop() failed, closing anyway")
            await self._session.close()
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
