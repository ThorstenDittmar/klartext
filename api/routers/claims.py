"""Router for claim extraction endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_claim_extractor_service, get_claim_service
from api.models.narrative import Scene
from api.schemas.claims import (
    ClaimResponse,
    ExtractClaimsRequest,
    ExtractClaimsResponse,
    LinkToWirkgefuegeRequest,
)
from api.services.claim_extractor_service import ClaimExtractorService
from api.services.claim_service import ClaimService

router = APIRouter()


@router.post("/claims/{claim_id}/link-to-wirkgefuege", response_model=ClaimResponse)
async def link_claim_to_wirkgefuege(
    claim_id: str,
    request: LinkToWirkgefuegeRequest,
    service: ClaimService = Depends(get_claim_service),
) -> ClaimResponse:
    """Links a Claim to a Wirkgefüge component (Slot or CausalRelation).

    Sets the Claim's status to LINKED and stores the wirkgefuege_ref.
    """
    claim = await service.link_to_wirkgefuege(
        claim_id=claim_id,
        wirkgefuege_ref=request.wirkgefuege_ref,
    )
    return ClaimResponse(
        id=claim.id,  # type: ignore[arg-type]
        label=claim.label,
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
        status=claim.status.value,
        wirkgefuege_ref=claim.wirkgefuege_ref,
    )


@router.post("/extract-claims", response_model=ExtractClaimsResponse)
async def extract_claims(
    request: ExtractClaimsRequest,
    service: ClaimExtractorService = Depends(get_claim_extractor_service),
) -> ExtractClaimsResponse:
    """Extracts preliminary claims from narrative text.

    Claims are provisional – the author must confirm, reject, or reformulate them.
    See Kap. 6.3.1 (Konsistenzschicht) and Kap. 20.2.2 (Claim-Extraktion).
    """
    scene = Scene.create(title="Unnamed", text=request.text, position=1)
    claims = await service.extract_from_scene(scene)
    return ExtractClaimsResponse(
        claims=[
            ClaimResponse(
                id=c.id,  # type: ignore[arg-type]
                label=c.label,
                text=c.text,
                typ=c.typ.value,
                confidence=c.confidence,
                status=c.status.value,
                wirkgefuege_ref=c.wirkgefuege_ref,
            )
            for c in claims
        ]
    )
