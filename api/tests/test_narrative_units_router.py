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

    async def test_create_fragment_without_parent_id_returns_422(self) -> None:
        """POST /narrative-units with typ=fragment and no parent_id returns 422.

        The router enforces that fragments must have a parent_id (a parent scene).
        """
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": "Some text.",
                    "position": 1,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422

    async def test_create_scene_without_parent_id_returns_422(self) -> None:
        """POST /narrative-units with typ=scene and no parent_id returns 422.

        All non-work, non-fragment types require a parent_id.
        """
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "scene",
                    "title": "A Scene",
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

    async def test_valid_content_returns_201(self) -> None:
        """POST /narrative-units with valid content returns 201 through the real service.

        Contract: valid Fragment content passes all domain invariants and is
        persisted, returning 201 with the saved unit.
        """
        async with _make_real_service_client() as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": "Ein vollständiger Absatz.",
                    "position": 1,
                    "parent_id": SCENE_ID,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 201
        body = response.json()
        assert body["typ"] == "fragment"
        assert body["content"] == "Ein vollständiger Absatz."


class TestCreateWorkContract:
    """Contract tests for POST /narrative-units (typ=work).

    Verifies that the Work title invariant is enforced end-to-end through the
    real NarrativeUnitService — not bypassed by a fake stub.
    """

    async def test_empty_title_returns_422(self) -> None:
        """POST /narrative-units with typ=work and empty title returns 422.

        Work.create() raises NarrativeUnitValidationError for empty titles,
        which the global exception handler translates to 422.
        """
        async with _make_real_service_client() as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "work",
                    "title": "",
                    "position": 1,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422
        assert response.json()["error"] == "title must not be empty"

    async def test_whitespace_only_title_returns_422(self) -> None:
        """POST /narrative-units with typ=work and whitespace-only title returns 422."""
        async with _make_real_service_client() as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "work",
                    "title": "   ",
                    "position": 1,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422
        assert response.json()["error"] == "title must not be empty"


class TestDeleteUnitContract:
    """Contract tests for DELETE /narrative-units/{id}.

    Verifies the full chain — real NarrativeUnitService + FakeNarrativeUnitRepository —
    to ensure the 204/404 contract from docs/contracts/narrative-units-fragment.md
    (section: API Contract DELETE /narrative-units/{id}) is enforced end-to-end.

    These tests use the real service (not FakeNarrativeUnitService) so that the
    NarrativeUnitNotFoundError propagation path through the service cannot be
    accidentally bypassed by a stub.
    """

    async def test_delete_existing_unit_returns_204(self) -> None:
        """DELETE /narrative-units/{id} with a known ID returns 204.

        Contract: a successful delete removes the unit and returns 204 No Content.
        """
        repo = FakeNarrativeUnitRepository()
        real_service = NarrativeUnitService(repository=repo)
        app.dependency_overrides[get_narrative_unit_service] = lambda: real_service

        # Pre-seed a unit via the service so the fake repo has it with a real ID.
        from api.tests.mothers.narrative_unit_mother import NarrativeUnitMother

        saved = await real_service.add_unit(NarrativeUnitMother.unsaved_fragment())
        assert saved.id is not None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/narrative-units/{saved.id}")
        assert response.status_code == 204

    async def test_delete_unknown_unit_returns_404(self) -> None:
        """DELETE /narrative-units/{id} with an unknown ID returns 404.

        Contract: the real service propagates NarrativeUnitNotFoundError from the
        repository; the central exception handler translates it to 404 with
        {"error": "Narrative unit not found: <id>"}.
        """
        real_service = NarrativeUnitService(repository=FakeNarrativeUnitRepository())
        app.dependency_overrides[get_narrative_unit_service] = lambda: real_service

        unknown_id = "00000000-0000-0000-0000-000000000000"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/narrative-units/{unknown_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["error"].lower()


class TestDeleteUnitSemanticsContract:
    """QA-owned complementary contract tests for the strict DELETE semantics (DELETE-404).

    TestDeleteUnitContract above already covers the two core cases (204 known, 404
    unknown) through the real service chain. These tests verify the *consequences* of
    the strict Option-B decision that those two cases do not — the exact failure modes
    the contract rationale names: double-deletes, stale IDs, and consistency with the
    other mutating verb (PATCH).

    Contract source: docs/contracts/narrative-units-fragment.md
    (section: API Contract DELETE /narrative-units/{id} — rationale: "must not be
    silently swallowed … mask bugs such as double-deletes or stale IDs").

    All tests use the real NarrativeUnitService + FakeNarrativeUnitRepository so the
    NarrativeUnitNotFoundError propagation path cannot be bypassed by a service stub.
    """

    async def test_second_delete_of_same_unit_returns_404(self) -> None:
        """DELETE twice on the same ID: first 204, second 404 (double-delete is a client error).

        Contract rationale: returning 204 for an unknown ID would mask a double-delete.
        The first delete succeeds (204); the second targets a now-absent ID and must
        surface as 404 — proving the strict semantics directly against the named bug.
        """
        repo = FakeNarrativeUnitRepository()
        real_service = NarrativeUnitService(repository=repo)
        app.dependency_overrides[get_narrative_unit_service] = lambda: real_service

        saved = await real_service.add_unit(NarrativeUnitMother.unsaved_fragment())
        assert saved.id is not None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            first = await client.delete(f"/narrative-units/{saved.id}")
            second = await client.delete(f"/narrative-units/{saved.id}")

        assert first.status_code == 204
        assert second.status_code == 404
        assert second.json()["error"] == f"Narrative unit not found: {saved.id}"

    async def test_patch_and_delete_unknown_unit_are_symmetric_404(self) -> None:
        """PATCH and DELETE on an unknown ID both return 404 (the two mutating verbs agree).

        Contract rationale: DELETE follows the same strict semantics as PATCH. The
        existing PATCH-404 router test uses a service stub; this asserts the symmetry
        through the real service + repository chain, where both verbs reach the strict
        repository and raise NarrativeUnitNotFoundError.
        """
        real_service = NarrativeUnitService(repository=FakeNarrativeUnitRepository())
        app.dependency_overrides[get_narrative_unit_service] = lambda: real_service

        unknown_id = "11111111-1111-1111-1111-111111111111"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            patch_response = await client.patch(
                f"/narrative-units/{unknown_id}",
                json={"content": "irrelevant"},
            )
            delete_response = await client.delete(f"/narrative-units/{unknown_id}")

        assert patch_response.status_code == 404
        assert delete_response.status_code == 404

    async def test_delete_unknown_unit_error_body_matches_contract_verbatim(self) -> None:
        """DELETE unknown ID returns the exact contract error body, echoing the ID.

        Contract: {"error": "Narrative unit not found: <id>"} — the ID must be echoed
        verbatim so the frontend can correlate the failure with the element it tried to
        remove. Asserts the full body, not a substring.
        """
        real_service = NarrativeUnitService(repository=FakeNarrativeUnitRepository())
        app.dependency_overrides[get_narrative_unit_service] = lambda: real_service

        unknown_id = "22222222-2222-2222-2222-222222222222"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/narrative-units/{unknown_id}")

        assert response.status_code == 404
        assert response.json() == {"error": f"Narrative unit not found: {unknown_id}"}
