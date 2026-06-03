"""Tests for CausalRelation domain object.

A CausalRelation describes a directed causal link between two Slots:
if the source Slot is in a given condition, the target Slot shows a
given effect — mediated by an optional mechanism.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import CausalRelationValidationError
from api.models.causal_model import CausalRelation, EpistemicStatus

# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_causal_relation_create_assigns_identifier() -> None:
    """Expects the identifier to be stored and accessible after creation."""
    relation = CausalRelation.create(
        identifier="co2_causes_warming",
        source_slot_id="slot-co2",
        source_condition="high",
        target_slot_id="slot-temp",
        target_effect="rising",
    )

    assert relation.identifier == "co2_causes_warming"


def test_causal_relation_create_assigns_source_and_target() -> None:
    """Expects source_slot_id, source_condition, target_slot_id, target_effect to be stored."""
    relation = CausalRelation.create(
        identifier="r1",
        source_slot_id="slot-co2",
        source_condition="high",
        target_slot_id="slot-temp",
        target_effect="rising",
    )

    assert relation.source_slot_id == "slot-co2"
    assert relation.source_condition == "high"
    assert relation.target_slot_id == "slot-temp"
    assert relation.target_effect == "rising"


def test_causal_relation_create_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    relation = CausalRelation.create(
        identifier="r1",
        source_slot_id="s1",
        source_condition="x",
        target_slot_id="s2",
        target_effect="y",
    )

    assert relation.id is None


def test_causal_relation_default_epistemic_status_is_incomplete() -> None:
    """Expects INCOMPLETE as the default — the relation has not yet been formalised."""
    relation = CausalRelation.create(
        identifier="r1",
        source_slot_id="s1",
        source_condition="x",
        target_slot_id="s2",
        target_effect="y",
    )

    assert relation.epistemic_status == EpistemicStatus.INCOMPLETE


def test_causal_relation_can_be_created_with_axiomatic_status() -> None:
    """Expects AXIOMATIC to be accepted as an explicit epistemic status at creation."""
    relation = CausalRelation.create(
        identifier="r1",
        source_slot_id="s1",
        source_condition="x",
        target_slot_id="s2",
        target_effect="y",
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert relation.epistemic_status == EpistemicStatus.AXIOMATIC


def test_causal_relation_mechanism_defaults_to_none() -> None:
    """Expects mechanism to be None when not provided — it is an optional attribution."""
    relation = CausalRelation.create(
        identifier="r1",
        source_slot_id="s1",
        source_condition="x",
        target_slot_id="s2",
        target_effect="y",
    )

    assert relation.mechanism is None


def test_causal_relation_create_stores_mechanism() -> None:
    """Expects mechanism to be stored when provided."""
    relation = CausalRelation.create(
        identifier="r1",
        source_slot_id="s1",
        source_condition="high",
        target_slot_id="s2",
        target_effect="rising",
        mechanism="Greenhouse effect",
    )

    assert relation.mechanism == "Greenhouse effect"


def test_causal_relation_from_record_reconstructs_all_fields() -> None:
    """Expects all fields including id to be restored from a DB record."""
    record = {
        "id": "cr-001",
        "identifier": "co2_causes_warming",
        "source_slot_id": "slot-co2",
        "source_condition": "high",
        "target_slot_id": "slot-temp",
        "target_effect": "rising",
        "mechanism": "Greenhouse effect",
        "epistemic_status": "incomplete",
    }

    relation = CausalRelation.from_record(record)

    assert relation.id == "cr-001"
    assert relation.identifier == "co2_causes_warming"
    assert relation.source_slot_id == "slot-co2"
    assert relation.source_condition == "high"
    assert relation.target_slot_id == "slot-temp"
    assert relation.target_effect == "rising"
    assert relation.mechanism == "Greenhouse effect"
    assert relation.epistemic_status == EpistemicStatus.INCOMPLETE


def test_causal_relation_from_record_handles_null_mechanism() -> None:
    """Expects mechanism to be None when the DB record contains null."""
    record = {
        "id": "cr-002",
        "identifier": "r1",
        "source_slot_id": "s1",
        "source_condition": "x",
        "target_slot_id": "s2",
        "target_effect": "y",
        "mechanism": None,
        "epistemic_status": "incomplete",
    }

    relation = CausalRelation.from_record(record)

    assert relation.mechanism is None


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_causal_relation_create_raises_for_empty_identifier() -> None:
    """Expects CausalRelationValidationError when identifier is empty."""
    with pytest.raises(CausalRelationValidationError):
        CausalRelation.create(
            identifier="",
            source_slot_id="s1",
            source_condition="x",
            target_slot_id="s2",
            target_effect="y",
        )


def test_causal_relation_create_raises_when_source_equals_target() -> None:
    """Expects CausalRelationValidationError — a slot cannot cause itself."""
    with pytest.raises(CausalRelationValidationError):
        CausalRelation.create(
            identifier="self_loop",
            source_slot_id="same-slot",
            source_condition="x",
            target_slot_id="same-slot",
            target_effect="y",
        )
