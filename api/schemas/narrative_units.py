"""Pydantic schemas for the /narrative-units endpoints."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class NarrativeUnitResponse(BaseModel):
    """Response schema for a single NarrativeUnit — includes its assembled subtree."""

    id: str
    typ: str
    title: str | None
    content: str | None
    position: int
    narrative_id: str
    parent_id: str | None
    children: list[NarrativeUnitResponse] = []

    model_config = {"from_attributes": True}


NarrativeUnitResponse.model_rebuild()


class NarrativeTreeResponse(BaseModel):
    """Response schema for GET /narrative-units/tree/{narrative_id}."""

    narrative_id: str
    root: NarrativeUnitResponse | None


class CreateNarrativeUnitRequest(BaseModel):
    """Request body for POST /narrative-units."""

    typ: str
    title: str | None = None
    content: str | None = None
    position: int
    parent_id: str | None = None
    narrative_id: str

    @field_validator("typ")
    @classmethod
    def typ_must_be_valid(cls, value: str) -> str:
        """Rejects typ values not in the database CHECK constraint."""
        valid = {"work", "part", "chapter", "scene", "fragment"}
        if value not in valid:
            raise ValueError(f"typ must be one of: {', '.join(sorted(valid))}")
        return value


class UpdateNarrativeUnitRequest(BaseModel):
    """Request body for PATCH /narrative-units/{unit_id}.

    Both fields are optional — only the non-None fields are applied.
    """

    title: str | None = None
    content: str | None = None
