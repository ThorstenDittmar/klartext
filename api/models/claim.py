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


class Claim:
    """A single extractable assertion from a Scene.

    Claims are provisional – the author can confirm, reject, or reformulate them.
    Invariants enforced at construction time:
    - text must not be empty
    - confidence must be between 0.0 and 1.0 (inclusive)
    """

    def __init__(
        self,
        id: str | None,
        text: str,
        typ: ClaimType,
        confidence: float,
    ) -> None:
        self._id = id
        self._text = text
        self._typ = typ
        self._confidence = confidence

    @classmethod
    def create(cls, text: str, typ: ClaimType, confidence: float) -> Claim:
        """Creates a new Claim from extracted data.

        Raises ClaimValidationError for empty text or out-of-range confidence.
        """
        if not text.strip():
            raise ClaimValidationError("text must not be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ClaimValidationError("confidence must be between 0.0 and 1.0")
        return cls(id=None, text=text, typ=typ, confidence=confidence)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Claim:
        """Reconstructs a Claim from a database record.

        Raises ClaimValidationError for an unrecognised typ value.
        """
        try:
            typ = ClaimType(record["typ"])
        except ValueError as e:
            raise ClaimValidationError(f"Unknown claim type in record: {record['typ']}") from e
        return cls(
            id=record["id"],
            text=record["text"],
            typ=typ,
            confidence=record["confidence"],
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def text(self) -> str:
        return self._text

    @property
    def typ(self) -> ClaimType:
        return self._typ

    @property
    def confidence(self) -> float:
        return self._confidence
