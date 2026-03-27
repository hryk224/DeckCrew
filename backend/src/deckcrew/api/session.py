from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from deckcrew.music.registry import music_backend
from deckcrew.state.models import SessionState
from deckcrew.state.store import session_store

router = APIRouter(prefix="/session", tags=["session"])


class UserRequest(BaseModel):
    """Payload for user input submission."""

    text: str


@router.post("", response_model=SessionState)
async def create_session() -> SessionState:
    """Create a new session and start music playback."""
    session = session_store.create()
    await music_backend.start()
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
