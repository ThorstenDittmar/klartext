"""Tests for the /narratives router.

The NarrativeService is replaced with a FakeNarrativeService via
app.dependency_overrides so no file system or database is involved.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import (
    get_narrative_analysis_service,
    get_narrative_service,
    get_wirkgefuege_suggestion_service,
)
from api.exceptions.narrative import (
    ActorNotFoundError,
    NarrativeFileNotFoundError,
    NarrativeNotFoundError,
)
from api.main import app
from api.models.narrative import Actor, ActorType, Narrative, Scene
from api.providers.narrative_analysis_provider import (
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisResult,
)
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionResult,
)

# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------

SAVED_NARRATIVE_ID = "aaaa-1111"
SAVED_SCENE_ID = "bbbb-2222"


def make_saved_narrative() -> Narrative:
    narrative = Narrative(id=SAVED_NARRATIVE_ID, title="A Test Narrative")
    narrative.add_scene(
        Scene(
            id=SAVED_SCENE_ID,
            title="Scene 1",
            text="A short text.",
            position=1,
        )
    )
    return narrative


SAVED_SCENE_2_ID = "cccc-3333"
SAVED_ACTOR_ID = "dddd-4444"


class FakeNarrativeService:
    """Returns preset responses without hitting the file system or database."""

    def __init__(
        self,
        *,
        raise_on_import: Exception | None = None,
        raise_on_find: Exception | None = None,
        raise_on_create: Exception | None = None,
        raise_on_add_scene: Exception | None = None,
        raise_on_add_actor: Exception | None = None,
        raise_on_update_actor: Exception | None = None,
        raise_on_remove_actor: Exception | None = None,
        raise_on_link_to_causal_model: Exception | None = None,
    ) -> None:
        self._raise_on_import = raise_on_import
        self._raise_on_find = raise_on_find
        self._raise_on_create = raise_on_create
        self._raise_on_add_scene = raise_on_add_scene
        self._raise_on_add_actor = raise_on_add_actor
        self._raise_on_update_actor = raise_on_update_actor
        self._raise_on_remove_actor = raise_on_remove_actor
        self._raise_on_link_to_causal_model = raise_on_link_to_causal_model
        self._saved: list[Narrative] = [make_saved_narrative()]

    async def create(self, title: str) -> Narrative:
        if self._raise_on_create:
            raise self._raise_on_create
        narrative = Narrative(id=SAVED_NARRATIVE_ID, title=title)
        return narrative

    async def add_scene(self, narrative_id: str, title: str, text: str) -> Scene:
        if self._raise_on_add_scene:
            raise self._raise_on_add_scene
        return Scene(id=SAVED_SCENE_2_ID, title=title, text=text, position=2)

    async def import_from_file(self, path: Path) -> Narrative:
        if self._raise_on_import:
            raise self._raise_on_import
        return make_saved_narrative()

    async def find_by_id(self, narrative_id: str) -> Narrative:
        if self._raise_on_find:
            raise self._raise_on_find
        return make_saved_narrative()

    async def list_all(self) -> list[Narrative]:
        return self._saved

    async def add_actor(
        self,
        narrative_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None = None,
        entity_ref: str | None = None,
    ) -> Actor:
        if self._raise_on_add_actor:
            raise self._raise_on_add_actor
        return Actor(
            id=SAVED_ACTOR_ID,
            label=label,
            actor_type=actor_type,
            notes=notes,
            entity_ref=entity_ref,
        )

    async def update_actor(
        self,
        narrative_id: str,
        actor_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None,
        entity_ref: str | None = None,
    ) -> Actor:
        if self._raise_on_update_actor:
            raise self._raise_on_update_actor
        return Actor(
            id=actor_id, label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref
        )

    async def remove_actor(self, narrative_id: str, actor_id: str) -> None:
        if self._raise_on_remove_actor:
            raise self._raise_on_remove_actor

    async def link_to_causal_model(self, narrative_id: str, causal_model_id: str) -> Narrative:
        if self._raise_on_link_to_causal_model:
            raise self._raise_on_link_to_causal_model
        narrative = Narrative(
            id=narrative_id, title="A Test Narrative", causal_model_id=causal_model_id
        )
        return narrative


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def override_with(service: FakeNarrativeService) -> None:
    app.dependency_overrides[get_narrative_service] = lambda: service


def clear_overrides() -> None:
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /narratives/import – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_import_returns_201() -> None:
    """Expects 201 when a valid path is provided and the service succeeds."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/narratives/import",
                json={"path": "/some/narrative.md"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_narratives_import_response_contains_id_and_title() -> None:
    """Expects the response to include the narrative id and title."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/narratives/import",
                json={"path": "/some/narrative.md"},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert data["id"] == SAVED_NARRATIVE_ID
    assert data["title"] == "A Test Narrative"


@pytest.mark.asyncio
async def test_narratives_import_response_contains_scenes() -> None:
    """Expects the response to include the scenes produced by the service."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/narratives/import",
                json={"path": "/some/narrative.md"},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert len(data["scenes"]) == 1
    assert data["scenes"][0]["id"] == SAVED_SCENE_ID


# ---------------------------------------------------------------------------
# POST /narratives/import – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_import_returns_422_for_empty_path() -> None:
    """Expects 422 when the path field is an empty string."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives/import", json={"path": ""})
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_import_returns_404_when_file_not_found() -> None:
    """Expects 404 when the service raises NarrativeFileNotFoundError."""
    override_with(
        FakeNarrativeService(raise_on_import=NarrativeFileNotFoundError("File not found."))
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/narratives/import",
                json={"path": "/nonexistent.md"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /narratives – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_list_returns_200() -> None:
    """Expects 200 and a list when narratives exist."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/narratives")
    finally:
        clear_overrides()

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_narratives_list_response_contains_narrative_summary() -> None:
    """Expects each item in the list to have id and title but no scenes."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/narratives")
    finally:
        clear_overrides()

    item = response.json()[0]
    assert item["id"] == SAVED_NARRATIVE_ID
    assert item["title"] == "A Test Narrative"
    assert "scenes" not in item


# ---------------------------------------------------------------------------
# GET /narratives/{id} – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_get_by_id_returns_200() -> None:
    """Expects 200 and the full Narrative when a known ID is requested."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/narratives/{SAVED_NARRATIVE_ID}")
    finally:
        clear_overrides()

    assert response.status_code == 200
    assert response.json()["id"] == SAVED_NARRATIVE_ID


@pytest.mark.asyncio
async def test_narratives_get_by_id_returns_404_for_unknown_id() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    override_with(FakeNarrativeService(raise_on_find=NarrativeNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/narratives/unknown-id")
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /narratives – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_create_returns_201() -> None:
    """Expects 201 when a valid title is provided."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives", json={"title": "My Narrative"})
    finally:
        clear_overrides()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_narratives_create_response_contains_id_and_title() -> None:
    """Expects the response to include the narrative id and title."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives", json={"title": "My Narrative"})
    finally:
        clear_overrides()

    data = response.json()
    assert data["id"] == SAVED_NARRATIVE_ID
    assert data["title"] == "My Narrative"
    assert data["scenes"] == []


# ---------------------------------------------------------------------------
# POST /narratives – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_create_returns_422_for_empty_title() -> None:
    """Expects 422 when the title field is an empty string."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives", json={"title": ""})
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_create_returns_422_for_whitespace_only_title() -> None:
    """Expects 422 when the title field contains only whitespace."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives", json={"title": "   "})
    finally:
        clear_overrides()

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /narratives/{id}/scenes – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_add_scene_returns_201() -> None:
    """Expects 201 when a valid scene is added to an existing narrative."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/scenes",
                json={"title": "Scene 2", "text": "Another text."},
            )
    finally:
        clear_overrides()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_narratives_add_scene_response_contains_id_title_and_text() -> None:
    """Expects the response to include the scene id, title, text and position."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/scenes",
                json={"title": "Scene 2", "text": "Another text."},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert data["id"] == SAVED_SCENE_2_ID
    assert data["title"] == "Scene 2"
    assert data["text"] == "Another text."


# ---------------------------------------------------------------------------
# POST /narratives/{id}/scenes – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_add_scene_returns_422_for_empty_title() -> None:
    """Expects 422 when the title field is empty."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/scenes",
                json={"title": "", "text": "A text."},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_add_scene_returns_422_for_whitespace_only_title() -> None:
    """Expects 422 when the title field contains only whitespace."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/scenes",
                json={"title": "   ", "text": "A text."},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_add_scene_returns_422_for_empty_text() -> None:
    """Expects 422 when the text field is empty."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/scenes",
                json={"title": "Scene 1", "text": ""},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_add_scene_returns_422_for_whitespace_only_text() -> None:
    """Expects 422 when the text field contains only whitespace."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/scenes",
                json={"title": "Scene 1", "text": "   "},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_add_scene_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    override_with(FakeNarrativeService(raise_on_add_scene=NarrativeNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/narratives/unknown-id/scenes",
                json={"title": "Scene", "text": "Text."},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /narratives/{id}/actors – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_add_actor_returns_201() -> None:
    """Expects 201 when a valid actor is added to an existing narrative."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors",
                json={"label": "Max", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_narratives_add_actor_response_contains_id_label_and_actor_type() -> None:
    """Expects the response to include the actor id, label and actor_type."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors",
                json={"label": "Max", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert data["id"] == SAVED_ACTOR_ID
    assert data["label"] == "Max"
    assert data["actor_type"] == "individual"


# ---------------------------------------------------------------------------
# POST /narratives/{id}/actors – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_add_actor_returns_422_for_empty_label() -> None:
    """Expects 422 when the label field is an empty string."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors",
                json={"label": "", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_add_actor_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    override_with(FakeNarrativeService(raise_on_add_actor=NarrativeNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/narratives/unknown-id/actors",
                json={"label": "Max", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /narratives/{id}/actors/{actor_id} – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_update_actor_returns_200() -> None:
    """Expects 200 when a valid update is sent for an existing actor."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors/{SAVED_ACTOR_ID}",
                json={"label": "CDU", "actor_type": "organisation", "notes": "A party."},
            )
    finally:
        clear_overrides()

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_narratives_update_actor_response_contains_updated_fields() -> None:
    """Expects the response to reflect the new label, actor_type and notes."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors/{SAVED_ACTOR_ID}",
                json={"label": "CDU", "actor_type": "organisation", "notes": "A party."},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert data["label"] == "CDU"
    assert data["actor_type"] == "organisation"
    assert data["notes"] == "A party."


# ---------------------------------------------------------------------------
# PUT /narratives/{id}/actors/{actor_id} – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_update_actor_returns_422_for_empty_label() -> None:
    """Expects 422 when the label field is an empty string."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors/{SAVED_ACTOR_ID}",
                json={"label": "", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_update_actor_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    override_with(FakeNarrativeService(raise_on_update_actor=NarrativeNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/unknown-id/actors/{SAVED_ACTOR_ID}",
                json={"label": "Max", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_narratives_update_actor_returns_404_for_unknown_actor() -> None:
    """Expects 404 when the service raises ActorNotFoundError."""
    override_with(FakeNarrativeService(raise_on_update_actor=ActorNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors/unknown-actor-id",
                json={"label": "Max", "actor_type": "individual"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /narratives/{id}/actors/{actor_id} – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_remove_actor_returns_204() -> None:
    """Expects 204 No Content when an existing actor is deleted."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors/{SAVED_ACTOR_ID}",
            )
    finally:
        clear_overrides()

    assert response.status_code == 204


# ---------------------------------------------------------------------------
# DELETE /narratives/{id}/actors/{actor_id} – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_remove_actor_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    override_with(FakeNarrativeService(raise_on_remove_actor=NarrativeNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                f"/narratives/unknown-id/actors/{SAVED_ACTOR_ID}",
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_narratives_remove_actor_returns_404_for_unknown_actor() -> None:
    """Expects 404 when the service raises ActorNotFoundError."""
    override_with(FakeNarrativeService(raise_on_remove_actor=ActorNotFoundError("Not found.")))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                f"/narratives/{SAVED_NARRATIVE_ID}/actors/unknown-actor-id",
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /narratives/{id}/causal-model – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_link_to_causal_model_returns_200() -> None:
    """Expects 200 when a valid causal model ID is linked to an existing narrative."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/causal-model",
                json={"causal_model_id": "model-xyz"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_narratives_link_to_causal_model_response_contains_causal_model_id() -> None:
    """Expects the response to include the linked causal_model_id."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/causal-model",
                json={"causal_model_id": "model-xyz"},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert data["causal_model_id"] == "model-xyz"


# ---------------------------------------------------------------------------
# PUT /narratives/{id}/causal-model – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_link_to_causal_model_returns_422_for_empty_id() -> None:
    """Expects 422 when the causal_model_id field is an empty string."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/narratives/{SAVED_NARRATIVE_ID}/causal-model",
                json={"causal_model_id": ""},
            )
    finally:
        clear_overrides()

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_narratives_link_to_causal_model_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    override_with(
        FakeNarrativeService(raise_on_link_to_causal_model=NarrativeNotFoundError("Not found."))
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                "/narratives/unknown-id/causal-model",
                json={"causal_model_id": "model-xyz"},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Fake services for analysis endpoints
# ---------------------------------------------------------------------------


class FakeNarrativeAnalysisService:
    """Returns preset analysis results without hitting the DB or Claude API."""

    def __init__(
        self,
        *,
        raise_on_analyse: Exception | None = None,
    ) -> None:
        self._raise_on_analyse = raise_on_analyse

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        if self._raise_on_analyse:
            raise self._raise_on_analyse
        return NarrativeAnalysisResult(
            actors=[
                ActorSuggestion(
                    label="Central Bank",
                    actor_type="institution",
                    occurrences=["Scene 1"],
                    entity_suggestion="central_bank",
                )
            ],
            claims=[
                ClaimSuggestion(
                    label="Money supply causes inflation",
                    text="Higher money supply leads to inflation.",
                    claim_type="causal",
                    confidence=0.87,
                    wirkgefuege_suggestion=None,
                )
            ],
        )


class FakeWirkgefuegeSuggestionService:
    """Returns preset suggestion results without hitting the DB or Claude API."""

    def __init__(
        self,
        *,
        raise_on_suggest: Exception | None = None,
    ) -> None:
        self._raise_on_suggest = raise_on_suggest

    async def suggest_for_narrative(self, narrative_id: str) -> WirkgefuegeSuggestionResult:
        if self._raise_on_suggest:
            raise self._raise_on_suggest
        return WirkgefuegeSuggestionResult(
            suggested_slots=[
                SuggestedSlot(identifier="money_supply", slot_type="physical_quantity"),
                SuggestedSlot(identifier="inflation", slot_type="trend"),
            ],
            suggested_relations=[
                SuggestedRelation(
                    source="money_supply",
                    target="inflation",
                    mechanism="quantity_theory",
                    epistemic_status="incomplete",
                )
            ],
            from_claims=["claim-uuid-1"],
        )


# ---------------------------------------------------------------------------
# Tests for POST /{narrative_id}/analyse
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyse_narrative_returns_actors_and_claims() -> None:
    """Expects 200 with actors and claims when the service succeeds."""
    app.dependency_overrides[get_narrative_analysis_service] = (
        lambda: FakeNarrativeAnalysisService()
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        assert response.status_code == 200
        body = response.json()
        assert len(body["actors"]) == 1
        assert body["actors"][0]["label"] == "Central Bank"
        assert len(body["claims"]) == 1
        assert body["claims"][0]["claim_type"] == "causal"
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_analyse_narrative_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    from api.exceptions.narrative import NarrativeNotFoundError

    app.dependency_overrides[get_narrative_analysis_service] = lambda: (
        FakeNarrativeAnalysisService(raise_on_analyse=NarrativeNotFoundError("not found"))
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives/does-not-exist/analyse")

        assert response.status_code == 404
    finally:
        clear_overrides()


# ---------------------------------------------------------------------------
# Tests for POST /{narrative_id}/suggest-wirkgefuege
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_wirkgefuege_returns_slots_and_relations() -> None:
    """Expects 200 with suggested slots and relations when the service succeeds."""
    app.dependency_overrides[get_wirkgefuege_suggestion_service] = (
        lambda: FakeWirkgefuegeSuggestionService()
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/suggest-wirkgefuege")

        assert response.status_code == 200
        body = response.json()
        assert len(body["suggested_slots"]) == 2
        assert body["suggested_slots"][0]["identifier"] == "money_supply"
        assert len(body["suggested_relations"]) == 1
        assert body["from_claims"] == ["claim-uuid-1"]
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_suggest_wirkgefuege_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    from api.exceptions.narrative import NarrativeNotFoundError

    app.dependency_overrides[get_wirkgefuege_suggestion_service] = lambda: (
        FakeWirkgefuegeSuggestionService(raise_on_suggest=NarrativeNotFoundError("not found"))
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives/does-not-exist/suggest-wirkgefuege")

        assert response.status_code == 404
    finally:
        clear_overrides()
