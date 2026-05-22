"""Pydantic schemas for Wirkmodell API requests and responses."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, field_validator


class CreateWirkmodellRequest(BaseModel):
    titel: str

    @field_validator("titel")
    @classmethod
    def titel_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("titel must not be empty")
        return v


class AddAxiomRequest(BaseModel):
    label: str
    beschreibung: str

    @field_validator("label", "beschreibung")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v


class CheckConsistencyRequest(BaseModel):
    szenen_text: str

    @field_validator("szenen_text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("szenen_text must not be empty")
        return v


class AxiomResponse(BaseModel):
    id: str
    label: str
    beschreibung: str


class WirkmodellResponse(BaseModel):
    id: str
    titel: str
    status: str
    axiome: list[AxiomResponse]


class WirkmodellSummaryResponse(BaseModel):
    id: str
    titel: str
    status: str


class KonsistenzKonfliktResponse(BaseModel):
    axiom_label: str
    beschreibung: str
    vorschlag: Optional[str]


class KonsistenzResultResponse(BaseModel):
    konsistent: bool
    konflikte: list[KonsistenzKonfliktResponse]
