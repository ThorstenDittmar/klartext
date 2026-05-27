"""Pydantic schemas for the narrative import and retrieval endpoints."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


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


class SceneResponse(BaseModel):
    """A single scene as returned in the API response."""

    id: str
    title: str
    text: str
    position: int


class NarrativeResponse(BaseModel):
    """A full Narrative with all its scenes."""

    id: str
    title: str
    scenes: list[SceneResponse]


class NarrativeSummaryResponse(BaseModel):
    """A Narrative without scenes, used for list views."""

    id: str
    title: str
