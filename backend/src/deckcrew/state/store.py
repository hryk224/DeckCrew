import uuid

from deckcrew.state.models import SessionState
from deckcrew.venue.presets import DEFAULT_VENUE


class SessionStore:
    """In-memory session store.

    Holds a single active session for M1.
    Keyed by session_id for future multi-session support.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._active_id: str | None = None

    def create(self) -> SessionState:
        """Create a new session, replacing any existing one."""
        session_id = uuid.uuid4().hex[:12]
        session = SessionState(
            session_id=session_id, status="running", venue=DEFAULT_VENUE
        )
        self._sessions = {session_id: session}
        self._active_id = session_id
        return session

    def get_active(self) -> SessionState | None:
        """Return the active session, or None if no session exists."""
        if self._active_id is None:
            return None
        return self._sessions.get(self._active_id)

    def update(self, session: SessionState) -> None:
        """Persist an updated session state."""
        self._sessions[session.session_id] = session
        self._active_id = session.session_id

    def reset(self) -> SessionState:
        """Reset the active session to initial state."""
        return self.create()


# Singleton instance shared across the application.
session_store = SessionStore()
