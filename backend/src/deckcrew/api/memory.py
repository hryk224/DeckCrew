from fastapi import APIRouter

from deckcrew.memory.models import InterventionRecord
from deckcrew.memory.registry import memory_store

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/interventions", response_model=list[InterventionRecord])
async def list_interventions() -> list[InterventionRecord]:
    """Return all recorded user interventions.

    Scope: local process context (single user, no auth).
    Returns interventions across all sessions in the current
    process lifetime.
    """
    state = await memory_store.load()
    return state.interventions
