"""Tests for CausalModel and Axiom domain objects.

A CausalModel is the formal causal model container. It holds Axioms —
axiomatic assumptions that serve as the basis for consistency checking.

An Axiom is the simplest model element: a labelled, axiomatic statement
that cannot be derived from other elements in the model.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import AxiomValidationError, CausalModelValidationError
from api.models.causal_model import Axiom, CausalModel, CausalModelStatus


# ---------------------------------------------------------------------------
# Axiom
# ---------------------------------------------------------------------------


def test_axiom_create_stores_label_and_description() -> None:
    """Expects create to store label and description as given."""
    axiom = Axiom.create(
        label="A-01",
        description="Zinserhöhungen dämpfen kurzfristig private Investitionen.",
    )

    assert axiom.label == "A-01"
    assert axiom.description == "Zinserhöhungen dämpfen kurzfristig private Investitionen."


def test_axiom_has_no_id_before_persistence() -> None:
    """Expects a newly created Axiom to have no ID before it is saved."""
    axiom = Axiom.create(label="A-01", description="Eine Annahme.")

    assert axiom.id is None


def test_axiom_create_raises_for_empty_label() -> None:
    """Expects AxiomValidationError when the label is empty."""
    with pytest.raises(AxiomValidationError):
        Axiom.create(label="", description="Eine Annahme.")


def test_axiom_create_raises_for_whitespace_only_label() -> None:
    """Expects AxiomValidationError when the label is whitespace only."""
    with pytest.raises(AxiomValidationError):
        Axiom.create(label="   ", description="Eine Annahme.")


def test_axiom_create_raises_for_empty_description() -> None:
    """Expects AxiomValidationError when the description is empty."""
    with pytest.raises(AxiomValidationError):
        Axiom.create(label="A-01", description="")


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
    assert axiom.description == "Eine Annahme."


# ---------------------------------------------------------------------------
# CausalModel
# ---------------------------------------------------------------------------


def test_causal_model_create_stores_title() -> None:
    """Expects create to store the given title."""
    cm = CausalModel.create(title="Klartext Wirkmodell")

    assert cm.title == "Klartext Wirkmodell"


def test_causal_model_create_sets_default_status_to_private() -> None:
    """Expects a new CausalModel to start with status 'private'."""
    cm = CausalModel.create(title="Test")

    assert cm.status == CausalModelStatus.PRIVATE


def test_causal_model_has_no_id_before_persistence() -> None:
    """Expects a newly created CausalModel to have no ID before it is saved."""
    cm = CausalModel.create(title="Test")

    assert cm.id is None


def test_causal_model_create_raises_for_empty_title() -> None:
    """Expects CausalModelValidationError when the title is empty."""
    with pytest.raises(CausalModelValidationError):
        CausalModel.create(title="")


def test_causal_model_create_raises_for_whitespace_only_title() -> None:
    """Expects CausalModelValidationError when the title is whitespace only."""
    with pytest.raises(CausalModelValidationError):
        CausalModel.create(title="   ")


def test_causal_model_starts_with_no_axioms() -> None:
    """Expects a new CausalModel to have an empty axioms list."""
    cm = CausalModel.create(title="Test")

    assert cm.axioms == []


def test_causal_model_add_axiom_appends_axiom() -> None:
    """Expects add_axiom to append the Axiom to the CausalModel."""
    cm = CausalModel.create(title="Test")
    axiom = Axiom.create(label="A-01", description="Eine Annahme.")

    cm.add_axiom(axiom)

    assert len(cm.axioms) == 1
    assert cm.axioms[0].label == "A-01"


def test_causal_model_add_axiom_preserves_order() -> None:
    """Expects axioms to appear in the order they were added."""
    cm = CausalModel.create(title="Test")
    cm.add_axiom(Axiom.create(label="A-01", description="Erste Annahme."))
    cm.add_axiom(Axiom.create(label="A-02", description="Zweite Annahme."))

    assert cm.axioms[0].label == "A-01"
    assert cm.axioms[1].label == "A-02"


def test_causal_model_from_record_reconstructs_causal_model() -> None:
    """Expects from_record to reconstruct a persisted CausalModel with its ID."""
    record = {"id": "cm-123", "title": "Klartext Wirkmodell", "status": "privat"}

    cm = CausalModel.from_record(record)

    assert cm.id == "cm-123"
    assert cm.title == "Klartext Wirkmodell"
    assert cm.status == CausalModelStatus.PRIVATE
