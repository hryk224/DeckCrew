import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from deckcrew.api.event_bus import event_bus
from deckcrew.api.events import EVENT_HEARTBEAT, EVENT_STATE, SSEEvent
from deckcrew.state.store import session_store

router = APIRouter(tags=["stream"])

HEARTBEAT_INTERVAL_SECONDS = 15


def _format_sse(event: SSEEvent) -> str:
    """Format an SSEEvent as a wire-protocol SSE message."""
    data_json = json.dumps(event.data, ensure_ascii=False)
    return f"event: {event.event}\ndata: {data_json}\n\n"


async def _event_stream() -> AsyncGenerator[str, None]:
    """Generate SSE events for the client.

    Sends an initial state snapshot (if session exists), then relays
    events from the EventBus. Sends heartbeats to keep the connection alive.
    """
    queue = event_bus.subscribe()
    try:
        # Send initial state snapshot if a session exists
        session = session_store.get_active()
        if session is not None:
            initial = SSEEvent(event=EVENT_STATE, data=session.model_dump())
            yield _format_sse(initial)

        # Stream events from the bus with periodic heartbeats
        while True:
            try:
                event = await asyncio.wait_for(
                    queue.get(), timeout=HEARTBEAT_INTERVAL_SECONDS
                )
                yield _format_sse(event)
            except asyncio.TimeoutError:
                heartbeat = SSEEvent(
                    event=EVENT_HEARTBEAT,
                    data={"timestamp": datetime.now(UTC).isoformat()},
                )
                yield _format_sse(heartbeat)
    except asyncio.CancelledError:
        pass
    finally:
        event_bus.unsubscribe(queue)


@router.get("/session/stream")
async def session_stream() -> StreamingResponse:
    """SSE endpoint for streaming session events."""
    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
