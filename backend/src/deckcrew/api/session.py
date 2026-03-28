import logging
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from deckcrew.api.event_bus import event_bus
from deckcrew.api.events import EVENT_STATE, SSEEvent
from deckcrew.music.genres import GROUPS_BY_ID
from deckcrew.music.registry import music_backend
from deckcrew.state.models import SessionState
from deckcrew.state.store import session_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/session", tags=["session"])


class UserRequest(BaseModel):
    """Payload for user input submission."""

    text: str


@router.post("", response_model=SessionState)
async def create_session() -> SessionState:
    """Create a new session and start music playback.

    If a session already exists, stops the current music backend
    before creating a fresh session (reset-then-start).
    """
    if session_store.get_active() is not None:
        await music_backend.stop()
    session = session_store.create()
    try:
        await music_backend.start()
    except Exception as e:
        logger.error("music_backend.start() failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=502, detail=f"Music backend failed: {e}")
    # Broadcast new session state via SSE so UI updates immediately
    await event_bus.publish(
        SSEEvent(event=EVENT_STATE, data=session.model_dump())
    )
    return session


@router.get("", response_model=SessionState)
async def get_session() -> SessionState:
    """Return the current active session state."""
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    return session


@router.post("/request", response_model=SessionState)
async def submit_request(body: UserRequest) -> SessionState:
    """Submit a user request to influence the current session."""
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    if session.status != "running":
        raise HTTPException(status_code=400, detail="Session is not running")
    updated = session.model_copy(update={"last_user_request": body.text})
    session_store.update(updated)
    return updated


_SUPPORTED_LOCALES = {"en", "ja"}


class ParamsUpdate(BaseModel):
    """Partial update for session params."""

    genre_group: str | None = None
    locale: str | None = None


@router.patch("/params", response_model=SessionState)
async def update_params(body: ParamsUpdate) -> SessionState:
    """Partially update session params (e.g. genre_group, locale)."""
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    if session.status != "running":
        raise HTTPException(status_code=400, detail="Session is not running")

    updates: dict[str, object] = {}

    if body.genre_group is not None:
        if body.genre_group not in GROUPS_BY_ID:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown genre_group: {body.genre_group}",
            )
        updates["current_params"] = session.current_params.model_copy(
            update={"genre_group": body.genre_group},
        )

    if body.locale is not None:
        if body.locale not in _SUPPORTED_LOCALES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported locale: {body.locale}",
            )
        updates["locale"] = body.locale

    if updates:
        updated = session.model_copy(update=updates)
        session_store.update(updated)
        await event_bus.publish(
            SSEEvent(event=EVENT_STATE, data=updated.model_dump())
        )
        return updated
    return session


@router.post("/stop")
async def stop_session() -> dict[str, str]:
    """Stop the current session and music playback."""
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    await music_backend.stop()
    updated = session.model_copy(update={"status": "stopped"})
    session_store.update(updated)
    await event_bus.publish(
        SSEEvent(event=EVENT_STATE, data=updated.model_dump())
    )
    return {"status": "stopped"}


@router.post("/reset", response_model=SessionState)
async def reset_session() -> SessionState:
    """Reset the session: stop music, restart with fresh state."""
    await music_backend.stop()
    session = session_store.reset()
    await music_backend.start()
    return session
