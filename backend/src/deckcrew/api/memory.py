from fastapi import APIRouter

from deckcrew.memory.models import InterventionRecord, PreferenceProfile
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


@router.get("/profile", response_model=PreferenceProfile)
async def get_profile() -> PreferenceProfile:
    """Return the current preference profile.

    Scope: local process context (single user, no auth).
    """
    return await memory_store.get_profile()


@router.delete("")
async def clear_memory() -> dict[str, str]:
    """Reset all memory (interventions and profile).

    Scope: local process context. Irreversible within the session.
    """
    await memory_store.clear()
    return {"status": "cleared"}
