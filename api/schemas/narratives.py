"""Pydantic schemas for all narrative endpoints (create, import, retrieval)."""

from __future__ import annotations

from pydantic import BaseModel, field_validator

from api.models.narrative import ActorType


class ImportNarrativeRequest(BaseModel):
    """Request body for POST /narratives/import."""

    path: str

    @field_validator("path")
    @classmethod
    def path_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only paths."""
        if not value.strip():
            raise ValueError("path must not be empty")
        return value


class CreateNarrativeRequest(BaseModel):
    """Request body for POST /narratives."""

    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only titles."""
        if not value.strip():
            raise ValueError("title must not be empty")
        return value


class CreateSceneRequest(BaseModel):
    """Request body for POST /narratives/{id}/scenes."""

    title: str
    text: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only titles."""
        if not value.strip():
            raise ValueError("title must not be empty")
        return value

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only text."""
        if not value.strip():
            raise ValueError("text must not be empty")
        return value


class CreateActorRequest(BaseModel):
    """Request body for POST /narratives/{id}/actors."""

    label: str
    actor_type: ActorType
    notes: str | None = None
    entity_ref: str | None = None

    @field_validator("label")
    @classmethod
    def label_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only labels."""
        if not value.strip():
            raise ValueError("label must not be empty")
        return value


class UpdateActorRequest(BaseModel):
    """Request body for PUT /narratives/{id}/actors/{actor_id}."""

    label: str
    actor_type: ActorType
    notes: str | None = None

    @field_validator("label")
    @classmethod
    def label_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only labels."""
        if not value.strip():
            raise ValueError("label must not be empty")
        return value


class LinkCausalModelRequest(BaseModel):
    """Request body for PUT /narratives/{id}/causal-model."""

    causal_model_id: str

    @field_validator("causal_model_id")
    @classmethod
    def id_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only IDs."""
        if not value.strip():
            raise ValueError("causal_model_id must not be empty")
        return value


class ActorResponse(BaseModel):
    """A single actor as returned in the API response."""

    id: str
    label: str
    actor_type: str
    notes: str | None
    entity_ref: str | None = None


class SceneResponse(BaseModel):
    """A single scene as returned in the API response."""

    id: str
    title: str
    text: str
    position: int


class NarrativeResponse(BaseModel):
    """A full Narrative with all its scenes and actors."""

    id: str
    title: str
    causal_model_id: str | None = None
    scenes: list[SceneResponse] = []
    actors: list[ActorResponse] = []


class NarrativeSummaryResponse(BaseModel):
    """A Narrative without scenes or actors, used for list views."""

    id: str
    title: str
