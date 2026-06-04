"""Tests for Slot and EpistemicStatus domain objects.

Slot is the basic building block of the Wirkgefüge — a named placeholder
for an observable or measurable value. EpistemicStatus describes whether
an element is a set premise (AXIOMATIC) or not yet formalised (INCOMPLETE).
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import SlotValidationError
from api.models.causal_model import EpistemicStatus, Slot, SlotType

# ---------------------------------------------------------------------------
# EpistemicStatus
# ---------------------------------------------------------------------------


def test_epistemic_status_has_incomplete_and_axiomatic() -> None:
    """Expects exactly two explicit values: INCOMPLETE (default) and AXIOMATIC."""
    assert EpistemicStatus.INCOMPLETE == "incomplete"
    assert EpistemicStatus.AXIOMATIC == "axiomatic"


# ---------------------------------------------------------------------------
# SlotType
# ---------------------------------------------------------------------------


def test_slot_type_covers_expected_variants() -> None:
    """Expects at least the four basic slot types needed for the experiment scope."""
    values = {t.value for t in SlotType}

    assert "physical_quantity" in values
    assert "social_quantity" in values
    assert "entity_state" in values
    assert "trend" in values


# ---------------------------------------------------------------------------
# Slot — happy path
# ---------------------------------------------------------------------------


def test_slot_create_assigns_identifier() -> None:
    """Expects the identifier to be stored and accessible after creation."""
    slot = Slot.create(identifier="co2_concentration", slot_type=SlotType.PHYSICAL_QUANTITY)

    assert slot.identifier == "co2_concentration"


def test_slot_create_assigns_slot_type() -> None:
    """Expects the slot type to be stored and accessible after creation."""
    slot = Slot.create(identifier="co2_concentration", slot_type=SlotType.PHYSICAL_QUANTITY)

    assert slot.slot_type == SlotType.PHYSICAL_QUANTITY


def test_slot_create_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    slot = Slot.create(identifier="co2_concentration", slot_type=SlotType.PHYSICAL_QUANTITY)

    assert slot.id is None


def test_slot_default_epistemic_status_is_incomplete() -> None:
    """Expects INCOMPLETE as the default — the slot has not yet been formalised."""
    slot = Slot.create(identifier="co2_concentration", slot_type=SlotType.PHYSICAL_QUANTITY)

    assert slot.epistemic_status == EpistemicStatus.INCOMPLETE


def test_slot_can_be_created_with_axiomatic_status() -> None:
    """Expects AXIOMATIC to be accepted as an explicit epistemic status at creation."""
    slot = Slot.create(
        identifier="baseline_temperature",
        slot_type=SlotType.PHYSICAL_QUANTITY,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert slot.epistemic_status == EpistemicStatus.AXIOMATIC


def test_slot_is_axiomatic_returns_true_for_axiomatic_status() -> None:
    """Expects the is_axiomatic convenience property to return True for AXIOMATIC slots."""
    slot = Slot.create(
        identifier="baseline",
        slot_type=SlotType.PHYSICAL_QUANTITY,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert slot.is_axiomatic is True


def test_slot_is_axiomatic_returns_false_for_incomplete_status() -> None:
    """Expects is_axiomatic to return False for default INCOMPLETE slots."""
    slot = Slot.create(identifier="co2", slot_type=SlotType.PHYSICAL_QUANTITY)

    assert slot.is_axiomatic is False


def test_slot_from_record_reconstructs_all_fields() -> None:
    """Expects all fields including id and epistemic_status to be restored from a DB record."""
    record = {
        "id": "slot-001",
        "identifier": "co2_concentration",
        "slot_type": "physical_quantity",
        "epistemic_status": "incomplete",
    }

    slot = Slot.from_record(record)

    assert slot.id == "slot-001"
    assert slot.identifier == "co2_concentration"
    assert slot.slot_type == SlotType.PHYSICAL_QUANTITY
    assert slot.epistemic_status == EpistemicStatus.INCOMPLETE


def test_slot_from_record_restores_axiomatic_status() -> None:
    """Expects AXIOMATIC status to be correctly restored from a DB record."""
    record = {
        "id": "slot-002",
        "identifier": "baseline",
        "slot_type": "physical_quantity",
        "epistemic_status": "axiomatic",
    }

    slot = Slot.from_record(record)

    assert slot.epistemic_status == EpistemicStatus.AXIOMATIC
    assert slot.is_axiomatic is True


# ---------------------------------------------------------------------------
# Slot — error cases
# ---------------------------------------------------------------------------


def test_slot_create_raises_for_empty_identifier() -> None:
    """Expects SlotValidationError because a Slot without an identifier cannot be addressed."""
    with pytest.raises(SlotValidationError):
        Slot.create(identifier="", slot_type=SlotType.PHYSICAL_QUANTITY)


def test_slot_create_raises_for_whitespace_only_identifier() -> None:
    """Expects SlotValidationError because a whitespace-only identifier is equivalent to empty."""
    with pytest.raises(SlotValidationError):
        Slot.create(identifier="   ", slot_type=SlotType.PHYSICAL_QUANTITY)


def test_slot_from_record_raises_for_unknown_slot_type() -> None:
    """Expects SlotValidationError when the DB record contains an unrecognised slot_type value."""
    record = {
        "id": "slot-003",
        "identifier": "co2",
        "slot_type": "unknown_type",
        "epistemic_status": "incomplete",
    }

    with pytest.raises(SlotValidationError):
        Slot.from_record(record)


# ---------------------------------------------------------------------------
# Slot.update()
# ---------------------------------------------------------------------------


def test_slot_update_changes_epistemic_status() -> None:
    """Expects update() to change epistemic_status to AXIOMATIC."""
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)

    slot.update(epistemic_status=EpistemicStatus.AXIOMATIC)

    assert slot.epistemic_status == EpistemicStatus.AXIOMATIC


def test_slot_update_keeps_identifier_unchanged() -> None:
    """Expects update() to not change identifier."""
    slot = Slot.create(identifier="money_supply", slot_type=SlotType.PHYSICAL_QUANTITY)

    slot.update(epistemic_status=EpistemicStatus.AXIOMATIC)

    assert slot.identifier == "money_supply"
