"""Tests for the /narratives router.

The NarrativeService is replaced with a FakeNarrativeService via
app.dependency_overrides so no file system or database is involved.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_narrative_service
from api.exceptions.narrative import NarrativeFileNotFoundError, NarrativeNotFoundError
from api.main import app
from api.models.narrative import Narrative, Scene
from api.services.narrative_service import NarrativeService

# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------

SAVED_NARRATIVE_ID = "aaaa-1111"
SAVED_SCENE_ID = "bbbb-2222"


def make_saved_narrative() -> Narrative:
    narrative = Narrative(id=SAVED_NARRATIVE_ID, title="Klartext")
    narrative.add_scene(
        Scene(
            id=SAVED_SCENE_ID,
            title="Szene 1",
            text="Ein kurzer Text.",
            position=1,
        )
    )
    return narrative


SAVED_SCENE_2_ID = "cccc-3333"


class FakeNarrativeService:
    """Returns preset responses without hitting the file system or database."""

    def __init__(
        self,
        *,
        raise_on_import: Exception | None = None,
        raise_on_find: Exception | None = None,
        raise_on_create: Exception | None = None,
        raise_on_add_scene: Exception | None = None,
    ) -> None:
        self._raise_on_import = raise_on_import
        self._raise_on_find = raise_on_find
        self._raise_on_create = raise_on_create
        self._raise_on_add_scene = raise_on_add_scene
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
    assert data["title"] == "Klartext"


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
        FakeNarrativeService(
            raise_on_import=NarrativeFileNotFoundError("File not found.")
        )
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
    assert item["title"] == "Klartext"
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
    override_with(
        FakeNarrativeService(
            raise_on_find=NarrativeNotFoundError("Not found.")
        )
    )
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
            response = await client.post("/narratives", json={"title": "Mein Narrativ"})
    finally:
        clear_overrides()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_narratives_create_response_contains_id_and_title() -> None:
    """Expects the response to include the narrative id and title."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/narratives", json={"title": "Mein Narrativ"})
    finally:
        clear_overrides()

    data = response.json()
    assert data["id"] == SAVED_NARRATIVE_ID
    assert data["title"] == "Mein Narrativ"
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
                json={"title": "Szene 2", "text": "Ein weiterer Text."},
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
                json={"title": "Szene 2", "text": "Ein weiterer Text."},
            )
    finally:
        clear_overrides()

    data = response.json()
    assert data["id"] == SAVED_SCENE_2_ID
    assert data["title"] == "Szene 2"
    assert data["text"] == "Ein weiterer Text."


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
                json={"title": "", "text": "Ein Text."},
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
                json={"title": "Szene", "text": "Text."},
            )
    finally:
        clear_overrides()

    assert response.status_code == 404
