"""Debug endpoints for development.

These endpoints expose internal configuration and are intended
for local development only. Review before public deployment.
"""

from fastapi import APIRouter

from deckcrew.orchestrator.config import get_all_config

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/config")
async def show_config() -> dict[str, float | int]:
    """Return all orchestrator tuning parameters.

    Development use only. Review access before public deployment.
    """
    return get_all_config()
