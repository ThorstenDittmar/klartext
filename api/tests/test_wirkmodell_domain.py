"""Tests for Wirkmodell and Axiom domain objects.

A Wirkmodell is the formal causal model container. It holds Axiome —
axiomatic assumptions that serve as the basis for consistency checking.

An Axiom is the simplest Modellelement: a labelled, axiomatic statement
that cannot be derived from other elements in the model.
"""

from __future__ import annotations

import pytest

from api.exceptions.wirkmodell import AxiomValidationError, WirkmodellValidationError
from api.models.wirkmodell import Axiom, Wirkmodell, WirkmodellStatus


# ---------------------------------------------------------------------------
# Axiom
# ---------------------------------------------------------------------------


def test_axiom_create_stores_label_and_beschreibung() -> None:
    """Expects create to store label and beschreibung as given."""
    axiom = Axiom.create(
        label="A-01",
        beschreibung="Zinserhöhungen dämpfen kurzfristig private Investitionen.",
    )

    assert axiom.label == "A-01"
    assert axiom.beschreibung == "Zinserhöhungen dämpfen kurzfristig private Investitionen."


def test_axiom_has_no_id_before_persistence() -> None:
    """Expects a newly created Axiom to have no ID before it is saved."""
    axiom = Axiom.create(label="A-01", beschreibung="Eine Annahme.")

    assert axiom.id is None


def test_axiom_create_raises_for_empty_label() -> None:
    """Expects AxiomValidationError when the label is empty."""
    with pytest.raises(AxiomValidationError):
        Axiom.create(label="", beschreibung="Eine Annahme.")


def test_axiom_create_raises_for_whitespace_only_label() -> None:
    """Expects AxiomValidationError when the label is whitespace only."""
    with pytest.raises(AxiomValidationError):
        Axiom.create(label="   ", beschreibung="Eine Annahme.")


def test_axiom_create_raises_for_empty_beschreibung() -> None:
    """Expects AxiomValidationError when the beschreibung is empty."""
    with pytest.raises(AxiomValidationError):
        Axiom.create(label="A-01", beschreibung="")


def test_axiom_from_record_reconstructs_axiom() -> None:
    """Expects from_record to reconstruct a persisted Axiom with its ID."""
    record = {
        "id": "abc-123",
        "label": "A-01",
        "beschreibung": "Eine Annahme.",
    }

    axiom = Axiom.from_record(record)

    assert axiom.id == "abc-123"
    assert axiom.label == "A-01"
    assert axiom.beschreibung == "Eine Annahme."


# ---------------------------------------------------------------------------
# Wirkmodell
# ---------------------------------------------------------------------------


def test_wirkmodell_create_stores_titel() -> None:
    """Expects create to store the given titel."""
    wm = Wirkmodell.create(titel="Klartext Wirkmodell")

    assert wm.titel == "Klartext Wirkmodell"


def test_wirkmodell_create_sets_default_status_to_privat() -> None:
    """Expects a new Wirkmodell to start with status 'privat'."""
    wm = Wirkmodell.create(titel="Test")

    assert wm.status == WirkmodellStatus.PRIVAT


def test_wirkmodell_has_no_id_before_persistence() -> None:
    """Expects a newly created Wirkmodell to have no ID before it is saved."""
    wm = Wirkmodell.create(titel="Test")

    assert wm.id is None


def test_wirkmodell_create_raises_for_empty_titel() -> None:
    """Expects WirkmodellValidationError when the titel is empty."""
    with pytest.raises(WirkmodellValidationError):
        Wirkmodell.create(titel="")


def test_wirkmodell_create_raises_for_whitespace_only_titel() -> None:
    """Expects WirkmodellValidationError when the titel is whitespace only."""
    with pytest.raises(WirkmodellValidationError):
        Wirkmodell.create(titel="   ")


def test_wirkmodell_starts_with_no_axiome() -> None:
    """Expects a new Wirkmodell to have an empty axiome list."""
    wm = Wirkmodell.create(titel="Test")

    assert wm.axiome == []


def test_wirkmodell_add_axiom_appends_axiom() -> None:
    """Expects add_axiom to append the Axiom to the Wirkmodell."""
    wm = Wirkmodell.create(titel="Test")
    axiom = Axiom.create(label="A-01", beschreibung="Eine Annahme.")

    wm.add_axiom(axiom)

    assert len(wm.axiome) == 1
    assert wm.axiome[0].label == "A-01"


def test_wirkmodell_add_axiom_preserves_order() -> None:
    """Expects axiome to appear in the order they were added."""
    wm = Wirkmodell.create(titel="Test")
    wm.add_axiom(Axiom.create(label="A-01", beschreibung="Erste Annahme."))
    wm.add_axiom(Axiom.create(label="A-02", beschreibung="Zweite Annahme."))

    assert wm.axiome[0].label == "A-01"
    assert wm.axiome[1].label == "A-02"


def test_wirkmodell_from_record_reconstructs_wirkmodell() -> None:
    """Expects from_record to reconstruct a persisted Wirkmodell with its ID."""
    record = {"id": "wm-123", "titel": "Klartext Wirkmodell", "status": "privat"}

    wm = Wirkmodell.from_record(record)

    assert wm.id == "wm-123"
    assert wm.titel == "Klartext Wirkmodell"
    assert wm.status == WirkmodellStatus.PRIVAT
