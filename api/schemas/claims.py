"""Pydantic schemas for claim extraction endpoints."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class ExtractClaimsRequest(BaseModel):
    """Request body for extracting claims from raw text."""

    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Rejects empty or whitespace-only text before it reaches the service."""
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class ClaimResponse(BaseModel):
    """Response shape for a single extracted Claim."""

    label: str
    text: str
    typ: str
    confidence: float
    status: str = "draft"
    wirkgefuege_ref: str | None = None


class ExtractClaimsResponse(BaseModel):
    """Response shape for a claim extraction result."""

    claims: list[ClaimResponse]
