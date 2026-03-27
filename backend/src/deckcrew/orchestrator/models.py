from pydantic import BaseModel

from deckcrew.agent.models import Proposal
from deckcrew.state.models import MusicParams, SessionState


class Decision(BaseModel):
    """The Conductor's adoption decision for a single turn."""

    adopted_proposal: Proposal
    reason: str
    applied_params: MusicParams


class TurnResult(BaseModel):
    """Complete result of a single turn execution."""

    proposals: list[Proposal]
    decision: Decision
    state: SessionState
