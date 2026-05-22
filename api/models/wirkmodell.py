"""Domain objects for Wirkmodelle and their Axiome."""

from __future__ import annotations

from enum import Enum
from typing import Any

from api.exceptions.wirkmodell import AxiomValidationError, WirkmodellValidationError


class WirkmodellStatus(str, Enum):
    PRIVAT = "privat"
    GETEILT = "geteilt"
    REVIEWFAEHIG = "reviewfaehig"
    INTERN = "intern"
    KATALOG = "katalog"
    ARCHIVIERT = "archiviert"
    ERSETZT = "ersetzt"
    ZURUECKGEZOGEN = "zurueckgezogen"


class Axiom:
    """An axiomatic assumption within a Wirkmodell.

    An Axiom is the simplest Modellelement: a labelled statement that is
    set as a premise and not derived from other elements. It forms the
    basis for consistency checking against narrative scenes.

    Invariants enforced at construction time:
    - label must not be empty
    - beschreibung must not be empty
    """

    def __init__(self, id: str | None, label: str, beschreibung: str) -> None:
        self._id = id
        self._label = label
        self._beschreibung = beschreibung

    @classmethod
    def create(cls, label: str, beschreibung: str) -> Axiom:
        """Creates a new Axiom. Raises AxiomValidationError for empty label or beschreibung."""
        if not label.strip():
            raise AxiomValidationError("label must not be empty")
        if not beschreibung.strip():
            raise AxiomValidationError("beschreibung must not be empty")
        return cls(id=None, label=label, beschreibung=beschreibung)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Axiom:
        """Reconstructs an Axiom from a database record."""
        return cls(
            id=record["id"],
            label=record["label"],
            beschreibung=record["beschreibung"],
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def beschreibung(self) -> str:
        return self._beschreibung


class Wirkmodell:
    """A formal, versionable causal model.

    A Wirkmodell defines a bounded domain of assumptions (Axiome), entities,
    relations and claims. It serves as the reference against which narrative
    scenes are checked for consistency.

    Invariants enforced at construction time:
    - titel must not be empty
    """

    def __init__(
        self,
        id: str | None,
        titel: str,
        status: WirkmodellStatus = WirkmodellStatus.PRIVAT,
    ) -> None:
        self._id = id
        self._titel = titel
        self._status = status
        self._axiome: list[Axiom] = []

    @classmethod
    def create(cls, titel: str) -> Wirkmodell:
        """Creates a new Wirkmodell with status 'privat'. Raises WirkmodellValidationError for empty titel."""
        if not titel.strip():
            raise WirkmodellValidationError("titel must not be empty")
        return cls(id=None, titel=titel)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Wirkmodell:
        """Reconstructs a Wirkmodell from a database record."""
        return cls(
            id=record["id"],
            titel=record["titel"],
            status=WirkmodellStatus(record["status"]),
        )

    def add_axiom(self, axiom: Axiom) -> None:
        """Appends an Axiom to the Wirkmodell in the order it is called."""
        self._axiome.append(axiom)

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def titel(self) -> str:
        return self._titel

    @property
    def status(self) -> WirkmodellStatus:
        return self._status

    @property
    def axiome(self) -> list[Axiom]:
        return self._axiome
