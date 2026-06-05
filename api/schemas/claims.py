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

    id: str
    label: str
    text: str
    typ: str
    confidence: float
    status: str = "draft"
    wirkgefuege_ref: str | None = None


class ExtractClaimsResponse(BaseModel):
    """Response shape for a claim extraction result."""

    claims: list[ClaimResponse]


class LinkToWirkgefuegeRequest(BaseModel):
    """Request body for linking a Claim to a Wirkgefüge component."""

    wirkgefuege_ref: str

    @field_validator("wirkgefuege_ref")
    @classmethod
    def ref_not_empty(cls, v: str) -> str:
        """Validates that wirkgefuege_ref is not empty."""
        if not v.strip():
            raise ValueError("wirkgefuege_ref must not be empty")
        return v
