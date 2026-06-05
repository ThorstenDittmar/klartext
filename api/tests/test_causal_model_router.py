"""Tests for the /causal-models router."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_causal_model_service, get_narrative_service
from api.exceptions.causal_model import CausalModelNotFoundError
from api.main import app
from api.models.causal_model import (
    Axiom,
    CausalModel,
    CausalModelStatus,
    CausalRelation,
    EpistemicStatus,
    Polarity,
    Slot,
    SlotType,
)
from api.models.narrative import Narrative
from api.providers.consistency_checker import ConsistencyConflict, ConsistencyResult

# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeNarrativeService:
    """Minimal NarrativeService stub for causal_model router tests."""

    async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
        """Returns an empty list — no linked narratives in default stub."""
        return []


class FakeCausalModelService:
    """In-memory CausalModelService stub for router tests."""

    def __init__(self) -> None:
        self._cm = CausalModel(
            id="cm-001", title="Klartext Wirkmodell", status=CausalModelStatus.PRIVATE
        )
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
        return [
            CausalModel(id="cm-001", title="Klartext Wirkmodell", status=CausalModelStatus.PRIVATE)
        ]

    async def check_consistency(self, causal_model_id: str, scene_text: str) -> ConsistencyResult:
        if causal_model_id == "unknown":
            raise CausalModelNotFoundError("not found")
        if "invest" in scene_text.lower():
            return ConsistencyResult(
                consistent=False,
                conflicts=[
                    ConsistencyConflict(
                        axiom_label="A-01",
                        description="Konflikt erkannt.",
                        suggestion="Ausnahme ergänzen.",
                    )
                ],
            )
        return ConsistencyResult(consistent=True)

    async def add_slot(
        self,
        causal_model_id: str,
        identifier: str,
        slot_type: SlotType,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> Slot:
        """Returns a stubbed Slot. Raises CausalModelNotFoundError for unknown model."""
        if causal_model_id == "unknown":
            raise CausalModelNotFoundError("not found")
        return Slot(
            id="slot-001",
            identifier=identifier,
            slot_type=slot_type,
            epistemic_status=epistemic_status,
        )

    async def update_slot(
        self, causal_model_id: str, slot_id: str, epistemic_status: EpistemicStatus
    ) -> Slot:
        """Returns a stubbed updated Slot."""
        return Slot(
            id=slot_id,
            identifier="money_supply",
            slot_type=SlotType.PHYSICAL_QUANTITY,
            epistemic_status=epistemic_status,
        )

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """No-op for test stub."""
        pass

    async def add_relation(
        self,
        causal_model_id: str,
        identifier: str,
        source_slot_id: str,
        target_slot_id: str,
        mechanism: str | None = None,
        polarity: Polarity | None = None,
    ) -> CausalRelation:
        """Returns a stubbed CausalRelation."""
        source = Slot(id=source_slot_id, identifier="src", slot_type=SlotType.PHYSICAL_QUANTITY)
        target = Slot(id=target_slot_id, identifier="tgt", slot_type=SlotType.TREND)
        return CausalRelation(
            id="rel-001",
            identifier=identifier,
            source=source,
            target=target,
            mechanism=mechanism,
            polarity=polarity,
        )

    async def update_relation(
        self,
        causal_model_id: str,
        relation_id: str,
        mechanism: str | None,
        polarity: Polarity | None,
        epistemic_status: EpistemicStatus,
    ) -> CausalRelation:
        """Returns a stubbed updated CausalRelation."""
        source = Slot(id="slot-src", identifier="src", slot_type=SlotType.PHYSICAL_QUANTITY)
        target = Slot(id="slot-tgt", identifier="tgt", slot_type=SlotType.TREND)
        return CausalRelation(
            id=relation_id,
            identifier="money_supply_causes_inflation",
            source=source,
            target=target,
            mechanism=mechanism,
            polarity=polarity,
            epistemic_status=epistemic_status,
        )

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """No-op for test stub."""
        pass


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
# Tests — GET /causal-models/{id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_causal_model_returns_200() -> None:
    """Expects 200 when a CausalModel is found."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    app.dependency_overrides[get_narrative_service] = lambda: FakeNarrativeService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models/cm-001")
    app.dependency_overrides.clear()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_causal_model_returns_title_and_axioms() -> None:
    """Expects the response to contain the title and axioms list."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    app.dependency_overrides[get_narrative_service] = lambda: FakeNarrativeService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models/cm-001")
    app.dependency_overrides.clear()
    body = response.json()
    assert body["title"] == "Klartext Wirkmodell"
    assert len(body["axioms"]) == 1


@pytest.mark.asyncio
async def test_get_causal_model_returns_404_for_unknown_id() -> None:
    """Expects 404 when the CausalModel does not exist."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    app.dependency_overrides[get_narrative_service] = lambda: FakeNarrativeService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models/unknown")
    app.dependency_overrides.clear()
    assert response.status_code == 404


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


@pytest.mark.asyncio
async def test_add_axiom_returns_422_for_empty_label() -> None:
    """Expects 422 when the label is empty."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/axioms",
            json={"label": "", "description": "Eine Annahme."},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_axiom_returns_422_for_empty_description() -> None:
    """Expects 422 when the description is empty."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/axioms",
            json={"label": "A-01", "description": ""},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 422


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


@pytest.mark.asyncio
async def test_check_consistency_returns_422_for_empty_scene_text() -> None:
    """Expects 422 when the scene_text is empty."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/check-consistency",
            json={"scene_text": ""},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /causal-models/health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_models_health_returns_200() -> None:
    """Expects GET /causal-models/health to return HTTP 200 with status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# POST /causal-models/{id}/slots
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_slot_returns_201() -> None:
    """Expects POST /causal-models/{id}/slots to return HTTP 201."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/slots",
            json={"identifier": "money_supply", "slot_type": "physical_quantity"},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_slot_response_contains_id_and_identifier() -> None:
    """Expects the slot response to include id and identifier."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/slots",
            json={"identifier": "money_supply", "slot_type": "physical_quantity"},
        )
    app.dependency_overrides.clear()
    data = response.json()
    assert data["id"] == "slot-001"
    assert data["identifier"] == "money_supply"


# ---------------------------------------------------------------------------
# POST /causal-models/{id}/relations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_relation_returns_201() -> None:
    """Expects POST /causal-models/{id}/relations to return HTTP 201."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/relations",
            json={
                "identifier": "money_supply_causes_inflation",
                "source_slot_id": "slot-src",
                "target_slot_id": "slot-tgt",
            },
        )
    app.dependency_overrides.clear()
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# PUT /causal-models/{id}/relations/{rid}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_relation_returns_200() -> None:
    """Expects PUT /causal-models/{id}/relations/{rid} to return HTTP 200."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/causal-models/cm-001/relations/rel-001",
            json={"mechanism": "quantity_theory", "polarity": "positive"},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["mechanism"] == "quantity_theory"


# ---------------------------------------------------------------------------
# GET /causal-models/{id} — linked_narratives
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_causal_model_includes_linked_narratives_key() -> None:
    """Expects GET /causal-models/{id} response to contain a linked_narratives list."""
    app.dependency_overrides[get_causal_model_service] = lambda: FakeCausalModelService()
    app.dependency_overrides[get_narrative_service] = lambda: FakeNarrativeService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models/cm-001")
    app.dependency_overrides.clear()
    body = response.json()
    assert "linked_narratives" in body
    assert isinstance(body["linked_narratives"], list)
