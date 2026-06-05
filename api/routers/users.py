"""Router: /users endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Returns the health status of the users service."""
    return {"status": "ok"}
