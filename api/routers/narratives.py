"""Router: endpoints for creating, importing and retrieving Narratives and their Claims."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, status

from api.dependencies import (
    get_claim_extractor_service,
    get_claim_repository,
    get_narrative_analysis_service,
    get_narrative_service,
    get_wirkgefuege_suggestion_service,
)
from api.exceptions.narrative import SceneNotFoundError
from api.models.claim import Claim
from api.models.narrative import Actor, Narrative, Scene
from api.repositories.claim_repository import ClaimRepository
from api.schemas.claims import ClaimResponse, ExtractClaimsResponse
from api.schemas.narratives import (
    ActorResponse,
    ActorSuggestionResponse,
    AnalyseNarrativeResponse,
    ClaimSuggestionResponse,
    CreateActorRequest,
    CreateNarrativeRequest,
    CreateSceneRequest,
    ImportNarrativeRequest,
    LinkCausalModelRequest,
    NarrativeResponse,
    NarrativeSummaryResponse,
    SceneResponse,
    SuggestedRelationResponse,
    SuggestedSlotResponse,
    SuggestWirkgefuegeResponse,
    UpdateActorRequest,
    WirkgefuegeSuggestionResponse,
)
from api.services.claim_extractor_service import ClaimExtractorService
from api.services.narrative_analysis_service import NarrativeAnalysisService
from api.services.narrative_service import NarrativeService
from api.services.wirkgefuege_suggestion_service import WirkgefuegeSuggestionService

router = APIRouter(prefix="/narratives")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_narrative_response(narrative: Narrative) -> NarrativeResponse:
    """Converts a Narrative domain object into a NarrativeResponse schema."""
    return NarrativeResponse(
        id=narrative.id,  # type: ignore[arg-type]
        title=narrative.title,
        causal_model_id=narrative.causal_model_id,
        scenes=[_to_scene_response(scene) for scene in narrative.scenes],
        actors=[_to_actor_response(actor) for actor in narrative.actors],
    )


def _to_actor_response(actor: Actor) -> ActorResponse:
    """Converts an Actor domain object into an ActorResponse schema."""
    return ActorResponse(
        id=actor.id,  # type: ignore[arg-type]
        label=actor.label,
        actor_type=actor.actor_type.value,
        notes=actor.notes,
        entity_ref=actor.entity_ref,
    )


def _to_claim_response(claim: Claim) -> ClaimResponse:
    """Converts a Claim domain object into a ClaimResponse schema."""
    return ClaimResponse(
        label=claim.label,
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
        status=claim.status.value,
        wirkgefuege_ref=claim.wirkgefuege_ref,
    )


def _to_scene_response(scene: Scene) -> SceneResponse:
    """Converts a Scene domain object into a SceneResponse schema."""
    return SceneResponse(
        id=scene.id,  # type: ignore[arg-type]
        title=scene.title,
        text=scene.text,
        position=scene.position,
    )


def _to_wirkgefuege_suggestion_schema(
    ws: Any,
) -> WirkgefuegeSuggestionResponse:
    """Converts a WirkgefuegeSuggestion dataclass to its Pydantic schema."""
    return WirkgefuegeSuggestionResponse(
        suggestion_type=ws.suggestion_type,
        slot=ws.slot,
        slot_state=ws.slot_state,
        source_slot=ws.source_slot,
        source_condition=ws.source_condition,
        target_slot=ws.target_slot,
        target_effect=ws.target_effect,
        mechanism=ws.mechanism,
    )


def _to_analyse_response(result: Any) -> AnalyseNarrativeResponse:
    """Converts a NarrativeAnalysisResult to AnalyseNarrativeResponse."""
    return AnalyseNarrativeResponse(
        actors=[
            ActorSuggestionResponse(
                label=a.label,
                actor_type=a.actor_type,
                occurrences=a.occurrences,
                entity_suggestion=a.entity_suggestion,
            )
            for a in result.actors
        ],
        claims=[
            ClaimSuggestionResponse(
                label=c.label,
                text=c.text,
                claim_type=c.claim_type,
                confidence=c.confidence,
                wirkgefuege_suggestion=(
                    _to_wirkgefuege_suggestion_schema(c.wirkgefuege_suggestion)
                    if c.wirkgefuege_suggestion
                    else None
                ),
            )
            for c in result.claims
        ],
    )


def _to_suggest_response(result: Any) -> SuggestWirkgefuegeResponse:
    """Converts a WirkgefuegeSuggestionResult to SuggestWirkgefuegeResponse."""
    return SuggestWirkgefuegeResponse(
        suggested_slots=[
            SuggestedSlotResponse(identifier=s.identifier, slot_type=s.slot_type)
            for s in result.suggested_slots
        ],
        suggested_relations=[
            SuggestedRelationResponse(
                source=r.source,
                target=r.target,
                source_condition=r.source_condition,
                target_effect=r.target_effect,
                mechanism=r.mechanism,
                epistemic_status=r.epistemic_status,
            )
            for r in result.suggested_relations
        ],
        from_claims=result.from_claims,
    )


# ---------------------------------------------------------------------------
# Narrative endpoints
# ---------------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NarrativeResponse)
async def create_narrative(
    request: CreateNarrativeRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeResponse:
    """Creates a new empty Narrative with the given title."""
    narrative = await service.create(request.title)
    return _to_narrative_response(narrative)


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
        NarrativeSummaryResponse(id=n.id, title=n.title, causal_model_id=n.causal_model_id)  # type: ignore[arg-type]
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


@router.post(
    "/{narrative_id}/scenes",
    status_code=status.HTTP_201_CREATED,
    response_model=SceneResponse,
)
async def add_scene(
    narrative_id: str,
    request: CreateSceneRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> SceneResponse:
    """Adds a new Scene to the Narrative with the given ID."""
    scene = await service.add_scene(narrative_id, request.title, request.text)
    return _to_scene_response(scene)


# ---------------------------------------------------------------------------
# Actor endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/{narrative_id}/actors",
    status_code=status.HTTP_201_CREATED,
    response_model=ActorResponse,
)
async def add_actor(
    narrative_id: str,
    request: CreateActorRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> ActorResponse:
    """Adds a new Actor to the Narrative with the given ID."""
    actor = await service.add_actor(
        narrative_id,
        request.label,
        request.actor_type,
        request.notes,
        request.entity_ref,
    )
    return _to_actor_response(actor)


@router.put(
    "/{narrative_id}/actors/{actor_id}",
    response_model=ActorResponse,
)
async def update_actor(
    narrative_id: str,
    actor_id: str,
    request: UpdateActorRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> ActorResponse:
    """Updates the label, actor_type and notes of an existing Actor."""
    actor = await service.update_actor(
        narrative_id,
        actor_id,
        request.label,
        request.actor_type,
        request.notes,
    )
    return _to_actor_response(actor)


@router.delete(
    "/{narrative_id}/actors/{actor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_actor(
    narrative_id: str,
    actor_id: str,
    service: NarrativeService = Depends(get_narrative_service),
) -> None:
    """Removes an Actor from the Narrative with the given ID."""
    await service.remove_actor(narrative_id, actor_id)


@router.put(
    "/{narrative_id}/causal-model",
    response_model=NarrativeResponse,
)
async def link_to_causal_model(
    narrative_id: str,
    request: LinkCausalModelRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeResponse:
    """Links the Narrative to a CausalModel by ID."""
    narrative = await service.link_to_causal_model(narrative_id, request.causal_model_id)
    return _to_narrative_response(narrative)


# ---------------------------------------------------------------------------
# Analysis endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/{narrative_id}/analyse",
    response_model=AnalyseNarrativeResponse,
)
async def analyse_narrative(
    narrative_id: str,
    service: NarrativeAnalysisService = Depends(get_narrative_analysis_service),
) -> AnalyseNarrativeResponse:
    """Analyses all scenes in the Narrative and returns suggested actors and claims.

    Does not persist anything — the caller confirms actors/claims via separate endpoints.
    Raises NarrativeNotFoundError (→ 404) if the Narrative does not exist.
    """
    result = await service.analyse(narrative_id)
    return _to_analyse_response(result)


@router.post(
    "/{narrative_id}/suggest-wirkgefuege",
    response_model=SuggestWirkgefuegeResponse,
)
async def suggest_wirkgefuege(
    narrative_id: str,
    service: WirkgefuegeSuggestionService = Depends(get_wirkgefuege_suggestion_service),
) -> SuggestWirkgefuegeResponse:
    """Suggests a minimal Wirkgefüge from all DRAFT Claims of the Narrative.

    Does not persist anything — the caller creates slots/relations via separate endpoints.
    Returns empty suggestions when no DRAFT Claims exist.
    Raises NarrativeNotFoundError (→ 404) if the Narrative does not exist.
    """
    result = await service.suggest_for_narrative(narrative_id)
    return _to_suggest_response(result)


# ---------------------------------------------------------------------------
# Scene claims endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/{narrative_id}/scenes/{scene_id}/extract-claims",
    response_model=ExtractClaimsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def extract_scene_claims(
    narrative_id: str,
    scene_id: str,
    narrative_service: NarrativeService = Depends(get_narrative_service),
    extractor: ClaimExtractorService = Depends(get_claim_extractor_service),
    claim_repo: ClaimRepository = Depends(get_claim_repository),
) -> ExtractClaimsResponse:
    """Extracts Claims for the given Scene, saves them and returns them.

    Raises NarrativeNotFoundError (→ 404) if the Narrative does not exist.
    Raises SceneNotFoundError (→ 404) if the Scene is not part of that Narrative.
    """
    narrative = await narrative_service.find_by_id(narrative_id)

    scene = next((s for s in narrative.scenes if s.id == scene_id), None)
    if scene is None:
        raise SceneNotFoundError(f"Scene {scene_id} not found in narrative {narrative_id}")

    claims = await extractor.extract_from_scene(scene)
    saved_claims = await claim_repo.save_all(claims, scene_id=scene_id)

    return ExtractClaimsResponse(claims=[_to_claim_response(c) for c in saved_claims])


@router.get(
    "/{narrative_id}/scenes/{scene_id}/claims",
    response_model=list[ClaimResponse],
)
async def get_scene_claims(
    narrative_id: str,  # noqa: ARG001 – kept for URL consistency
    scene_id: str,
    claim_repo: ClaimRepository = Depends(get_claim_repository),
) -> list[ClaimResponse]:
    """Returns all Claims that have been extracted for the given Scene."""
    claims = await claim_repo.find_by_scene_id(scene_id)
    return [_to_claim_response(c) for c in claims]
