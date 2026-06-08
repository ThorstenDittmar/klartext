"""Router: /narrative-units endpoints for the narrative content tree."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_narrative_unit_service
from api.models.narrative_unit import (
    Chapter,
    Fragment,
    NarrativeUnit,
    Part,
    Scene,
    Work,
)
from api.schemas.narrative_units import (
    CreateNarrativeUnitRequest,
    NarrativeTreeResponse,
    NarrativeUnitResponse,
    UpdateNarrativeUnitRequest,
)
from api.services.narrative_unit_service import NarrativeUnitService

router = APIRouter(prefix="/narrative-units", tags=["narrative-units"])

_TYP_FACTORY: dict[str, type[NarrativeUnit]] = {
    "work": Work,
    "part": Part,
    "chapter": Chapter,
    "scene": Scene,
    "fragment": Fragment,
}


def _to_response(unit: NarrativeUnit) -> NarrativeUnitResponse:
    """Recursively serialises a NarrativeUnit tree to the response schema."""
    return NarrativeUnitResponse(
        id=unit.id or "",
        typ=unit.typ,
        title=unit.title,
        content=unit.content,
        position=unit.position,
        narrative_id=unit.narrative_id,
        parent_id=unit.parent_id,
        children=[_to_response(child) for child in unit.children],
    )


@router.get("/health")
async def health() -> dict[str, str]:
    """Returns the health status of the narrative-units service."""
    return {"status": "ok", "service": "narrative-units"}


@router.get("/tree/{narrative_id}", response_model=NarrativeTreeResponse)
async def get_tree(
    narrative_id: str,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> NarrativeTreeResponse:
    """Returns the full content tree for a narrative, or root=null if empty."""
    root = await service.get_tree(narrative_id)
    return NarrativeTreeResponse(
        narrative_id=narrative_id,
        root=_to_response(root) if root is not None else None,
    )


@router.post("", response_model=NarrativeUnitResponse, status_code=201)
async def create_unit(
    body: CreateNarrativeUnitRequest,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> NarrativeUnitResponse:
    """Creates a new NarrativeUnit and returns it with an assigned ID."""
    if body.typ == "work":
        unit: NarrativeUnit = Work.create(title=body.title or "", narrative_id=body.narrative_id)
    elif body.typ == "fragment":
        if not body.parent_id:
            raise HTTPException(status_code=422, detail="parent_id is required for fragment")
        unit = Fragment.create(
            content=body.content or "",
            narrative_id=body.narrative_id,
            parent_id=body.parent_id,
            position=body.position,
        )
    else:
        if not body.parent_id:
            raise HTTPException(
                status_code=422,
                detail=f"parent_id is required for typ='{body.typ}'",
            )
        subclass = _TYP_FACTORY[body.typ]
        unit = subclass(
            id=None,
            title=body.title,
            content=body.content,
            position=body.position,
            narrative_id=body.narrative_id,
            parent_id=body.parent_id,
        )
    saved = await service.add_unit(unit)
    return _to_response(saved)


@router.patch("/{unit_id}", response_model=NarrativeUnitResponse)
async def update_unit(
    unit_id: str,
    body: UpdateNarrativeUnitRequest,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> NarrativeUnitResponse:
    """Updates the title and/or content of an existing NarrativeUnit.

    The repository's update() sends only title/content — the shell's other
    fields (position, narrative_id, parent_id) are placeholders not persisted.
    """
    shell = Fragment(
        id=unit_id,
        title=body.title,
        content=body.content,
        position=0,
        narrative_id="",
        parent_id=None,
    )
    updated = await service.update_unit(shell)
    return _to_response(updated)


@router.delete("/{unit_id}", status_code=204)
async def remove_unit(
    unit_id: str,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> None:
    """Deletes a NarrativeUnit and all its descendants."""
    await service.remove_unit(unit_id)
