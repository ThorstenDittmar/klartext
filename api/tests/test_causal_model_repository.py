"""Tests for the CausalModelRepository contract.

All unit tests run against FakeCausalModelRepository.
The SupabaseCausalModelRepository must satisfy the same contract;
those tests are marked @pytest.mark.integration.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import CausalModelNotFoundError
from api.models.causal_model import CausalRelation, EpistemicStatus, Polarity, Slot, SlotType
from tests.fakes.fake_causal_model_repository import FakeCausalModelRepository
from tests.mothers.causal_model_mother import AxiomMother, CausalModelMother


@pytest.mark.asyncio
async def test_causal_model_repository_save_assigns_id() -> None:
    """Expects the saved CausalModel to have a non-None ID."""
    repo = FakeCausalModelRepository()

    saved = await repo.save(CausalModelMother.empty())

    assert saved.id is not None


@pytest.mark.asyncio
async def test_causal_model_repository_save_preserves_title() -> None:
    """Expects the saved CausalModel to retain its title."""
    repo = FakeCausalModelRepository()

    saved = await repo.save(CausalModelMother.empty())

    assert saved.title == "Klartext Wirkmodell"


@pytest.mark.asyncio
async def test_causal_model_repository_save_assigns_ids_to_axioms() -> None:
    """Expects all axioms of the saved CausalModel to have IDs."""
    repo = FakeCausalModelRepository()

    saved = await repo.save(CausalModelMother.with_axioms())

    assert all(a.id is not None for a in saved.axioms)


@pytest.mark.asyncio
async def test_causal_model_repository_add_axiom_assigns_id() -> None:
    """Expects add_axiom to return the Axiom with a non-None ID."""
    repo = FakeCausalModelRepository()
    saved_cm = await repo.save(CausalModelMother.empty())

    saved_axiom = await repo.add_axiom(saved_cm.id, AxiomMother.interest_rate())  # type: ignore[arg-type]

    assert saved_axiom.id is not None


@pytest.mark.asyncio
async def test_causal_model_repository_add_axiom_makes_it_retrievable() -> None:
    """Expects added Axiom to appear in find_by_id result."""
    repo = FakeCausalModelRepository()
    saved_cm = await repo.save(CausalModelMother.empty())
    await repo.add_axiom(saved_cm.id, AxiomMother.interest_rate())  # type: ignore[arg-type]

    found = await repo.find_by_id(saved_cm.id)  # type: ignore[arg-type]

    assert len(found.axioms) == 1
    assert found.axioms[0].label == "A-01"


@pytest.mark.asyncio
async def test_causal_model_repository_find_by_id_returns_causal_model_with_axioms() -> None:
    """Expects find_by_id to return the CausalModel with all its Axioms."""
    repo = FakeCausalModelRepository()
    saved = await repo.save(CausalModelMother.with_axioms())

    found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.title == "Klartext Wirkmodell"
    assert len(found.axioms) == 3


@pytest.mark.asyncio
async def test_causal_model_repository_list_all_returns_all() -> None:
    """Expects list_all to include every saved CausalModel."""
    repo = FakeCausalModelRepository()
    for cm in CausalModelMother.collection():
        await repo.save(cm)

    all_cm = await repo.list_all()

    titles = {cm.title for cm in all_cm}
    assert titles == {"Erstes Wirkmodell", "Zweites Wirkmodell", "Drittes Wirkmodell"}


@pytest.mark.asyncio
async def test_causal_model_repository_find_by_id_raises_for_unknown_id() -> None:
    """Expects CausalModelNotFoundError when no CausalModel exists for the given ID."""
    repo = FakeCausalModelRepository()

    with pytest.raises(CausalModelNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_causal_model_repository_add_axiom_raises_for_unknown_id() -> None:
    """Expects CausalModelNotFoundError when adding an Axiom to a non-existent CausalModel."""
    repo = FakeCausalModelRepository()

    with pytest.raises(CausalModelNotFoundError):
        await repo.add_axiom("00000000-0000-0000-0000-000000000000", AxiomMother.interest_rate())


@pytest.mark.asyncio
async def test_causal_model_repository_list_all_returns_empty_list_when_empty() -> None:
    """Expects list_all to return an empty list when no CausalModels have been saved."""
    repo = FakeCausalModelRepository()

    result = await repo.list_all()

    assert result == []


# ---------------------------------------------------------------------------
# Slot repository contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_slot_repository_add_slot_assigns_id() -> None:
    """Expects add_slot to return the Slot with a non-None ID."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)

    saved = await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]

    assert saved.id is not None


@pytest.mark.asyncio
async def test_slot_repository_add_slot_makes_it_retrievable() -> None:
    """Expects find_slots_by_model_id to return the added Slot."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)
    await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]

    found = await repo.find_slots_by_model_id(cm.id)  # type: ignore[arg-type]

    assert len(found) == 1
    assert found[0].identifier == "money_supply"


@pytest.mark.asyncio
async def test_slot_repository_update_slot_persists_epistemic_status() -> None:
    """Expects update_slot to persist the changed epistemic_status."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)
    saved = await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]
    saved.update(epistemic_status=EpistemicStatus.AXIOMATIC)

    await repo.update_slot(saved)

    found = await repo.find_slots_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found[0].epistemic_status == EpistemicStatus.AXIOMATIC


@pytest.mark.asyncio
async def test_slot_repository_remove_slot_deletes_it() -> None:
    """Expects remove_slot to make the Slot no longer retrievable."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)
    saved = await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]

    await repo.remove_slot(cm.id, saved.id)  # type: ignore[arg-type]

    found = await repo.find_slots_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found == []


@pytest.mark.asyncio
async def test_slot_repository_add_slot_raises_for_unknown_model() -> None:
    """Expects CausalModelNotFoundError when adding a Slot to a non-existent CausalModel."""
    repo = FakeCausalModelRepository()
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)

    with pytest.raises(CausalModelNotFoundError):
        await repo.add_slot("00000000-0000-0000-0000-000000000000", slot)


# ---------------------------------------------------------------------------
# CausalRelation repository contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_relation_repository_add_relation_assigns_id() -> None:
    """Expects add_relation to return the CausalRelation with a non-None ID."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("money_supply", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    relation = CausalRelation.create(
        identifier="money_supply_causes_inflation", source=source, target=target
    )

    saved = await repo.add_relation(cm.id, relation)  # type: ignore[arg-type]

    assert saved.id is not None


@pytest.mark.asyncio
async def test_relation_repository_add_relation_makes_it_retrievable() -> None:
    """Expects find_relations_by_model_id to return the added CausalRelation."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("money_supply", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    relation = CausalRelation.create("money_supply_causes_inflation", source=source, target=target)
    await repo.add_relation(cm.id, relation)  # type: ignore[arg-type]

    found = await repo.find_relations_by_model_id(cm.id)  # type: ignore[arg-type]

    assert len(found) == 1
    assert found[0].identifier == "money_supply_causes_inflation"


@pytest.mark.asyncio
async def test_relation_repository_update_relation_persists_mechanism() -> None:
    """Expects update_relation to persist mechanism and polarity changes."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("money_supply", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    saved = await repo.add_relation(  # type: ignore[arg-type]
        cm.id,
        CausalRelation.create("money_supply_causes_inflation", source=source, target=target),
    )
    saved.update(
        mechanism="quantity_theory",
        polarity=Polarity.POSITIVE,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    await repo.update_relation(saved)

    found = await repo.find_relations_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found[0].mechanism == "quantity_theory"


@pytest.mark.asyncio
async def test_relation_repository_remove_relation_deletes_it() -> None:
    """Expects remove_relation to make the CausalRelation no longer retrievable."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("money_supply", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    saved = await repo.add_relation(  # type: ignore[arg-type]
        cm.id,
        CausalRelation.create("money_supply_causes_inflation", source=source, target=target),
    )

    await repo.remove_relation(cm.id, saved.id)  # type: ignore[arg-type]

    found = await repo.find_relations_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found == []


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_causal_model_repository_save_and_find_by_id() -> None:
    """Calls the real database. Expects save to persist a CausalModel retrievable by ID.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_causal_model_repository import SupabaseCausalModelRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseCausalModelRepository(client=client)
    cm = CausalModelMother.with_axioms()

    saved = await repo.save(cm)
    try:
        found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

        assert found.title == "Klartext Wirkmodell"
        assert len(found.axioms) == 3
    finally:
        await client.table("modellelemente").delete().eq("wirkmodell_id", saved.id).execute()
        await client.table("wirkmodelle").delete().eq("id", saved.id).execute()
