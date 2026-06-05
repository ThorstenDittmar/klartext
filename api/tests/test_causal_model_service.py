"""Tests for CausalModelService.

Service-level tests use FakeCausalModelRepository and FakeConsistencyChecker
so no database or external API is involved.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import CausalModelNotFoundError, SlotNotFoundError
from api.models.causal_model import CausalModelStatus, EpistemicStatus, Polarity, SlotType
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

    assert cm.id is not None
    axiom = await service.add_axiom(
        causal_model_id=cm.id, label="A-01", description="Eine Annahme."
    )

    assert axiom.id is not None


@pytest.mark.asyncio
async def test_add_axiom_stores_label_and_description() -> None:
    """Expects the added Axiom to retain label and description."""
    service = make_service()
    cm = await service.create(title="Test")

    assert cm.id is not None
    axiom = await service.add_axiom(
        causal_model_id=cm.id, label="A-01", description="Eine Annahme."
    )

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


# ---------------------------------------------------------------------------
# add_slot
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_add_slot_returns_slot_with_id() -> None:
    """Expects add_slot to return a Slot with a non-None ID."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")

    slot = await service.add_slot(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        identifier="money_supply",
        slot_type=SlotType.PHYSICAL_QUANTITY,
    )

    assert slot.id is not None
    assert slot.identifier == "money_supply"


@pytest.mark.asyncio
async def test_service_add_slot_raises_for_unknown_model() -> None:
    """Expects CausalModelNotFoundError when the CausalModel does not exist."""
    service = make_service()

    with pytest.raises(CausalModelNotFoundError):
        await service.add_slot(
            causal_model_id="00000000-0000-0000-0000-000000000000",
            identifier="money_supply",
            slot_type=SlotType.PHYSICAL_QUANTITY,
        )


# ---------------------------------------------------------------------------
# add_relation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_add_relation_returns_relation_with_id() -> None:
    """Expects add_relation to return a CausalRelation with a non-None ID."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")
    source = await service.add_slot(cm.id, "money_supply", SlotType.PHYSICAL_QUANTITY)  # type: ignore[arg-type]
    target = await service.add_slot(cm.id, "inflation", SlotType.TREND)  # type: ignore[arg-type]

    relation = await service.add_relation(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        identifier="money_supply_causes_inflation",
        source_slot_id=source.id,  # type: ignore[arg-type]
        target_slot_id=target.id,  # type: ignore[arg-type]
    )

    assert relation.id is not None
    assert relation.identifier == "money_supply_causes_inflation"


@pytest.mark.asyncio
async def test_service_add_relation_raises_for_unknown_source_slot() -> None:
    """Expects SlotNotFoundError when source_slot_id does not exist."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")
    target = await service.add_slot(cm.id, "inflation", SlotType.TREND)  # type: ignore[arg-type]

    with pytest.raises(SlotNotFoundError):
        await service.add_relation(
            causal_model_id=cm.id,  # type: ignore[arg-type]
            identifier="unknown_causes_inflation",
            source_slot_id="00000000-0000-0000-0000-000000000000",
            target_slot_id=target.id,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# update_relation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_update_relation_changes_mechanism() -> None:
    """Expects update_relation to persist the new mechanism."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")
    source = await service.add_slot(cm.id, "money_supply", SlotType.PHYSICAL_QUANTITY)  # type: ignore[arg-type]
    target = await service.add_slot(cm.id, "inflation", SlotType.TREND)  # type: ignore[arg-type]
    rel = await service.add_relation(cm.id, "money_supply_causes_inflation", source.id, target.id)  # type: ignore[arg-type]

    updated = await service.update_relation(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        relation_id=rel.id,  # type: ignore[arg-type]
        mechanism="quantity_theory",
        polarity=Polarity.POSITIVE,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert updated.mechanism == "quantity_theory"
    assert updated.polarity == Polarity.POSITIVE


# ---------------------------------------------------------------------------
# update_slot — identifier rename
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_slot_renames_identifier() -> None:
    """Expects update_slot with a new identifier to rename the Slot."""
    service = make_service()
    cm = await service.create("Test Model")
    slot = await service.add_slot(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        identifier="old_name",
        slot_type=SlotType.PHYSICAL_QUANTITY,
        epistemic_status=EpistemicStatus.INCOMPLETE,
    )

    updated = await service.update_slot(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        slot_id=slot.id,  # type: ignore[arg-type]
        epistemic_status=EpistemicStatus.INCOMPLETE,
        identifier="new_name",
    )

    assert updated.identifier == "new_name"
