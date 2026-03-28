import logging
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from deckcrew.orchestrator.auto_loop import auto_loop
from deckcrew.orchestrator.meeting import DialogueMode
from deckcrew.orchestrator.models import TurnResult
from deckcrew.state.models import ChangeKind
from deckcrew.state.store import session_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["turn"])


class TurnRequest(BaseModel):
    """Optional request body for turn execution."""

    kind: ChangeKind = "major"
    rounds: int | None = Field(default=None, ge=1, le=10)  # None = use config default
    dialogue_mode: DialogueMode | None = None  # None = use config default


@router.post("/session/turn", response_model=TurnResult)
async def execute_turn(body: TurnRequest | None = None) -> TurnResult:
    """Execute a manual turn (always major by default).

    Uses the auto_loop's lock to prevent concurrent execution
    with automatic turns, then resets the auto timer.
    """
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    if session.status != "running":
        raise HTTPException(status_code=400, detail="Session is not running")

    kind = body.kind if body else "major"
    max_rounds = body.rounds if body and body.rounds else None
    mode = body.dialogue_mode if body and body.dialogue_mode else None

    try:
        result = await auto_loop.run_manual_turn(
            kind=kind,
            max_rounds=max_rounds,
            dialogue_mode=mode,
        )
        if result is None:
            raise HTTPException(status_code=500, detail="Turn returned no result")
        return result  # type: ignore[return-value]
    except Exception as e:
        logger.error("run_turn failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Turn failed: {e}")
