"""Tests for the Claim domain object.

A Claim is a single extractable assertion from a Scene: a piece of text
classified by type and weighted by a confidence score. Claims are provisional
– the author can confirm, reject, or reformulate them.
"""

import pytest

from api.exceptions.claim import ClaimValidationError
from api.models.claim import Claim, ClaimStatus, ClaimType

# --- ClaimStatus ---


def test_claim_status_has_draft_linked_and_unresolved() -> None:
    """Expects exactly three status values covering the claim lifecycle."""
    assert ClaimStatus.DRAFT == "draft"
    assert ClaimStatus.LINKED == "linked"
    assert ClaimStatus.UNRESOLVED == "unresolved"


# --- Happy path ---


def test_claim_create_stores_label_text_type_and_confidence() -> None:
    """Expects label and all existing fields to be accessible after creation."""
    claim = Claim.create(
        label="Inflation through money supply",
        text="Inflation entsteht durch Geldmenge.",
        typ=ClaimType.CAUSAL,
        confidence=0.9,
    )

    assert claim.label == "Inflation through money supply"
    assert claim.text == "Inflation entsteht durch Geldmenge."
    assert claim.typ == ClaimType.CAUSAL
    assert claim.confidence == 0.9


def test_claim_default_status_is_draft() -> None:
    """Expects DRAFT as the default — a newly extracted claim has no Wirkgefüge link yet."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)

    assert claim.status == ClaimStatus.DRAFT


def test_claim_has_no_wirkgefuege_ref_by_default() -> None:
    """Expects wirkgefuege_ref to be None until the author links it to a causal model element."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)

    assert claim.wirkgefuege_ref is None


def test_claim_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)

    assert claim.id is None


def test_claim_link_to_wirkgefuege_sets_status_linked() -> None:
    """Expects status to become LINKED and wirkgefuege_ref to be set after linking."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)

    claim.link_to_wirkgefuege("slot-uuid-123")

    assert claim.status == ClaimStatus.LINKED
    assert claim.wirkgefuege_ref == "slot-uuid-123"


def test_claim_mark_unresolved_sets_status_unresolved() -> None:
    """Expects status to become UNRESOLVED — the author consciously marks the gap."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)

    claim.mark_unresolved()

    assert claim.status == ClaimStatus.UNRESOLVED


def test_claim_from_record_reconstructs_claim_with_status_and_ref() -> None:
    """Expects all fields – including id, status and wirkgefuege_ref – from the database record."""
    record = {
        "id": "abc-123",
        "label": "CO2 is rising",
        "text": "Ein Claim.",
        "typ": "empirical",
        "confidence": 0.8,
        "status": "draft",
        "wirkgefuege_ref": None,
    }

    claim = Claim.from_record(record)

    assert claim.id == "abc-123"
    assert claim.label == "CO2 is rising"
    assert claim.text == "Ein Claim."
    assert claim.typ == ClaimType.EMPIRICAL
    assert claim.confidence == 0.8
    assert claim.status == ClaimStatus.DRAFT
    assert claim.wirkgefuege_ref is None


def test_claim_from_record_restores_linked_status() -> None:
    """Expects LINKED status and wirkgefuege_ref to be correctly restored from the DB record."""
    record = {
        "id": "abc-456",
        "label": "CO2 causes warming",
        "text": "Text.",
        "typ": "causal",
        "confidence": 0.9,
        "status": "linked",
        "wirkgefuege_ref": "slot-uuid-789",
    }

    claim = Claim.from_record(record)

    assert claim.status == ClaimStatus.LINKED
    assert claim.wirkgefuege_ref == "slot-uuid-789"


# --- Confidence boundaries ---


def test_claim_create_accepts_confidence_of_zero() -> None:
    """Expects 0.0 to be a valid confidence value – minimum confidence."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.0)

    assert claim.confidence == 0.0


def test_claim_create_accepts_confidence_of_one() -> None:
    """Expects 1.0 to be a valid confidence value – maximum confidence."""
    claim = Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=1.0)

    assert claim.confidence == 1.0


# --- Error cases ---


def test_claim_create_raises_for_empty_label() -> None:
    """Expects ClaimValidationError because a claim without a label cannot be identified."""
    with pytest.raises(ClaimValidationError):
        Claim.create(label="", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)


def test_claim_create_raises_for_empty_text() -> None:
    """Expects a ClaimValidationError because a Claim without text has no assertable content."""
    with pytest.raises(ClaimValidationError):
        Claim.create(label="Test", text="", typ=ClaimType.EMPIRICAL, confidence=0.8)


def test_claim_create_raises_for_whitespace_only_text() -> None:
    """Expects a ClaimValidationError because whitespace-only text is equivalent to empty."""
    with pytest.raises(ClaimValidationError):
        Claim.create(label="Test", text="   ", typ=ClaimType.EMPIRICAL, confidence=0.8)


def test_claim_create_raises_for_confidence_below_zero() -> None:
    """Expects a ClaimValidationError because confidence below 0.0 is not meaningful."""
    with pytest.raises(ClaimValidationError):
        Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=-0.1)


def test_claim_create_raises_for_confidence_above_one() -> None:
    """Expects a ClaimValidationError because confidence above 1.0 is not meaningful."""
    with pytest.raises(ClaimValidationError):
        Claim.create(label="Test", text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=1.1)


def test_claim_from_record_raises_for_unknown_typ() -> None:
    """Expects ClaimValidationError when the database record contains an unrecognised claim type."""
    record = {
        "id": "abc-123",
        "label": "Test",
        "text": "Ein Claim.",
        "typ": "unknown_type",
        "confidence": 0.8,
        "status": "draft",
        "wirkgefuege_ref": None,
    }

    with pytest.raises(ClaimValidationError):
        Claim.from_record(record)
