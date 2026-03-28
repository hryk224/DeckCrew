"""Lyria Realtime API backend via google-genai SDK.

Connects to models/lyria-realtime-exp through the Gemini Live API
WebSocket. All Lyria-specific protocol details are contained here.

Requires api_version='v1alpha' for the Lyria Realtime endpoint.
"""

import asyncio
import logging
import os
from asyncio import Queue
from typing import Any

from google import genai
from google.genai.errors import APIError
from websockets.exceptions import ConnectionClosedOK

from deckcrew.music.params import LyriaCommand, build_command
from deckcrew.state.models import MusicParams

logger = logging.getLogger(__name__)

_DEFAULT_LYRIA_MODEL = "models/lyria-realtime-exp"

# Maximum audio chunks buffered before dropping old ones
_AUDIO_QUEUE_MAX = 10


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
        self._session_cm: Any = None  # context manager for proper cleanup
        self._last_bpm: int | None = None
        self._audio_q: Queue[bytes] = Queue(maxsize=_AUDIO_QUEUE_MAX)
        self._receive_task: asyncio.Task[None] | None = None
        self._audio_mime: str | None = None

    @property
    def audio_queue(self) -> Queue[bytes] | None:
        return self._audio_q

    @property
    def audio_mime(self) -> str | None:
        """MIME type of audio chunks (e.g. 'audio/l16;rate=48000;channels=2').

        Available after the first chunk is received.
        """
        return self._audio_mime

    async def _open_session(self) -> None:
        """Open a Lyria session via async context manager and configure it."""
        self._session_cm = self._client.aio.live.music.connect(
            model=self._model
        )
        self._session = await self._session_cm.__aenter__()
        await self._session.set_weighted_prompts(
            prompts=[{"text": "Ambient electronic music", "weight": 1.0}]
        )
        await self._session.set_music_generation_config(config={"bpm": 120})
        await self._session.play()

    async def _close_session(self) -> None:
        """Close the Lyria session via context manager exit."""
        if self._session_cm is not None:
            try:
                await self._session_cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._session = None
            self._session_cm = None

    async def start(self) -> None:
        """Open a WebSocket session, set initial prompts, and start playback."""
        await self._open_session()
        self._receive_task = asyncio.create_task(self._receive_loop())
        logger.info("[lyria] Session started, playback and receive loop active")

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
        """Send updated parameters to the Lyria session.

        If the WebSocket has been disconnected (idle timeout etc.),
        automatically reconnects before sending commands.
        """
        if self._session is None:
            logger.warning("[lyria] apply() called but session is not started")
            return

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

    async def _receive_loop(self) -> None:
        """Background task: read audio chunks from Lyria and enqueue them."""
        chunk_count = 0
        try:
            async for message in self._session.receive():
                content = getattr(message, "server_content", None)
                if content is None:
                    continue
                chunks = getattr(content, "audio_chunks", None)
                if not chunks:
                    continue
                for chunk in chunks:
                    data = chunk.data
                    if not data:
                        continue
                    chunk_count += 1
                    # Log first chunk info
                    if chunk_count == 1:
                        mime = getattr(chunk, "mime_type", None)
                        logger.info(
                            "[lyria] First audio chunk: %d bytes, mime=%s",
                            len(data), mime,
                        )
                        if mime:
                            self._audio_mime = mime
                    # Enqueue, drop oldest if full
                    if self._audio_q.full():
                        try:
                            self._audio_q.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                        logger.warning("[lyria] Audio queue full, dropped oldest chunk")
                    self._audio_q.put_nowait(data)
        except asyncio.CancelledError:
            logger.info("[lyria] Receive loop cancelled")
        except ConnectionClosedOK:
            logger.info("[lyria] Receive loop ended: connection closed normally")
        except APIError as e:
            if "1000" in str(e):
                logger.info("[lyria] Receive loop ended: session closed (1000)")
            else:
                logger.exception("[lyria] Receive loop API error")
        except Exception:
            logger.exception("[lyria] Receive loop error")

    async def _reconnect(self) -> None:
        """Close stale session and open a fresh one."""
        if self._receive_task is not None:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except (asyncio.CancelledError, Exception):
                pass
            self._receive_task = None
        await self._close_session()
        await self._open_session()
        self._receive_task = asyncio.create_task(self._receive_loop())
        logger.info("[lyria] Reconnected and playback resumed")

    async def stop(self) -> None:
        """Stop playback, cancel receive loop, and close the session."""
        if self._receive_task is not None:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except (asyncio.CancelledError, Exception):
                pass
            self._receive_task = None
        if self._session is not None:
            try:
                await self._session.stop()
            except Exception:
                logger.warning("[lyria] stop() failed, closing anyway")
        await self._close_session()
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
