"""Domain objects for CausalModels and their Axioms."""

from __future__ import annotations

from enum import Enum
from typing import Any

from api.exceptions.causal_model import AxiomValidationError, CausalModelValidationError


class CausalModelStatus(str, Enum):
    PRIVATE = "privat"
    SHARED = "geteilt"
    REVIEWABLE = "reviewfaehig"
    INTERNAL = "intern"
    CATALOG = "katalog"
    ARCHIVED = "archiviert"
    REPLACED = "ersetzt"
    WITHDRAWN = "zurueckgezogen"


class Axiom:
    """An axiomatic assumption within a CausalModel.

    An Axiom is the simplest model element: a labelled statement that is
    set as a premise and not derived from other elements. It forms the
    basis for consistency checking against narrative scenes.

    Invariants enforced at construction time:
    - label must not be empty
    - description must not be empty
    """

    def __init__(self, id: str | None, label: str, description: str) -> None:
        self._id = id
        self._label = label
        self._description = description

    @classmethod
    def create(cls, label: str, description: str) -> Axiom:
        """Creates a new Axiom. Raises AxiomValidationError for empty label or description."""
        if not label.strip():
            raise AxiomValidationError("label must not be empty")
        if not description.strip():
            raise AxiomValidationError("description must not be empty")
        return cls(id=None, label=label, description=description)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Axiom:
        """Reconstructs an Axiom from a database record."""
        return cls(
            id=record["id"],
            label=record["label"],
            description=record["beschreibung"],
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def description(self) -> str:
        return self._description


class CausalModel:
    """A formal, versionable causal model.

    A CausalModel defines a bounded domain of assumptions (Axioms), entities,
    relations and claims. It serves as the reference against which narrative
    scenes are checked for consistency.

    Invariants enforced at construction time:
    - title must not be empty
    """

    def __init__(
        self,
        id: str | None,
        title: str,
        status: CausalModelStatus = CausalModelStatus.PRIVATE,
    ) -> None:
        self._id = id
        self._title = title
        self._status = status
        self._axioms: list[Axiom] = []

    @classmethod
    def create(cls, title: str) -> CausalModel:
        """Creates a new CausalModel with status 'private'. Raises CausalModelValidationError for empty title."""
        if not title.strip():
            raise CausalModelValidationError("title must not be empty")
        return cls(id=None, title=title)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> CausalModel:
        """Reconstructs a CausalModel from a database record."""
        return cls(
            id=record["id"],
            title=record["title"],
            status=CausalModelStatus(record["status"]),
        )

    def add_axiom(self, axiom: Axiom) -> None:
        """Appends an Axiom to the CausalModel in the order it is called."""
        self._axioms.append(axiom)

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> CausalModelStatus:
        return self._status

    @property
    def axioms(self) -> list[Axiom]:
        return self._axioms
