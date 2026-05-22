"""Router for /causal-models endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from api.dependencies import get_causal_model_service
from api.schemas.causal_models import (
    AddAxiomRequest,
    AxiomResponse,
    CausalModelResponse,
    CausalModelSummaryResponse,
    CheckConsistencyRequest,
    ConsistencyConflictResponse,
    ConsistencyResultResponse,
    CreateCausalModelRequest,
)
from api.services.causal_model_service import CausalModelService

router = APIRouter(prefix="/causal-models")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CausalModelResponse)
async def create_causal_model(
    request: CreateCausalModelRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> CausalModelResponse:
    """Creates a new CausalModel."""
    cm = await service.create(title=request.title)
    return CausalModelResponse(
        id=cm.id,  # type: ignore[arg-type]
        title=cm.title,
        status=cm.status.value,
        axioms=[AxiomResponse(id=a.id, label=a.label, description=a.description) for a in cm.axioms],  # type: ignore[arg-type]
    )


@router.get("", response_model=list[CausalModelSummaryResponse])
async def list_causal_models(
    service: CausalModelService = Depends(get_causal_model_service),
) -> list[CausalModelSummaryResponse]:
    """Returns all CausalModels as title-only summaries."""
    cm_list = await service.list_all()
    return [
        CausalModelSummaryResponse(id=cm.id, title=cm.title, status=cm.status.value)  # type: ignore[arg-type]
        for cm in cm_list
    ]


@router.get("/{causal_model_id}", response_model=CausalModelResponse)
async def get_causal_model(
    causal_model_id: str,
    service: CausalModelService = Depends(get_causal_model_service),
) -> CausalModelResponse:
    """Returns a CausalModel with all its Axioms."""
    cm = await service.find_by_id(causal_model_id)
    return CausalModelResponse(
        id=cm.id,  # type: ignore[arg-type]
        title=cm.title,
        status=cm.status.value,
        axioms=[AxiomResponse(id=a.id, label=a.label, description=a.description) for a in cm.axioms],  # type: ignore[arg-type]
    )


@router.post("/{causal_model_id}/axioms", status_code=status.HTTP_201_CREATED, response_model=AxiomResponse)
async def add_axiom(
    causal_model_id: str,
    request: AddAxiomRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> AxiomResponse:
    """Adds an Axiom to an existing CausalModel."""
    axiom = await service.add_axiom(
        causal_model_id=causal_model_id,
        label=request.label,
        description=request.description,
    )
    return AxiomResponse(id=axiom.id, label=axiom.label, description=axiom.description)  # type: ignore[arg-type]


@router.post("/{causal_model_id}/check-consistency", response_model=ConsistencyResultResponse)
async def check_consistency(
    causal_model_id: str,
    request: CheckConsistencyRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> ConsistencyResultResponse:
    """Checks a scene text against the Axioms of the given CausalModel."""
    result = await service.check_consistency(
        causal_model_id=causal_model_id,
        scene_text=request.scene_text,
    )
    return ConsistencyResultResponse(
        consistent=result.consistent,
        conflicts=[
            ConsistencyConflictResponse(
                axiom_label=c.axiom_label,
                description=c.description,
                suggestion=c.suggestion,
            )
            for c in result.conflicts
        ],
    )
