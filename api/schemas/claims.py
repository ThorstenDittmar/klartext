"""Pydantic schemas for claim extraction endpoints."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class ExtractClaimsRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Rejects empty or whitespace-only text before it reaches the service."""
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class ClaimResponse(BaseModel):
    text: str
    typ: str
    confidence: float


class ExtractClaimsResponse(BaseModel):
    claims: list[ClaimResponse]
