from typing import Any

from pydantic import BaseModel

from deckcrew.state.models import MusicParams

# Event type constants
EVENT_STATE = "session.state"
EVENT_PROPOSALS = "session.proposals"
EVENT_DECISION = "session.decision"
EVENT_HEARTBEAT = "session.heartbeat"


class SSEEvent(BaseModel):
    """A single SSE event to be sent to the client."""

    event: str
    data: dict[str, Any]


class ProposalEvent(BaseModel):
    """Payload schema for session.proposals events."""

    proposals: list[dict[str, Any]]


class DecisionEvent(BaseModel):
    """Payload schema for session.decision events."""

    adopted: str
    reason: str
    applied_params: MusicParams
