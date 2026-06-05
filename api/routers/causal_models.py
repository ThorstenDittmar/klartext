"""Router for /causal-models endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from api.dependencies import get_causal_model_service, get_narrative_service
from api.models.causal_model import CausalModel, CausalRelation
from api.schemas.causal_models import (
    AddAxiomRequest,
    AxiomResponse,
    CausalModelResponse,
    CausalModelSummaryResponse,
    CheckConsistencyRequest,
    ConsistencyConflictResponse,
    ConsistencyResultResponse,
    CreateCausalModelRequest,
    CreateRelationRequest,
    CreateSlotRequest,
    LinkedNarrativeResponse,
    RelationResponse,
    SlotResponse,
    UpdateRelationRequest,
    UpdateSlotRequest,
)
from api.services.causal_model_service import CausalModelService
from api.services.narrative_service import NarrativeService

router = APIRouter(prefix="/causal-models")


def _to_causal_model_response(cm: CausalModel) -> CausalModelResponse:
    """Converts a CausalModel domain object to its API response shape."""
    return CausalModelResponse(
        id=cm.id,  # type: ignore[arg-type]
        title=cm.title,
        status=cm.status.value,
        axioms=[
            AxiomResponse(id=a.id, label=a.label, description=a.description)  # type: ignore[arg-type]
            for a in cm.axioms
        ],
        slots=[
            SlotResponse(
                id=s.id,  # type: ignore[arg-type]
                identifier=s.identifier,
                slot_type=s.slot_type.value,
                epistemic_status=s.epistemic_status.value,
            )
            for s in cm.get_slots()
        ],
        relations=[
            RelationResponse(
                id=r.id,  # type: ignore[arg-type]
                identifier=r.identifier,
                source_slot_id=r.source.id,  # type: ignore[arg-type]
                target_slot_id=r.target.id,  # type: ignore[arg-type]
                mechanism=r.mechanism,
                polarity=r.polarity.value if r.polarity else None,
                epistemic_status=r.epistemic_status.value,
            )
            for r in cm.get_relations()
            if isinstance(r, CausalRelation)
        ],
    )


@router.get("/health")
async def health() -> dict[str, str]:
    """Returns service health status. Public — no authentication required."""
    return {"status": "ok"}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CausalModelResponse)
async def create_causal_model(
    request: CreateCausalModelRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> CausalModelResponse:
    """Creates a new CausalModel."""
    cm = await service.create(title=request.title)
    return _to_causal_model_response(cm)


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
    narrative_service: NarrativeService = Depends(get_narrative_service),
) -> CausalModelResponse:
    """Returns the CausalModel with all Slots, Relations and linked Narratives."""
    cm = await service.find_by_id(causal_model_id)
    linked = await narrative_service.find_by_causal_model_id(causal_model_id)
    response = _to_causal_model_response(cm)
    return response.model_copy(
        update={
            "linked_narratives": [
                LinkedNarrativeResponse(id=n.id, title=n.title)  # type: ignore[arg-type]
                for n in linked
            ]
        }
    )


@router.post(
    "/{causal_model_id}/axioms", status_code=status.HTTP_201_CREATED, response_model=AxiomResponse
)
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


@router.post(
    "/{causal_model_id}/slots",
    status_code=status.HTTP_201_CREATED,
    response_model=SlotResponse,
)
async def add_slot(
    causal_model_id: str,
    request: CreateSlotRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> SlotResponse:
    """Adds a Slot (named placeholder) to an existing CausalModel."""
    slot = await service.add_slot(
        causal_model_id=causal_model_id,
        identifier=request.identifier,
        slot_type=request.slot_type,
        epistemic_status=request.epistemic_status,
    )
    return SlotResponse(
        id=slot.id,  # type: ignore[arg-type]
        identifier=slot.identifier,
        slot_type=slot.slot_type.value,
        epistemic_status=slot.epistemic_status.value,
    )


@router.put("/{causal_model_id}/slots/{slot_id}", response_model=SlotResponse)
async def update_slot(
    causal_model_id: str,
    slot_id: str,
    request: UpdateSlotRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> SlotResponse:
    """Updates the epistemic_status of a Slot."""
    slot = await service.update_slot(
        causal_model_id=causal_model_id,
        slot_id=slot_id,
        epistemic_status=request.epistemic_status,
        identifier=request.identifier,
    )
    return SlotResponse(
        id=slot.id,  # type: ignore[arg-type]
        identifier=slot.identifier,
        slot_type=slot.slot_type.value,
        epistemic_status=slot.epistemic_status.value,
    )


@router.delete(
    "/{causal_model_id}/slots/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_slot(
    causal_model_id: str,
    slot_id: str,
    service: CausalModelService = Depends(get_causal_model_service),
) -> None:
    """Removes a Slot from the CausalModel."""
    await service.remove_slot(causal_model_id=causal_model_id, slot_id=slot_id)


@router.post(
    "/{causal_model_id}/relations",
    status_code=status.HTTP_201_CREATED,
    response_model=RelationResponse,
)
async def add_relation(
    causal_model_id: str,
    request: CreateRelationRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> RelationResponse:
    """Adds a CausalRelation (directed causal link) to an existing CausalModel."""
    relation = await service.add_relation(
        causal_model_id=causal_model_id,
        identifier=request.identifier,
        source_slot_id=request.source_slot_id,
        target_slot_id=request.target_slot_id,
        mechanism=request.mechanism,
        polarity=request.polarity,
    )
    return RelationResponse(
        id=relation.id,  # type: ignore[arg-type]
        identifier=relation.identifier,
        source_slot_id=relation.source.id,  # type: ignore[arg-type]
        target_slot_id=relation.target.id,  # type: ignore[arg-type]
        mechanism=relation.mechanism,
        polarity=relation.polarity.value if relation.polarity else None,
        epistemic_status=relation.epistemic_status.value,
    )


@router.put("/{causal_model_id}/relations/{relation_id}", response_model=RelationResponse)
async def update_relation(
    causal_model_id: str,
    relation_id: str,
    request: UpdateRelationRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> RelationResponse:
    """Updates mechanism, polarity and epistemic_status of a CausalRelation."""
    relation = await service.update_relation(
        causal_model_id=causal_model_id,
        relation_id=relation_id,
        mechanism=request.mechanism,
        polarity=request.polarity,
        epistemic_status=request.epistemic_status,
    )
    return RelationResponse(
        id=relation.id,  # type: ignore[arg-type]
        identifier=relation.identifier,
        source_slot_id=relation.source.id,  # type: ignore[arg-type]
        target_slot_id=relation.target.id,  # type: ignore[arg-type]
        mechanism=relation.mechanism,
        polarity=relation.polarity.value if relation.polarity else None,
        epistemic_status=relation.epistemic_status.value,
    )


@router.delete(
    "/{causal_model_id}/relations/{relation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_relation(
    causal_model_id: str,
    relation_id: str,
    service: CausalModelService = Depends(get_causal_model_service),
) -> None:
    """Removes a CausalRelation from the CausalModel."""
    await service.remove_relation(causal_model_id=causal_model_id, relation_id=relation_id)
