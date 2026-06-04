"""Router for claim extraction endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_claim_extractor_service
from api.models.narrative import Scene
from api.schemas.claims import ClaimResponse, ExtractClaimsRequest, ExtractClaimsResponse
from api.services.claim_extractor_service import ClaimExtractorService

router = APIRouter()


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
