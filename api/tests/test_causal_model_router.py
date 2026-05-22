"""Tests for the /causal-models router."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_causal_model_service
from api.exceptions.causal_model import CausalModelNotFoundError
from api.main import app
from api.models.causal_model import Axiom, CausalModel, CausalModelStatus
from api.providers.consistency_checker import ConsistencyConflict, ConsistencyResult
from api.services.causal_model_service import CausalModelService
from tests.mothers.causal_model_mother import AxiomMother, CausalModelMother


# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeCausalModelService:
    """In-memory CausalModelService stub for router tests."""

    def __init__(self) -> None:
        self._cm = CausalModel(id="cm-001", title="Klartext Wirkmodell", status=CausalModelStatus.PRIVATE)
        self._cm.add_axiom(Axiom(id="ax-001", label="A-01", description="Eine Annahme."))

    async def create(self, title: str) -> CausalModel:
        return CausalModel(id="cm-new", title=title, status=CausalModelStatus.PRIVATE)

    async def add_axiom(self, causal_model_id: str, label: str, description: str) -> Axiom:
        if causal_model_id == "unknown":
            raise CausalModelNotFoundError("not found")
        return Axiom(id="ax-new", label=label, description=description)

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        if causal_model_id == "unknown":
            raise CausalModelNotFoundError("not found")
        return self._cm

    async def list_all(self) -> list[CausalModel]:
        return [CausalModel(id="cm-001", title="Klartext Wirkmodell", status=CausalModelStatus.PRIVATE)]

    async def check_consistency(self, causal_model_id: str, scene_text: str) -> ConsistencyResult:
        if causal_model_id == "unknown":
            raise CausalModelNotFoundError("not found")
        if "invest" in scene_text.lower():
            return ConsistencyResult(
                consistent=False,
                conflicts=[ConsistencyConflict(
                    axiom_label="A-01",
                    description="Konflikt erkannt.",
                    suggestion="Ausnahme ergänzen.",
                )],
            )
        return ConsistencyResult(consistent=True)


# ---------------------------------------------------------------------------
# Tests — POST /causal-models
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_causal_model_returns_201() -> None:
    """Expects 201 when a valid CausalModel is created."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/causal-models", json={"title": "Test Wirkmodell"})
    app.dependency_overrides.clear()
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_causal_model_returns_id_and_title() -> None:
    """Expects the response to contain id and title."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/causal-models", json={"title": "Test Wirkmodell"})
    app.dependency_overrides.clear()
    body = response.json()
    assert body["id"] == "cm-new"
    assert body["title"] == "Test Wirkmodell"


@pytest.mark.asyncio
async def test_create_causal_model_returns_422_for_empty_title() -> None:
    """Expects 422 when the title is empty."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/causal-models", json={"title": ""})
    app.dependency_overrides.clear()
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests — GET /causal-models
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_causal_models_returns_200() -> None:
    """Expects 200 and a list response."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Tests — POST /causal-models/{id}/axioms
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_axiom_returns_201() -> None:
    """Expects 201 when an Axiom is added successfully."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/axioms",
            json={"label": "A-01", "description": "Eine Annahme."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_axiom_returns_404_for_unknown_causal_model() -> None:
    """Expects 404 when the CausalModel does not exist."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/unknown/axioms",
            json={"label": "A-01", "description": "Eine Annahme."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests — POST /causal-models/{id}/check-consistency
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_consistency_returns_200() -> None:
    """Expects 200 for a valid consistency check request."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/check-consistency",
            json={"scene_text": "Eine neutrale Szene."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_consistency_returns_consistent_true_for_neutral_scene() -> None:
    """Expects consistent=true for a scene with no conflicts."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/check-consistency",
            json={"scene_text": "Eine neutrale Szene."},
        )
    app.dependency_overrides.clear()
    assert response.json()["consistent"] is True


@pytest.mark.asyncio
async def test_check_consistency_returns_conflicts_for_conflicting_scene() -> None:
    """Expects conflicts list to be non-empty when a conflict is detected."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/check-consistency",
            json={"scene_text": "Unternehmen investieren massiv nach Zinserhöhung."},
        )
    app.dependency_overrides.clear()
    body = response.json()
    assert body["consistent"] is False
    assert len(body["conflicts"]) > 0


@pytest.mark.asyncio
async def test_check_consistency_returns_404_for_unknown_causal_model() -> None:
    """Expects 404 when the CausalModel does not exist."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/unknown/check-consistency",
            json={"scene_text": "Eine Szene."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 404
