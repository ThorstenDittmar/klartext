"""Pydantic schemas for CausalModel API requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class CreateCausalModelRequest(BaseModel):
    """Request body for creating a new CausalModel."""

    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v


class AddAxiomRequest(BaseModel):
    """Request body for adding an Axiom to a CausalModel."""

    label: str
    description: str

    @field_validator("label", "description")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v


class CheckConsistencyRequest(BaseModel):
    """Request body for checking a scene's consistency against a CausalModel."""

    scene_text: str

    @field_validator("scene_text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("scene_text must not be empty")
        return v


class AxiomResponse(BaseModel):
    """Response shape for a single Axiom."""

    id: str
    label: str
    description: str


class SlotResponse(BaseModel):
    """Response shape for a single Slot."""

    id: str
    identifier: str
    slot_type: str
    epistemic_status: str
    is_entity: bool = False


class RelationResponse(BaseModel):
    """Response shape for a single CausalRelation."""

    id: str
    identifier: str
    source_slot_id: str
    target_slot_id: str
    mechanism: str | None
    polarity: str | None
    epistemic_status: str


class CausalModelResponse(BaseModel):
    """Response shape for a CausalModel with its Axioms, Slots and CausalRelations."""

    id: str
    title: str
    status: str
    axioms: list[AxiomResponse]
    slots: list[SlotResponse] = []
    relations: list[RelationResponse] = []


class CausalModelSummaryResponse(BaseModel):
    """Response shape for a CausalModel without Axioms (list view)."""

    id: str
    title: str
    status: str


class CreateSlotRequest(BaseModel):
    """Request body for adding a Slot to a CausalModel."""

    identifier: str
    slot_type: str
    epistemic_status: str = "incomplete"

    @field_validator("identifier")
    @classmethod
    def identifier_not_empty(cls, v: str) -> str:
        """Validates that identifier is not empty."""
        if not v.strip():
            raise ValueError("identifier must not be empty")
        return v


class UpdateSlotRequest(BaseModel):
    """Request body for updating a Slot's epistemic_status."""

    epistemic_status: str


class CreateRelationRequest(BaseModel):
    """Request body for adding a CausalRelation to a CausalModel."""

    identifier: str
    source_slot_id: str
    target_slot_id: str
    mechanism: str | None = None
    polarity: str | None = None

    @field_validator("identifier")
    @classmethod
    def identifier_not_empty(cls, v: str) -> str:
        """Validates that identifier is not empty."""
        if not v.strip():
            raise ValueError("identifier must not be empty")
        return v


class UpdateRelationRequest(BaseModel):
    """Request body for updating a CausalRelation."""

    mechanism: str | None = None
    polarity: str | None = None
    epistemic_status: str = "incomplete"


class ConsistencyConflictResponse(BaseModel):
    """Response shape for a single consistency conflict between a scene and an Axiom."""

    axiom_label: str
    description: str
    suggestion: str | None


class ConsistencyResultResponse(BaseModel):
    """Response shape for the full consistency check result."""

    consistent: bool
    conflicts: list[ConsistencyConflictResponse]
