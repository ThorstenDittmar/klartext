"""Tests for CausalRelation domain object (persistence-layer representation).

CausalRelation stores references to actual Slot objects. These tests verify
that the basic persistence attributes (id, identifier, epistemic_status) and
factory methods work correctly. Composition behaviour is tested in
test_causal_model_composition.py.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import CausalRelationValidationError
from api.models.causal_model import CausalRelation, EpistemicStatus, Polarity, Slot, SlotType


def _slot(identifier: str) -> Slot:
    return Slot.create(identifier=identifier, slot_type=SlotType.PHYSICAL_QUANTITY)


def test_causal_relation_create_assigns_identifier() -> None:
    """Expects the identifier to be stored and accessible after creation."""
    relation = CausalRelation.create(
        identifier="co2_causes_warming",
        source=_slot("co2"),
        target=_slot("temperature"),
    )

    assert relation.identifier == "co2_causes_warming"


def test_causal_relation_create_assigns_source_and_target() -> None:
    """Expects source and target Slot objects to be stored by reference."""
    source = _slot("co2")
    target = _slot("temperature")
    relation = CausalRelation.create(identifier="r1", source=source, target=target)

    assert relation.source is source
    assert relation.target is target


def test_causal_relation_create_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    relation = CausalRelation.create(identifier="r1", source=_slot("a"), target=_slot("b"))

    assert relation.id is None


def test_causal_relation_default_epistemic_status_is_incomplete() -> None:
    """Expects INCOMPLETE as the default — the relation has not yet been formalised."""
    relation = CausalRelation.create(identifier="r1", source=_slot("a"), target=_slot("b"))

    assert relation.epistemic_status == EpistemicStatus.INCOMPLETE


def test_causal_relation_can_be_created_with_axiomatic_status() -> None:
    """Expects AXIOMATIC to be accepted as an explicit epistemic status at creation."""
    relation = CausalRelation.create(
        identifier="r1",
        source=_slot("a"),
        target=_slot("b"),
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert relation.epistemic_status == EpistemicStatus.AXIOMATIC


def test_causal_relation_mechanism_defaults_to_none() -> None:
    """Expects mechanism to be None when not provided."""
    relation = CausalRelation.create(identifier="r1", source=_slot("a"), target=_slot("b"))

    assert relation.mechanism is None


def test_causal_relation_create_stores_mechanism() -> None:
    """Expects mechanism to be stored when provided."""
    relation = CausalRelation.create(
        identifier="r1",
        source=_slot("a"),
        target=_slot("b"),
        mechanism="Greenhouse effect",
    )

    assert relation.mechanism == "Greenhouse effect"


def test_causal_relation_from_record_reconstructs_all_fields() -> None:
    """Expects all fields including id to be restored when given actual Slot objects."""
    source = _slot("co2")
    target = _slot("temperature")
    record = {
        "id": "cr-001",
        "identifier": "co2_causes_warming",
        "source": source,
        "target": target,
        "mechanism": "Greenhouse effect",
        "epistemic_status": "incomplete",
    }

    relation = CausalRelation.from_record(record)

    assert relation.id == "cr-001"
    assert relation.identifier == "co2_causes_warming"
    assert relation.source is source
    assert relation.mechanism == "Greenhouse effect"
    assert relation.epistemic_status == EpistemicStatus.INCOMPLETE


def test_causal_relation_from_record_handles_null_mechanism() -> None:
    """Expects mechanism to be None when the record contains null."""
    record = {
        "id": "cr-002",
        "identifier": "r1",
        "source": _slot("a"),
        "target": _slot("b"),
        "mechanism": None,
        "epistemic_status": "incomplete",
    }

    relation = CausalRelation.from_record(record)

    assert relation.mechanism is None


def test_causal_relation_create_raises_for_empty_identifier() -> None:
    """Expects CausalRelationValidationError when identifier is empty."""
    with pytest.raises(CausalRelationValidationError):
        CausalRelation.create(identifier="", source=_slot("a"), target=_slot("b"))


def test_causal_relation_create_raises_when_source_equals_target() -> None:
    """Expects CausalRelationValidationError — a slot cannot cause itself."""
    slot = _slot("same")
    with pytest.raises(CausalRelationValidationError):
        CausalRelation.create(identifier="self_loop", source=slot, target=slot)


# ---------------------------------------------------------------------------
# CausalRelation.update()
# ---------------------------------------------------------------------------


def test_causal_relation_update_changes_mechanism_and_polarity() -> None:
    """Expects update() to change mechanism, polarity and epistemic_status."""
    source = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    target = Slot.create(identifier="inflation", slot_type=SlotType.TREND)
    rel = CausalRelation.create(identifier="geldmenge→inflation", source=source, target=target)

    rel.update(
        mechanism="Quantitätstheorie",
        polarity=Polarity.POSITIVE,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert rel.mechanism == "Quantitätstheorie"
    assert rel.polarity == Polarity.POSITIVE
    assert rel.epistemic_status == EpistemicStatus.AXIOMATIC


def test_causal_relation_update_can_clear_mechanism() -> None:
    """Expects update() to accept None as mechanism."""
    source = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    target = Slot.create(identifier="inflation", slot_type=SlotType.TREND)
    rel = CausalRelation.create(
        identifier="geldmenge→inflation", source=source, target=target, mechanism="old"
    )

    rel.update(mechanism=None, polarity=None, epistemic_status=EpistemicStatus.INCOMPLETE)

    assert rel.mechanism is None
