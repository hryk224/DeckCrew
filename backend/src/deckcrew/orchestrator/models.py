from pydantic import BaseModel

from deckcrew.agent.models import Proposal
from deckcrew.api.events import FeedbackItem
from deckcrew.state.models import MusicParams, SessionState


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

    proposals: list[Proposal]
    feedback: list[FeedbackItem]
    decision: Decision
    state: SessionState
