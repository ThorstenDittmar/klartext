"""Domain model: NarrativeUnit hierarchy (Work, Part, Chapter, Scene, Fragment).

All five types share a single database table (narrative_units) with a
self-referential parent_id FK. The tree is assembled in Python after
a single flat SELECT — not via recursive SQL.

Subclasses auto-register via __init_subclass__ so NarrativeUnit.from_record()
dispatches to the right type without an explicit if/elif chain.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from api.exceptions.narrative_unit import InvalidOperationError, NarrativeUnitValidationError


class NarrativeUnit(ABC):
    """Abstract base for all narrative content tree nodes.

    Subclasses must define TYP as a class-level string constant matching the
    value stored in the narrative_units.typ column.
    """

    TYP: str  # Defined by every concrete subclass
    _registry: ClassVar[dict[str, type[NarrativeUnit]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Registers each concrete subclass by its TYP value."""
        super().__init_subclass__(**kwargs)
        if "TYP" in cls.__dict__ and cls.TYP:
            NarrativeUnit._registry[cls.TYP] = cls

    def __init__(
        self,
        id: str | None,
        title: str | None,
        content: str | None,
        position: int,
        narrative_id: str,
        parent_id: str | None,
    ) -> None:
        self._id = id
        self._title = title
        self._content = content
        self._position = position
        self._narrative_id = narrative_id
        self._parent_id = parent_id
        self._children: list[NarrativeUnit] = []

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> NarrativeUnit:
        """Reconstructs the correct NarrativeUnit subclass from a database record.

        Routes by the 'typ' column value. Raises NarrativeUnitValidationError
        for unrecognised typ values.
        """
        typ = record.get("typ", "")
        subclass = cls._registry.get(typ)
        if subclass is None:
            raise NarrativeUnitValidationError(f"Unknown narrative unit type: '{typ}'")
        return subclass(
            id=record["id"],
            title=record.get("title"),
            content=record.get("content"),
            position=record["position"],
            narrative_id=record["narrative_id"],
            parent_id=record.get("parent_id"),
        )

    def add_child(self, child: NarrativeUnit) -> None:
        """Appends a child node to this unit's subtree."""
        self._children.append(child)

    def update_content(self, content: str) -> None:
        """Replaces the text content of this unit."""
        self._content = content

    def update_title(self, title: str) -> None:
        """Renames this unit. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        self._title = title

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str | None:
        return self._title

    @property
    def content(self) -> str | None:
        return self._content

    @property
    def position(self) -> int:
        return self._position

    @property
    def narrative_id(self) -> str:
        return self._narrative_id

    @property
    def parent_id(self) -> str | None:
        return self._parent_id

    @property
    def children(self) -> list[NarrativeUnit]:
        return self._children

    @property
    def typ(self) -> str:
        """Returns the typ value matching the database column."""
        return self.__class__.TYP


class Work(NarrativeUnit):
    """Root container of a narrative content tree."""

    TYP = "work"

    @classmethod
    def create(cls, title: str, narrative_id: str) -> Work:
        """Creates a new Work node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None,
            title=title,
            content=None,
            position=1,
            narrative_id=narrative_id,
            parent_id=None,
        )


class Part(NarrativeUnit):
    """A major structural division within a Work (e.g. Erster Teil)."""

    TYP = "part"

    @classmethod
    def create(cls, title: str, narrative_id: str, parent_id: str, position: int) -> Part:
        """Creates a new Part node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None,
            title=title,
            content=None,
            position=position,
            narrative_id=narrative_id,
            parent_id=parent_id,
        )


class Chapter(NarrativeUnit):
    """A chapter within a Work or Part."""

    TYP = "chapter"

    @classmethod
    def create(cls, title: str, narrative_id: str, parent_id: str, position: int) -> Chapter:
        """Creates a new Chapter node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None,
            title=title,
            content=None,
            position=position,
            narrative_id=narrative_id,
            parent_id=parent_id,
        )


class Scene(NarrativeUnit):
    """A narrative scene: a thematic or temporal unit of action within the story."""

    TYP = "scene"

    @classmethod
    def create(cls, title: str, narrative_id: str, parent_id: str, position: int) -> Scene:
        """Creates a new Scene node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None,
            title=title,
            content=None,
            position=position,
            narrative_id=narrative_id,
            parent_id=parent_id,
        )


class Fragment(NarrativeUnit):
    """Atomic editing unit — one prose paragraph within a Scene.

    Fragment is the autosave boundary: each <textarea> in the Manuscript View
    corresponds to exactly one Fragment. Title is always None — calling
    update_title() raises InvalidOperationError.
    """

    TYP = "fragment"

    @classmethod
    def create(cls, content: str, narrative_id: str, parent_id: str, position: int) -> Fragment:
        """Creates a new Fragment. Raises NarrativeUnitValidationError for empty content."""
        if not content.strip():
            raise NarrativeUnitValidationError("content must not be empty")
        return cls(
            id=None,
            title=None,
            content=content,
            position=position,
            narrative_id=narrative_id,
            parent_id=parent_id,
        )

    def update_title(self, title: str) -> None:
        """Always raises InvalidOperationError — Fragment has no title."""
        raise InvalidOperationError("Fragment has no title — use update_content() instead.")
