"""Tests for CausalModelService.

Service-level tests use FakeCausalModelRepository and FakeConsistencyChecker
so no database or external API is involved.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import CausalModelNotFoundError
from api.models.causal_model import CausalModelStatus
from api.services.causal_model_service import CausalModelService
from tests.fakes.fake_causal_model_repository import FakeCausalModelRepository
from tests.fakes.fake_consistency_checker import FakeConsistencyChecker


def make_service(
    checker: FakeConsistencyChecker | None = None,
) -> CausalModelService:
    """Builds a CausalModelService with in-memory fakes."""
    return CausalModelService(
        repository=FakeCausalModelRepository(),
        consistency_checker=checker or FakeConsistencyChecker.consistent(),
    )


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_assigns_id() -> None:
    """Expects the created CausalModel to have a non-None ID."""
    service = make_service()

    cm = await service.create(title="Klartext Wirkmodell")

    assert cm.id is not None


@pytest.mark.asyncio
async def test_create_stores_title() -> None:
    """Expects the created CausalModel to retain the given title."""
    service = make_service()

    cm = await service.create(title="Klartext Wirkmodell")

    assert cm.title == "Klartext Wirkmodell"


@pytest.mark.asyncio
async def test_create_sets_status_to_private() -> None:
    """Expects a newly created CausalModel to have status private."""
    service = make_service()

    cm = await service.create(title="Test")

    assert cm.status == CausalModelStatus.PRIVATE


# ---------------------------------------------------------------------------
# add_axiom
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_axiom_assigns_id() -> None:
    """Expects the added Axiom to have a non-None ID."""
    service = make_service()
    cm = await service.create(title="Test")

    axiom = await service.add_axiom(
        causal_model_id=cm.id, label="A-01", description="Eine Annahme."
    )  # type: ignore[arg-type]

    assert axiom.id is not None


@pytest.mark.asyncio
async def test_add_axiom_stores_label_and_description() -> None:
    """Expects the added Axiom to retain label and description."""
    service = make_service()
    cm = await service.create(title="Test")

    axiom = await service.add_axiom(
        causal_model_id=cm.id, label="A-01", description="Eine Annahme."
    )  # type: ignore[arg-type]

    assert axiom.label == "A-01"
    assert axiom.description == "Eine Annahme."


@pytest.mark.asyncio
async def test_add_axiom_raises_for_unknown_causal_model() -> None:
    """Expects CausalModelNotFoundError when the CausalModel does not exist."""
    service = make_service()

    with pytest.raises(CausalModelNotFoundError):
        await service.add_axiom(
            causal_model_id="00000000-0000-0000-0000-000000000000",
            label="A-01",
            description="Eine Annahme.",
        )


# ---------------------------------------------------------------------------
# find_by_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_by_id_returns_causal_model_with_correct_title() -> None:
    """Expects find_by_id to return the CausalModel with its title."""
    service = make_service()
    cm = await service.create(title="Klartext Wirkmodell")

    found = await service.find_by_id(cm.id)  # type: ignore[arg-type]

    assert found.title == "Klartext Wirkmodell"


@pytest.mark.asyncio
async def test_find_by_id_raises_for_unknown_causal_model() -> None:
    """Expects CausalModelNotFoundError when the CausalModel does not exist."""
    service = make_service()

    with pytest.raises(CausalModelNotFoundError):
        await service.find_by_id("00000000-0000-0000-0000-000000000000")


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all_returns_all_causal_models() -> None:
    """Expects list_all to include all created CausalModels."""
    service = make_service()
    await service.create(title="Erstes Wirkmodell")
    await service.create(title="Zweites Wirkmodell")

    all_cm = await service.list_all()

    titles = {cm.title for cm in all_cm}
    assert titles == {"Erstes Wirkmodell", "Zweites Wirkmodell"}


@pytest.mark.asyncio
async def test_list_all_returns_empty_list_when_no_models_exist() -> None:
    """Expects list_all to return an empty list when no CausalModels have been created."""
    service = make_service()

    all_cm = await service.list_all()

    assert all_cm == []


# ---------------------------------------------------------------------------
# check_consistency
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_consistency_returns_consistent_result() -> None:
    """Expects check_consistency to return consistent=True when checker reports no conflicts."""
    service = make_service(checker=FakeConsistencyChecker.consistent())
    cm = await service.create(title="Test")

    result = await service.check_consistency(causal_model_id=cm.id, scene_text="Eine Szene.")  # type: ignore[arg-type]

    assert result.consistent is True
    assert result.conflicts == []


@pytest.mark.asyncio
async def test_check_consistency_returns_conflicts_when_checker_reports_them() -> None:
    """Expects check_consistency to forward conflicts from the consistency checker."""
    service = make_service(checker=FakeConsistencyChecker.with_conflict(axiom_label="A-01"))
    cm = await service.create(title="Test")

    result = await service.check_consistency(causal_model_id=cm.id, scene_text="Eine Szene.")  # type: ignore[arg-type]

    assert result.consistent is False
    assert len(result.conflicts) == 1
    assert result.conflicts[0].axiom_label == "A-01"


@pytest.mark.asyncio
async def test_check_consistency_raises_for_unknown_causal_model() -> None:
    """Expects CausalModelNotFoundError when the CausalModel does not exist."""
    service = make_service()

    with pytest.raises(CausalModelNotFoundError):
        await service.check_consistency(
            causal_model_id="00000000-0000-0000-0000-000000000000",
            scene_text="Eine Szene.",
        )
