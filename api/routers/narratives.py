"""Router: endpoints for importing and retrieving Narratives."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, status

from api.dependencies import get_narrative_service
from api.models.narrative import Narrative
from api.schemas.narratives import (
    ImportNarrativeRequest,
    NarrativeResponse,
    NarrativeSummaryResponse,
    SceneResponse,
)
from api.services.narrative_service import NarrativeService

router = APIRouter(prefix="/narratives")


def _to_narrative_response(narrative: Narrative) -> NarrativeResponse:
    """Converts a Narrative domain object into a NarrativeResponse schema."""
    return NarrativeResponse(
        id=narrative.id,  # type: ignore[arg-type]
        title=narrative.title,
        scenes=[
            SceneResponse(
                id=scene.id,  # type: ignore[arg-type]
                title=scene.title,
                text=scene.text,
                position=scene.position,
            )
            for scene in narrative.scenes
        ],
    )


@router.post(
    "/import",
    response_model=NarrativeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_narrative(
    request: ImportNarrativeRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeResponse:
    """Imports a Narrative from the given file path, saves it and returns it with IDs."""
    narrative = await service.import_from_file(Path(request.path))
    return _to_narrative_response(narrative)


@router.get("", response_model=list[NarrativeSummaryResponse])
async def list_narratives(
    service: NarrativeService = Depends(get_narrative_service),
) -> list[NarrativeSummaryResponse]:
    """Returns all persisted Narratives as a flat list without their scenes."""
    narratives = await service.list_all()
    return [
        NarrativeSummaryResponse(id=n.id, title=n.title)  # type: ignore[arg-type]
        for n in narratives
    ]


@router.get("/{narrative_id}", response_model=NarrativeResponse)
async def get_narrative(
    narrative_id: str,
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeResponse:
    """Returns the Narrative with the given ID, including its Scenes."""
    narrative = await service.find_by_id(narrative_id)
    return _to_narrative_response(narrative)
