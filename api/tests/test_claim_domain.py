"""Tests for the Claim domain object.

A Claim is a single extractable assertion from a Scene: a piece of text
classified by type and weighted by a confidence score. Claims are provisional
– the author can confirm, reject, or reformulate them.
"""

import pytest

from api.exceptions.claim import ClaimValidationError
from api.models.claim import Claim, ClaimType


# --- Happy path ---


def test_claim_create_stores_text_type_and_confidence() -> None:
    """Expects all three fields to be accessible after creation."""
    claim = Claim.create(text="Inflation entsteht durch Geldmenge.", typ=ClaimType.CAUSAL, confidence=0.9)

    assert claim.text == "Inflation entsteht durch Geldmenge."
    assert claim.typ == ClaimType.CAUSAL
    assert claim.confidence == 0.9


def test_claim_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    claim = Claim.create(text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.8)

    assert claim.id is None


def test_claim_from_record_reconstructs_claim() -> None:
    """Expects all fields – including the persisted id – to be restored from the database record."""
    record = {"id": "abc-123", "text": "Ein Claim.", "typ": "empirischer_claim", "confidence": 0.8}

    claim = Claim.from_record(record)

    assert claim.id == "abc-123"
    assert claim.text == "Ein Claim."
    assert claim.typ == ClaimType.EMPIRICAL
    assert claim.confidence == 0.8


# --- Confidence boundaries ---


def test_claim_create_accepts_confidence_of_zero() -> None:
    """Expects 0.0 to be a valid confidence value – minimum confidence."""
    claim = Claim.create(text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=0.0)

    assert claim.confidence == 0.0


def test_claim_create_accepts_confidence_of_one() -> None:
    """Expects 1.0 to be a valid confidence value – maximum confidence."""
    claim = Claim.create(text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=1.0)

    assert claim.confidence == 1.0


# --- Error cases ---


def test_claim_create_raises_for_empty_text() -> None:
    """Expects a ClaimValidationError because a Claim without text has no assertable content."""
    with pytest.raises(ClaimValidationError):
        Claim.create(text="", typ=ClaimType.EMPIRICAL, confidence=0.8)


def test_claim_create_raises_for_whitespace_only_text() -> None:
    """Expects a ClaimValidationError because whitespace-only text is equivalent to empty."""
    with pytest.raises(ClaimValidationError):
        Claim.create(text="   ", typ=ClaimType.EMPIRICAL, confidence=0.8)


def test_claim_create_raises_for_confidence_below_zero() -> None:
    """Expects a ClaimValidationError because confidence below 0.0 is not meaningful."""
    with pytest.raises(ClaimValidationError):
        Claim.create(text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=-0.1)


def test_claim_create_raises_for_confidence_above_one() -> None:
    """Expects a ClaimValidationError because confidence above 1.0 is not meaningful."""
    with pytest.raises(ClaimValidationError):
        Claim.create(text="Ein Claim.", typ=ClaimType.EMPIRICAL, confidence=1.1)


def test_claim_from_record_raises_for_unknown_typ() -> None:
    """Expects a ClaimValidationError when the database record contains an unrecognised claim type."""
    record = {"id": "abc-123", "text": "Ein Claim.", "typ": "unbekannter_claim", "confidence": 0.8}

    with pytest.raises(ClaimValidationError):
        Claim.from_record(record)
