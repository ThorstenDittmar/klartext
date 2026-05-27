"""Router: endpoints for creating, importing and retrieving Narratives and their Claims."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, status

from api.dependencies import (
    get_claim_extractor_service,
    get_claim_repository,
    get_narrative_service,
)
from api.exceptions.narrative import SceneNotFoundError
from api.models.claim import Claim
from api.models.narrative import Narrative, Scene
from api.repositories.claim_repository import ClaimRepository
from api.schemas.claims import ClaimResponse, ExtractClaimsResponse
from api.schemas.narratives import (
    CreateNarrativeRequest,
    CreateSceneRequest,
    ImportNarrativeRequest,
    NarrativeResponse,
    NarrativeSummaryResponse,
    SceneResponse,
)
from api.services.claim_extractor_service import ClaimExtractorService
from api.services.narrative_service import NarrativeService

router = APIRouter(prefix="/narratives")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_narrative_response(narrative: Narrative) -> NarrativeResponse:
    """Converts a Narrative domain object into a NarrativeResponse schema."""
    return NarrativeResponse(
        id=narrative.id,  # type: ignore[arg-type]
        title=narrative.title,
        scenes=[_to_scene_response(scene) for scene in narrative.scenes],
    )


def _to_claim_response(claim: Claim) -> ClaimResponse:
    """Converts a Claim domain object into a ClaimResponse schema."""
    return ClaimResponse(
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
    )


def _to_scene_response(scene: Scene) -> SceneResponse:
    """Converts a Scene domain object into a SceneResponse schema."""
    return SceneResponse(
        id=scene.id,  # type: ignore[arg-type]
        title=scene.title,
        text=scene.text,
        position=scene.position,
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
        raise SceneNotFoundError(
            f"Scene {scene_id} not found in narrative {narrative_id}"
        )

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
