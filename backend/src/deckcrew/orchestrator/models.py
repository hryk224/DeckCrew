from pydantic import BaseModel

from deckcrew.agent.models import Proposal
from deckcrew.api.events import FeedbackItem
from deckcrew.state.models import ChangeKind, MusicParams, SessionState


class RoundInfo(BaseModel):
    """Round metadata within a single turn."""

    round: int
    total_rounds: int


class RejectionDetail(BaseModel):
    """A proposal that was not adopted, with a reason."""

    agent_name: str
    summary: str
    reason: str


class Decision(BaseModel):
    """The Conductor's adoption decision for a single turn."""

    adopted_proposal: Proposal
    reason: str
    applied_params: MusicParams
    rejections: list[RejectionDetail]


class IntentSummary(BaseModel):
    """Summary of an agent's speaking intent."""

    agent_name: str
    intent: str  # "speak" or "pass"
    reason: str


class VoteSummary(BaseModel):
    """Summary of an agent's turn vote."""

    agent_name: str
    vote: str  # "continue", "stop", or "adopt"
    adopt_agent: str | None = None
    reason: str


class DialogueMetadata(BaseModel):
    """Metadata about the dialogue process within a turn."""

    mode: str
    total_messages: int
    rounds_executed: int
    early_stop: bool
    speaker_orders: list[list[str]]
    intents: list[IntentSummary] | None = None
    votes: list[VoteSummary] | None = None
    vote_result: str | None = None  # e.g. "adopt:groove (2/3)"


class TurnResult(BaseModel):
    """Complete result of a single turn execution."""

    kind: ChangeKind
    round_info: RoundInfo
    speaker_order: list[str] | None = None
    dialogue: DialogueMetadata | None = None
    proposals: list[Proposal]
    feedback: list[FeedbackItem]
    decision: Decision
    state: SessionState
