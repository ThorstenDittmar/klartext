"""Router for claim extraction endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

from api.services import claim_extractor

router = APIRouter()


class ExtractClaimsRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class Claim(BaseModel):
    text: str
    typ: str
    konfidenz: float


class ExtractClaimsResponse(BaseModel):
    claims: list[Claim]


@router.post("/extract-claims", response_model=ExtractClaimsResponse)
async def extract_claims(request: ExtractClaimsRequest) -> ExtractClaimsResponse:
    """Extract preliminary claims from narrative text.

    Claims are provisional – the author must confirm, reject, or reformulate them.
    See Kap. 6.3.1 (Konsistenzschicht) and Kap. 20.2.2 (Claim-Extraktion).
    """
    raw_claims = await claim_extractor.extract_claims_from_text(request.text)
    claims = [Claim(**c) for c in raw_claims]
    return ExtractClaimsResponse(claims=claims)
