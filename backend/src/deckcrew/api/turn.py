from fastapi import APIRouter, HTTPException

from deckcrew.agent.registry import create_agents, create_audiences, create_critic
from deckcrew.api.event_bus import event_bus
from deckcrew.music.registry import music_backend
from deckcrew.orchestrator.conductor import Conductor
from deckcrew.orchestrator.models import TurnResult
from deckcrew.state.store import session_store

router = APIRouter(tags=["turn"])


@router.post("/session/turn", response_model=TurnResult)
async def execute_turn() -> TurnResult:
    """Execute a single turn of the DJ meeting."""
    session = session_store.get_active()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session")
    if session.status != "running":
        raise HTTPException(status_code=400, detail="Session is not running")

    conductor = Conductor(
        agents=create_agents(),
        critic=create_critic(),
        audiences=create_audiences(),
        store=session_store,
        bus=event_bus,
        music=music_backend,
    )
    return await conductor.run_turn(session)
