"""Tests for the /wirkmodelle router."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_wirkmodell_service
from api.exceptions.wirkmodell import WirkmodellNotFoundError
from api.main import app
from api.models.wirkmodell import Axiom, Wirkmodell, WirkmodellStatus
from api.providers.konsistenz_checker import KonsistenzKonflikt, KonsistenzResult
from api.services.wirkmodell_service import WirkmodellService
from tests.mothers.wirkmodell_mother import AxiomMother, WirkmodellMother


# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeWirkmodellService:
    """In-memory WirkmodellService stub for router tests."""

    def __init__(self) -> None:
        self._wm = Wirkmodell(id="wm-001", titel="Klartext Wirkmodell", status=WirkmodellStatus.PRIVAT)
        self._wm.add_axiom(Axiom(id="ax-001", label="A-01", beschreibung="Eine Annahme."))

    async def create(self, titel: str) -> Wirkmodell:
        return Wirkmodell(id="wm-new", titel=titel, status=WirkmodellStatus.PRIVAT)

    async def add_axiom(self, wirkmodell_id: str, label: str, beschreibung: str) -> Axiom:
        if wirkmodell_id == "unknown":
            raise WirkmodellNotFoundError("not found")
        return Axiom(id="ax-new", label=label, beschreibung=beschreibung)

    async def find_by_id(self, wirkmodell_id: str) -> Wirkmodell:
        if wirkmodell_id == "unknown":
            raise WirkmodellNotFoundError("not found")
        return self._wm

    async def list_all(self) -> list[Wirkmodell]:
        return [Wirkmodell(id="wm-001", titel="Klartext Wirkmodell", status=WirkmodellStatus.PRIVAT)]

    async def check_consistency(self, wirkmodell_id: str, szenen_text: str) -> KonsistenzResult:
        if wirkmodell_id == "unknown":
            raise WirkmodellNotFoundError("not found")
        if "invest" in szenen_text.lower():
            return KonsistenzResult(
                konsistent=False,
                konflikte=[KonsistenzKonflikt(
                    axiom_label="A-01",
                    beschreibung="Konflikt erkannt.",
                    vorschlag="Ausnahme ergänzen.",
                )],
            )
        return KonsistenzResult(konsistent=True)


# ---------------------------------------------------------------------------
# Tests — POST /wirkmodelle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_wirkmodell_returns_201() -> None:
    """Expects 201 when a valid Wirkmodell is created."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/wirkmodelle", json={"titel": "Test Wirkmodell"})
    app.dependency_overrides.clear()
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_wirkmodell_returns_id_and_titel() -> None:
    """Expects the response to contain id and titel."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/wirkmodelle", json={"titel": "Test Wirkmodell"})
    app.dependency_overrides.clear()
    body = response.json()
    assert body["id"] == "wm-new"
    assert body["titel"] == "Test Wirkmodell"


@pytest.mark.asyncio
async def test_create_wirkmodell_returns_422_for_empty_titel() -> None:
    """Expects 422 when the titel is empty."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/wirkmodelle", json={"titel": ""})
    app.dependency_overrides.clear()
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests — GET /wirkmodelle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_wirkmodelle_returns_200() -> None:
    """Expects 200 and a list response."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/wirkmodelle")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Tests — POST /wirkmodelle/{id}/axiome
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_axiom_returns_201() -> None:
    """Expects 201 when an Axiom is added successfully."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/wirkmodelle/wm-001/axiome",
            json={"label": "A-01", "beschreibung": "Eine Annahme."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_axiom_returns_404_for_unknown_wirkmodell() -> None:
    """Expects 404 when the Wirkmodell does not exist."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/wirkmodelle/unknown/axiome",
            json={"label": "A-01", "beschreibung": "Eine Annahme."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests — POST /wirkmodelle/{id}/check-consistency
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_consistency_returns_200() -> None:
    """Expects 200 for a valid consistency check request."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/wirkmodelle/wm-001/check-consistency",
            json={"szenen_text": "Eine neutrale Szene."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_consistency_returns_konsistent_true_for_neutral_scene() -> None:
    """Expects konsistent=true for a scene with no conflicts."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/wirkmodelle/wm-001/check-consistency",
            json={"szenen_text": "Eine neutrale Szene."},
        )
    app.dependency_overrides.clear()
    assert response.json()["konsistent"] is True


@pytest.mark.asyncio
async def test_check_consistency_returns_konflikte_for_conflicting_scene() -> None:
    """Expects konflikte list to be non-empty when a conflict is detected."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/wirkmodelle/wm-001/check-consistency",
            json={"szenen_text": "Unternehmen investieren massiv nach Zinserhöhung."},
        )
    app.dependency_overrides.clear()
    body = response.json()
    assert body["konsistent"] is False
    assert len(body["konflikte"]) > 0


@pytest.mark.asyncio
async def test_check_consistency_returns_404_for_unknown_wirkmodell() -> None:
    """Expects 404 when the Wirkmodell does not exist."""
    app.dependency_overrides[get_wirkmodell_service] = lambda: FakeWirkmodellService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/wirkmodelle/unknown/check-consistency",
            json={"szenen_text": "Eine Szene."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 404
