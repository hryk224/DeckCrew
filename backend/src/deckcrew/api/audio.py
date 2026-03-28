"""WebSocket endpoint for streaming Lyria audio to the browser.

Reads raw audio chunks from the music backend's audio_queue and
sends them as binary WebSocket frames. Closes gracefully when
the backend has no audio (mock mode) or the session ends.

NOTE: Single-client design. Multiple WebSocket clients will compete
for chunks from the same queue, causing each to receive only a
fraction of the audio. For multi-client support, a broadcast
mechanism (e.g. per-client queues) would be needed.
"""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from deckcrew.music.registry import music_backend

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/session/audio")
async def audio_stream(ws: WebSocket) -> None:
    """Stream raw audio chunks from Lyria to the browser."""
    await ws.accept()

    queue = music_backend.audio_queue
    if queue is None:
        # Mock backend — no audio available, close with 4000 (app-level "no audio")
        await ws.close(code=4000, reason="No audio backend")
        return

    # Send audio format metadata as first text message
    mime = getattr(music_backend, "audio_mime", None)
    if mime:
        await ws.send_text(mime)
    else:
        # Format not yet known; send placeholder, client will detect from data
        await ws.send_text("audio/l16")

    logger.info("[audio-ws] Client connected, streaming audio")
    try:
        while True:
            try:
                chunk = await asyncio.wait_for(queue.get(), timeout=5.0)
                await ws.send_bytes(chunk)
            except TimeoutError:
                # Send ping to keep connection alive during silence
                await ws.send_bytes(b"")
    except WebSocketDisconnect:
        logger.info("[audio-ws] Client disconnected")
    except Exception:
        logger.exception("[audio-ws] Stream error")
    finally:
        logger.info("[audio-ws] Stream ended")
