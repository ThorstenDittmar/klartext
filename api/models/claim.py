"""Domain objects for claims extracted from narrative scenes."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from api.exceptions.claim import ClaimValidationError


class ClaimType(StrEnum):
    """The epistemic type of a claim.

    Values are stored in the database and passed to the Claude API prompt.
    """

    EMPIRICAL = "empirical"
    CAUSAL = "causal"
    DEFINITIONAL = "definitional"
    NORMATIVE = "normative"
    PROGNOSTIC = "prognostic"
    COUNTERFACTUAL = "counterfactual"
    METHODOLOGICAL = "methodological"
    UNCERTAINTY = "uncertainty"


class ClaimStatus(StrEnum):
    """The formalisation status of a claim.

    DRAFT:      Default. No Wirkgefüge link yet — blocks publication.
    LINKED:     Mapped to a causal model element — appears as confirmed claim.
    UNRESOLVED: Consciously marked as an open gap — appears as open finding.
    """

    DRAFT = "draft"
    LINKED = "linked"
    UNRESOLVED = "unresolved"


class Claim:
    """A single extractable assertion from a Scene.

    Claims are provisional – the author can confirm, reject, or reformulate them.
    The label is a short human-readable name; text is the full original wording.

    Invariants enforced at construction time:
    - label must not be empty
    - text must not be empty
    - confidence must be between 0.0 and 1.0 (inclusive)
    """

    def __init__(
        self,
        id: str | None,
        label: str,
        text: str,
        typ: ClaimType,
        confidence: float,
        status: ClaimStatus = ClaimStatus.DRAFT,
        wirkgefuege_ref: str | None = None,
    ) -> None:
        self._id = id
        self._label = label
        self._text = text
        self._typ = typ
        self._confidence = confidence
        self._status = status
        self._wirkgefuege_ref = wirkgefuege_ref

    @classmethod
    def create(cls, label: str, text: str, typ: ClaimType, confidence: float) -> Claim:
        """Creates a new Claim from extracted data.

        Raises ClaimValidationError for empty label, empty text,
        or out-of-range confidence.
        """
        if not label.strip():
            raise ClaimValidationError("label must not be empty")
        if not text.strip():
            raise ClaimValidationError("text must not be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ClaimValidationError("confidence must be between 0.0 and 1.0")
        return cls(id=None, label=label, text=text, typ=typ, confidence=confidence)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Claim:
        """Reconstructs a Claim from a database record.

        Raises ClaimValidationError for an unrecognised typ value.
        """
        try:
            typ = ClaimType(record["typ"])
        except ValueError as e:
            raise ClaimValidationError(f"Unknown claim type in record: {record['typ']}") from e
        status = ClaimStatus(record.get("status", ClaimStatus.DRAFT))
        return cls(
            id=record["id"],
            label=record["label"],
            text=record["text"],
            typ=typ,
            confidence=record["confidence"],
            status=status,
            wirkgefuege_ref=record.get("wirkgefuege_ref"),
        )

    def link_to_wirkgefuege(self, ref_id: str) -> None:
        """Links this Claim to a causal model element and sets status to LINKED."""
        self._wirkgefuege_ref = ref_id
        self._status = ClaimStatus.LINKED

    def mark_unresolved(self) -> None:
        """Marks this Claim as an open, unresolvable gap. Sets status to UNRESOLVED."""
        self._status = ClaimStatus.UNRESOLVED

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def text(self) -> str:
        return self._text

    @property
    def typ(self) -> ClaimType:
        return self._typ

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def status(self) -> ClaimStatus:
        return self._status

    @property
    def wirkgefuege_ref(self) -> str | None:
        return self._wirkgefuege_ref
