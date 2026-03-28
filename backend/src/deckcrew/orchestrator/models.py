from pydantic import BaseModel

from deckcrew.agent.models import Proposal
from deckcrew.api.events import FeedbackItem
from deckcrew.state.models import ChangeKind, MusicParams, SessionState


class RoundInfo(BaseModel):
    """Round metadata within a single turn.

    round=1, total_rounds=1 for current 1-shot behavior.
    M6-04 will increase total_rounds for multi-round deliberation.
    """

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


class TurnResult(BaseModel):
    """Complete result of a single turn execution."""

    kind: ChangeKind
    round_info: RoundInfo
    speaker_order: list[str] | None = None
    proposals: list[Proposal]
    feedback: list[FeedbackItem]
    decision: Decision
    state: SessionState
