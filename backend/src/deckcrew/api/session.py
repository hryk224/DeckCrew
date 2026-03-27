import logging
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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


@router.post("/reset", response_model=SessionState)
async def reset_session() -> SessionState:
    """Reset the session: stop music, restart with fresh state."""
    await music_backend.stop()
    session = session_store.reset()
    await music_backend.start()
    return session
