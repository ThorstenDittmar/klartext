"""Router for /wirkmodelle endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from api.dependencies import get_wirkmodell_service
from api.schemas.wirkmodelle import (
    AddAxiomRequest,
    AxiomResponse,
    CheckConsistencyRequest,
    CreateWirkmodellRequest,
    KonsistenzKonfliktResponse,
    KonsistenzResultResponse,
    WirkmodellResponse,
    WirkmodellSummaryResponse,
)
from api.services.wirkmodell_service import WirkmodellService

router = APIRouter(prefix="/wirkmodelle")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WirkmodellResponse)
async def create_wirkmodell(
    request: CreateWirkmodellRequest,
    service: WirkmodellService = Depends(get_wirkmodell_service),
) -> WirkmodellResponse:
    """Creates a new Wirkmodell."""
    wm = await service.create(titel=request.titel)
    return WirkmodellResponse(
        id=wm.id,  # type: ignore[arg-type]
        titel=wm.titel,
        status=wm.status.value,
        axiome=[AxiomResponse(id=a.id, label=a.label, beschreibung=a.beschreibung) for a in wm.axiome],  # type: ignore[arg-type]
    )


@router.get("", response_model=list[WirkmodellSummaryResponse])
async def list_wirkmodelle(
    service: WirkmodellService = Depends(get_wirkmodell_service),
) -> list[WirkmodellSummaryResponse]:
    """Returns all Wirkmodelle as title-only summaries."""
    wm_list = await service.list_all()
    return [
        WirkmodellSummaryResponse(id=wm.id, titel=wm.titel, status=wm.status.value)  # type: ignore[arg-type]
        for wm in wm_list
    ]


@router.get("/{wirkmodell_id}", response_model=WirkmodellResponse)
async def get_wirkmodell(
    wirkmodell_id: str,
    service: WirkmodellService = Depends(get_wirkmodell_service),
) -> WirkmodellResponse:
    """Returns a Wirkmodell with all its Axiome."""
    wm = await service.find_by_id(wirkmodell_id)
    return WirkmodellResponse(
        id=wm.id,  # type: ignore[arg-type]
        titel=wm.titel,
        status=wm.status.value,
        axiome=[AxiomResponse(id=a.id, label=a.label, beschreibung=a.beschreibung) for a in wm.axiome],  # type: ignore[arg-type]
    )


@router.post("/{wirkmodell_id}/axiome", status_code=status.HTTP_201_CREATED, response_model=AxiomResponse)
async def add_axiom(
    wirkmodell_id: str,
    request: AddAxiomRequest,
    service: WirkmodellService = Depends(get_wirkmodell_service),
) -> AxiomResponse:
    """Adds an Axiom to an existing Wirkmodell."""
    axiom = await service.add_axiom(
        wirkmodell_id=wirkmodell_id,
        label=request.label,
        beschreibung=request.beschreibung,
    )
    return AxiomResponse(id=axiom.id, label=axiom.label, beschreibung=axiom.beschreibung)  # type: ignore[arg-type]


@router.post("/{wirkmodell_id}/check-consistency", response_model=KonsistenzResultResponse)
async def check_consistency(
    wirkmodell_id: str,
    request: CheckConsistencyRequest,
    service: WirkmodellService = Depends(get_wirkmodell_service),
) -> KonsistenzResultResponse:
    """Checks a scene text against the Axiome of the given Wirkmodell."""
    result = await service.check_consistency(
        wirkmodell_id=wirkmodell_id,
        szenen_text=request.szenen_text,
    )
    return KonsistenzResultResponse(
        konsistent=result.konsistent,
        konflikte=[
            KonsistenzKonfliktResponse(
                axiom_label=k.axiom_label,
                beschreibung=k.beschreibung,
                vorschlag=k.vorschlag,
            )
            for k in result.konflikte
        ],
    )
