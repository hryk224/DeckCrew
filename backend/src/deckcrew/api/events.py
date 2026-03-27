from typing import Any, Literal

from pydantic import BaseModel

from deckcrew.state.models import MusicParams

# Event type constants
EVENT_STATE = "session.state"
EVENT_PROPOSALS = "session.proposals"
EVENT_FEEDBACK = "session.feedback"
EVENT_DECISION = "session.decision"
EVENT_HEARTBEAT = "session.heartbeat"


class SSEEvent(BaseModel):
    """A single SSE event to be sent to the client."""

    event: str
    data: dict[str, Any]


# --- session.proposals ---


class ProposalEvent(BaseModel):
    """Payload schema for session.proposals events."""

    proposals: list[dict[str, Any]]


# --- session.feedback ---


class CriticFeedbackContent(BaseModel):
    """Content of a Critic feedback item."""

    issue: str
    severity: Literal["low", "medium", "high"]
    suggestion: str


class AudienceFeedbackContent(BaseModel):
    """Content of an Audience feedback item."""

    reaction: str
    energy_delta: float
    reason: str


class FeedbackItem(BaseModel):
    """A single feedback entry from a supplementary agent.

    - `source`: agent type, used as a discriminator ("critic" | "audience")
    - `name`: instance identifier within that type. For critic there is one;
      for audience this distinguishes multiple listeners in future (M5).
    - `content`: source-specific payload (CriticFeedbackContent or
      AudienceFeedbackContent). Typed as dict for JSON serialization,
      but callers should construct from the typed models above.
    """

    source: Literal["critic", "audience"]
    name: str
    content: dict[str, Any]


class FeedbackEvent(BaseModel):
    """Payload schema for session.feedback events."""

    items: list[FeedbackItem]


# --- session.decision ---


class RejectedProposal(BaseModel):
    """A proposal that was not adopted, with a brief reason."""

    agent_name: str
    summary: str
    reason: str


class DecisionEvent(BaseModel):
    """Payload schema for session.decision events.

    `rejections` is optional for backward compatibility with M1.
    """

    adopted: str
    reason: str
    applied_params: MusicParams
    rejections: list[RejectedProposal] | None = None
