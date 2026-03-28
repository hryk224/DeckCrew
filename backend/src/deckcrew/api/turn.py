import logging
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from deckcrew.agent.registry import create_agents, create_audiences, create_critic
from deckcrew.api.event_bus import event_bus
from deckcrew.memory.registry import memory_store
from deckcrew.music.registry import music_backend
from deckcrew.orchestrator.conductor import Conductor
from deckcrew.orchestrator.config import MAX_DELIBERATION_ROUNDS
from deckcrew.orchestrator.models import TurnResult
from deckcrew.state.models import ChangeKind
from deckcrew.state.store import session_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["turn"])


class TurnRequest(BaseModel):
    """Optional request body for turn execution."""

    kind: ChangeKind = "major"
    rounds: int | None = Field(default=None, ge=1, le=10)  # None = use config default


@router.post("/session/turn", response_model=TurnResult)
async def execute_turn(body: TurnRequest | None = None) -> TurnResult:
    """Execute a single turn of the DJ meeting.

    kind="major" (default): full proposals + adoption, M1/M2 behavior.
    kind="minor": clamped parameter changes, section preserved.
    """
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    if session.status != "running":
        raise HTTPException(status_code=400, detail="Session is not running")

    kind = body.kind if body else "major"
    max_rounds = body.rounds if body and body.rounds else MAX_DELIBERATION_ROUNDS

    conductor = Conductor(
        agents=create_agents(),
        critic=create_critic(),
        audiences=create_audiences(),
        store=session_store,
        bus=event_bus,
        music=music_backend,
        memory=memory_store,
    )
    try:
        return await conductor.run_turn(session, kind=kind, max_rounds=max_rounds)
    except Exception as e:
        logger.error("run_turn failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Turn failed: {e}")
