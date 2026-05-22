"""Pydantic schemas for CausalModel API requests and responses."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, field_validator


class CreateCausalModelRequest(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v


class AddAxiomRequest(BaseModel):
    label: str
    description: str

    @field_validator("label", "description")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v


class CheckConsistencyRequest(BaseModel):
    scene_text: str

    @field_validator("scene_text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("scene_text must not be empty")
        return v


class AxiomResponse(BaseModel):
    id: str
    label: str
    description: str


class CausalModelResponse(BaseModel):
    id: str
    title: str
    status: str
    axioms: list[AxiomResponse]


class CausalModelSummaryResponse(BaseModel):
    id: str
    title: str
    status: str


class ConsistencyConflictResponse(BaseModel):
    axiom_label: str
    description: str
    suggestion: Optional[str]


class ConsistencyResultResponse(BaseModel):
    consistent: bool
    conflicts: list[ConsistencyConflictResponse]
