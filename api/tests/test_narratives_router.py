"""Tests for the /narratives router.

The NarrativeService is replaced with a FakeNarrativeService via
app.dependency_overrides so no file system or database is involved.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import (
    get_claim_repository,
    get_narrative_analysis_service,
    get_narrative_service,
    get_user_service,
    get_wirkgefuege_suggestion_service,
)
from api.exceptions.narrative import (
    ActorNotFoundError,
    NarrativeFileNotFoundError,
    NarrativeNotFoundError,
)
from api.main import app
from api.models.claim import Claim, ClaimType
from api.models.narrative import Actor, ActorType, Narrative, Scene
from api.models.user import User
from api.providers.narrative_analysis_provider import (
    ActorOccurrence,
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisResult,
)
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionResult,
)
from api.repositories.claim_repository import ClaimRepository
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID

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

    async def create(self, title: str, user_id: str | None = None) -> Narrative:
        if self._raise_on_create:
            raise self._raise_on_create
        self.last_create_user_id = user_id
        narrative = Narrative(id=SAVED_NARRATIVE_ID, title=title, user_id=user_id)
        return narrative

    async def add_scene(self, narrative_id: str, title: str, text: str) -> Scene:
        if self._raise_on_add_scene:
            raise self._raise_on_add_scene
        return Scene(id=SAVED_SCENE_2_ID, title=title, text=text, position=2)

    async def import_from_file(self, path: Path, user_id: str | None = None) -> Narrative:
        if self._raise_on_import:
            raise self._raise_on_import
        self.last_import_user_id = user_id
        return make_saved_narrative()

    async def find_by_id(self, narrative_id: str) -> Narrative:
        if self._raise_on_find:
            raise self._raise_on_find
        return make_saved_narrative()

    async def list_all(self) -> list[Narrative]:
        return self._saved

    async def list_for_user(self, user_id: str) -> list[Narrative]:
        return self._saved

    async def list_summaries_for_user(self, user_id: str) -> list:
        """Returns summaries derived from _saved for router tests."""
        from api.models.narrative import NarrativeSummary

        return [
            NarrativeSummary(
                id=n.id,  # type: ignore[arg-type]
                title=n.title,
                causal_model_id=n.causal_model_id,
                user_id=None,
                scene_count=len(n.scenes),
                actor_count=len(n.actors),
                claim_count=0,
            )
            for n in self._saved
        ]

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
# Fake user service
# ---------------------------------------------------------------------------


class FakeUserService:
    """Returns the pre-seeded default user without hitting the database."""

    async def get_default(self) -> User:
        """Returns a User with the default ID used in test fixtures."""
        return User(id=DEFAULT_USER_ID, name="Thorsten")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def override_with(service: FakeNarrativeService) -> None:
    app.dependency_overrides[get_narrative_service] = lambda: service
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()


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


@pytest.mark.asyncio
async def test_narratives_import_assigns_default_user() -> None:
    """Expects import_from_file to be called with the default user's ID so user_id is persisted."""
    service = FakeNarrativeService()
    override_with(service)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/narratives/import", json={"path": "/some/narrative.md"})
    finally:
        clear_overrides()

    assert service.last_import_user_id == DEFAULT_USER_ID


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


@pytest.mark.asyncio
async def test_narratives_list_response_includes_causal_model_id() -> None:
    """Expects each list item to include a causal_model_id field (null by default)."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/narratives")
    finally:
        clear_overrides()

    item = response.json()[0]
    assert "causal_model_id" in item
    assert item["causal_model_id"] is None


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


@pytest.mark.asyncio
async def test_narratives_create_assigns_default_user() -> None:
    """Expects create to be called with the default user's ID so user_id is persisted."""
    service = FakeNarrativeService()
    override_with(service)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/narratives", json={"title": "My Narrative"})
    finally:
        clear_overrides()

    assert service.last_create_user_id == DEFAULT_USER_ID


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
    """Returns preset analysis results without hitting the DB or Claude API.

    Use empty_actor_occurrences=True to simulate an implicit group actor (occurrences=[]).
    Use null_claim_offsets=True to simulate a claim where scene position is unknown.
    """

    def __init__(
        self,
        *,
        raise_on_analyse: Exception | None = None,
        empty_actor_occurrences: bool = False,
        null_claim_offsets: bool = False,
    ) -> None:
        self._raise_on_analyse = raise_on_analyse
        self._empty_actor_occurrences = empty_actor_occurrences
        self._null_claim_offsets = null_claim_offsets

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        """Returns one actor and one claim. Supports edge-case variants via constructor flags."""
        if self._raise_on_analyse:
            raise self._raise_on_analyse
        occurrences = (
            []
            if self._empty_actor_occurrences
            else [ActorOccurrence(scene_title="Scene 1", start_offset=0, end_offset=12)]
        )
        claim_scene_title = None if self._null_claim_offsets else "Scene 1"
        claim_start = None if self._null_claim_offsets else 0
        claim_end = None if self._null_claim_offsets else 38
        return NarrativeAnalysisResult(
            actors=[
                ActorSuggestion(
                    label="Central Bank",
                    actor_type="institution",
                    occurrences=occurrences,
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
                    scene_title=claim_scene_title,
                    start_offset=claim_start,
                    end_offset=claim_end,
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
    app.dependency_overrides[get_narrative_analysis_service] = lambda: (
        FakeNarrativeAnalysisService()
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
async def test_analyse_narrative_serializes_actor_occurrences() -> None:
    """Expects actor occurrences to contain scene_title, start_offset and end_offset fields."""
    app.dependency_overrides[get_narrative_analysis_service] = lambda: (
        FakeNarrativeAnalysisService()
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        body = response.json()
        occurrences = body["actors"][0]["occurrences"]
        assert len(occurrences) == 1
        assert occurrences[0]["scene_title"] == "Scene 1"
        assert occurrences[0]["start_offset"] == 0
        assert occurrences[0]["end_offset"] == 12
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_analyse_narrative_serializes_claim_offsets() -> None:
    """Expects claims to include scene_title, start_offset and end_offset when present."""
    app.dependency_overrides[get_narrative_analysis_service] = lambda: (
        FakeNarrativeAnalysisService()
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        body = response.json()
        claim = body["claims"][0]
        assert claim["scene_title"] == "Scene 1"
        assert claim["start_offset"] == 0
        assert claim["end_offset"] == 38
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_analyse_narrative_serializes_empty_actor_occurrences() -> None:
    """Expects occurrences to be an empty list for implicit group actors."""
    app.dependency_overrides[get_narrative_analysis_service] = lambda: FakeNarrativeAnalysisService(
        empty_actor_occurrences=True
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        body = response.json()
        assert body["actors"][0]["occurrences"] == []
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_analyse_narrative_serializes_null_claim_offsets() -> None:
    """Expects scene_title, start_offset and end_offset to be null when unknown."""
    app.dependency_overrides[get_narrative_analysis_service] = lambda: FakeNarrativeAnalysisService(
        null_claim_offsets=True
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        body = response.json()
        claim = body["claims"][0]
        assert claim["scene_title"] is None
        assert claim["start_offset"] is None
        assert claim["end_offset"] is None
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_analyse_narrative_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    from api.exceptions.narrative import NarrativeNotFoundError

    app.dependency_overrides[get_narrative_analysis_service] = lambda: FakeNarrativeAnalysisService(
        raise_on_analyse=NarrativeNotFoundError("not found")
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives/does-not-exist/analyse")

        assert response.status_code == 404
    finally:
        clear_overrides()


@pytest.mark.asyncio
async def test_analyse_narrative_returns_503_on_analysis_error() -> None:
    """Expects 503 when the service raises NarrativeAnalysisError (e.g. Claude truncation)."""
    from api.exceptions.narrative import NarrativeAnalysisError

    app.dependency_overrides[get_narrative_analysis_service] = lambda: FakeNarrativeAnalysisService(
        raise_on_analyse=NarrativeAnalysisError("Claude API returned invalid JSON")
    )
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        assert response.status_code == 503
        assert "error" in response.json()
    finally:
        clear_overrides()


# ---------------------------------------------------------------------------
# Tests for POST /{narrative_id}/suggest-wirkgefuege
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_wirkgefuege_returns_slots_and_relations() -> None:
    """Expects 200 with suggested slots and relations when the service succeeds."""
    app.dependency_overrides[get_wirkgefuege_suggestion_service] = lambda: (
        FakeWirkgefuegeSuggestionService()
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


# ---------------------------------------------------------------------------
# Fake claim repository for narrative claims tests
# ---------------------------------------------------------------------------


class FakeNarrativeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository with narrative-level storage for router tests."""

    def __init__(self) -> None:
        self._narrative_store: dict[str, list[Claim]] = {}

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Not used in these tests — returns empty list."""
        return []

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Not used in these tests — returns empty list."""
        return []

    async def find_by_id(self, claim_id: str) -> Claim:
        """Not used in these tests — raises ClaimNotFoundError."""
        from api.exceptions.claim import ClaimNotFoundError

        raise ClaimNotFoundError(f"Claim not found: {claim_id}")

    async def update(self, claim: Claim) -> Claim:
        """Not used in these tests — returns claim unchanged."""
        return claim

    async def save_for_narrative(self, claims: list[Claim], narrative_id: str) -> list[Claim]:
        """Stores the given Claims under the given narrative ID."""
        self._narrative_store[narrative_id] = list(claims)
        return list(claims)

    async def find_by_narrative_id(self, narrative_id: str) -> list[Claim]:
        """Returns all Claims saved for the given Narrative ID."""
        return self._narrative_store.get(narrative_id, [])


# ---------------------------------------------------------------------------
# Tests for GET /narratives/{id}/claims
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_narrative_claims_returns_200_with_one_item() -> None:
    """Expects 200 and one claim when a claim has been saved for the narrative."""
    repo = FakeNarrativeClaimRepository()
    claim = Claim(
        id="eeee-5555",
        label="Test Claim",
        text="This is a test claim.",
        typ=ClaimType.CAUSAL,
        confidence=0.8,
    )
    await repo.save_for_narrative([claim], "test-narrative-id")
    app.dependency_overrides[get_claim_repository] = lambda: repo
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/narratives/test-narrative-id/claims")
    finally:
        clear_overrides()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["label"] == "Test Claim"
    assert "id" in data[0]


# ---------------------------------------------------------------------------
# GET /narratives/health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narratives_health_returns_200() -> None:
    """Expects GET /narratives/health to return HTTP 200 with status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/narratives/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
