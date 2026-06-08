"""Debug router — not in the normal navigation.

Exposes internal object graph data for development inspection.
These endpoints are intentionally not listed in the frontend nav.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_debug_graph_service, get_user_service
from api.schemas.debug import DebugGraphResponse
from api.services.debug_graph_service import DebugGraphService
from api.services.user_service import UserService

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/health")
async def debug_health() -> dict[str, str]:
    """Returns HTTP 200 to confirm the debug router is mounted and reachable."""
    return {"status": "ok"}


@router.get("/object-graph", response_model=DebugGraphResponse)
async def get_object_graph(
    debug_service: DebugGraphService = Depends(get_debug_graph_service),
    user_service: UserService = Depends(get_user_service),
) -> DebugGraphResponse:
    """Returns all domain objects for the current user as a navigable graph.

    Traverses User → Narratives → Scenes/Actors/Claims → CausalModels
    → Slots/Relations/Axioms and returns them as flat node and edge lists
    for the frontend React Flow renderer.
    """
    user = await user_service.get_default()
    return await debug_service.build_graph(str(user.id))
