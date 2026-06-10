"""Tests for the /narrative-units router.

Two kinds of tests live here:

1. Unit-level router tests — NarrativeUnitService is replaced by FakeNarrativeUnitService
   via app.dependency_overrides. No database, no domain validation.

2. Contract tests (TestCreateFragmentContract) — use the real NarrativeUnitService
   with FakeNarrativeUnitRepository to verify that domain invariants are enforced
   end-to-end through the router. Contract source: docs/contracts/narrative-units-fragment.md
"""

from __future__ import annotations

import uuid

from httpx import ASGITransport, AsyncClient

from api.dependencies import get_narrative_unit_service
from api.exceptions.narrative_unit import NarrativeUnitNotFoundError
from api.main import app
from api.models.narrative_unit import Fragment, NarrativeUnit
from api.services.narrative_unit_service import NarrativeUnitService
from api.tests.fakes.fake_narrative_unit_repository import FakeNarrativeUnitRepository
from api.tests.mothers.narrative_unit_mother import (
    FRAGMENT_ID,
    SCENE_ID,
    TEST_NARRATIVE_ID,
    NarrativeUnitMother,
)

# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeNarrativeUnitService:
    """Returns preset responses; does not touch the database."""

    def __init__(
        self,
        *,
        tree: NarrativeUnit | None = None,
        added_unit: NarrativeUnit | None = None,
        updated_unit: NarrativeUnit | None = None,
        raise_on_update: Exception | None = None,
        raise_on_remove: Exception | None = None,
    ) -> None:
        self._tree = tree
        self._added_unit = added_unit
        self._updated_unit = updated_unit
        self._raise_on_update = raise_on_update
        self._raise_on_remove = raise_on_remove

    async def get_tree(self, narrative_id: str) -> NarrativeUnit | None:
        return self._tree

    async def add_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        if self._added_unit is not None:
            return self._added_unit
        return unit.__class__(
            id=str(uuid.uuid4()),
            title=unit.title,
            content=unit.content,
            position=unit.position,
            narrative_id=unit.narrative_id,
            parent_id=unit.parent_id,
        )

    async def update_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        if self._raise_on_update:
            raise self._raise_on_update
        return self._updated_unit or unit

    async def remove_unit(self, unit_id: str) -> None:
        if self._raise_on_remove:
            raise self._raise_on_remove


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_client(service: FakeNarrativeUnitService) -> AsyncClient:
    app.dependency_overrides[get_narrative_unit_service] = lambda: service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHealth:
    async def test_health_returns_ok(self) -> None:
        """GET /narrative-units/health returns 200 {"status": "ok"}."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.get("/narrative-units/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestGetTree:
    async def test_get_tree_returns_null_root_when_empty(self) -> None:
        """GET /narrative-units/tree/{id} returns 200 with root=null for empty narrative."""
        async with _make_client(FakeNarrativeUnitService(tree=None)) as client:
            response = await client.get(f"/narrative-units/tree/{TEST_NARRATIVE_ID}")
        assert response.status_code == 200
        body = response.json()
        assert body["narrative_id"] == TEST_NARRATIVE_ID
        assert body["root"] is None

    async def test_get_tree_returns_work_with_children(self) -> None:
        """GET /narrative-units/tree/{id} returns the assembled tree."""
        tree = NarrativeUnitMother.work_with_scene_and_fragment()
        async with _make_client(FakeNarrativeUnitService(tree=tree)) as client:
            response = await client.get(f"/narrative-units/tree/{TEST_NARRATIVE_ID}")
        assert response.status_code == 200
        body = response.json()
        assert body["root"]["typ"] == "work"
        assert len(body["root"]["children"]) == 1
        assert body["root"]["children"][0]["typ"] == "scene"


class TestCreateUnit:
    async def test_create_fragment_returns_201(self) -> None:
        """POST /narrative-units returns 201 with the created unit."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": "Ein neuer Absatz.",
                    "position": 1,
                    "parent_id": SCENE_ID,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 201
        body = response.json()
        assert body["typ"] == "fragment"
        assert body["content"] == "Ein neuer Absatz."

    async def test_create_unit_with_invalid_typ_returns_422(self) -> None:
        """POST /narrative-units rejects unknown typ values with 422."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "banana",
                    "content": "text",
                    "position": 1,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422


class TestUpdateUnit:
    async def test_update_fragment_content_returns_200(self) -> None:
        """PATCH /narrative-units/{id} returns 200 with the updated unit."""
        updated = Fragment(
            id=FRAGMENT_ID,
            title=None,
            content="Updated.",
            position=1,
            narrative_id=TEST_NARRATIVE_ID,
            parent_id=SCENE_ID,
        )
        async with _make_client(FakeNarrativeUnitService(updated_unit=updated)) as client:
            response = await client.patch(
                f"/narrative-units/{FRAGMENT_ID}",
                json={"content": "Updated."},
            )
        assert response.status_code == 200
        assert response.json()["content"] == "Updated."

    async def test_update_unknown_unit_returns_404(self) -> None:
        """PATCH /narrative-units/{id} returns 404 when unit does not exist."""
        async with _make_client(
            FakeNarrativeUnitService(raise_on_update=NarrativeUnitNotFoundError("not found"))
        ) as client:
            response = await client.patch(
                "/narrative-units/does-not-exist",
                json={"content": "x"},
            )
        assert response.status_code == 404


class TestRemoveUnit:
    async def test_remove_unit_returns_204(self) -> None:
        """DELETE /narrative-units/{id} returns 204 on success."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.delete(f"/narrative-units/{FRAGMENT_ID}")
        assert response.status_code == 204

    async def test_remove_unknown_unit_returns_404(self) -> None:
        """DELETE /narrative-units/{id} returns 404 when the unit does not exist."""
        async with _make_client(
            FakeNarrativeUnitService(raise_on_remove=NarrativeUnitNotFoundError("not found"))
        ) as client:
            response = await client.delete("/narrative-units/does-not-exist")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Contract tests — real service, fake repository
# ---------------------------------------------------------------------------


def _make_real_service_client() -> AsyncClient:
    """Returns a client wired to the real NarrativeUnitService with a FakeNarrativeUnitRepository.

    Used by contract tests to exercise the full domain validation chain without
    hitting the database. The fake repository is sufficient because the domain
    invariant fires before any repository call is made.
    """
    real_service = NarrativeUnitService(repository=FakeNarrativeUnitRepository())
    app.dependency_overrides[get_narrative_unit_service] = lambda: real_service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestCreateFragmentContract:
    """Contract tests for POST /narrative-units (typ=fragment).

    Verifies that the backend enforces the Fragment content invariant end-to-end
    through the router. These tests use the real NarrativeUnitService (not a fake)
    so that domain validation cannot be accidentally bypassed by a service stub.

    Contract source: docs/contracts/narrative-units-fragment.md
    """

    async def test_empty_content_returns_422(self) -> None:
        """POST /narrative-units with content='' returns 422.

        Contract: a Fragment with empty content violates the domain invariant
        and must be rejected with 422 and error message 'content must not be empty'.
        """
        async with _make_real_service_client() as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": "",
                    "position": 1,
                    "parent_id": SCENE_ID,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422
        assert response.json()["error"] == "content must not be empty"

    async def test_whitespace_only_content_returns_422(self) -> None:
        """POST /narrative-units with content='   ' (whitespace-only) returns 422.

        Contract: whitespace-only content is treated as empty by the domain invariant.
        """
        async with _make_real_service_client() as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": "   ",
                    "position": 1,
                    "parent_id": SCENE_ID,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422
        assert response.json()["error"] == "content must not be empty"

    async def test_null_content_returns_422(self) -> None:
        """POST /narrative-units with content=null returns 422.

        The router coerces null to '' via `body.content or ""`, which the domain
        invariant then rejects. Contract: content must be present and non-empty.
        """
        async with _make_real_service_client() as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": None,
                    "position": 1,
                    "parent_id": SCENE_ID,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422
        assert response.json()["error"] == "content must not be empty"
