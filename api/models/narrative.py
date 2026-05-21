"""Domain objects for narratives and their scenes."""

from __future__ import annotations

from typing import Any

from api.exceptions.narrative import NarrativeValidationError, SceneValidationError


class Scene:
    """A single scene: the smallest addressable unit within a Narrative.

    Invariants enforced at construction time:
    - title must not be empty
    - text must not be empty
    """

    def __init__(
        self,
        id: str | None,
        title: str,
        text: str,
        position: int,
    ) -> None:
        self._id = id
        self._title = title
        self._text = text
        self._position = position

    @classmethod
    def create(cls, title: str, text: str, position: int) -> Scene:
        """Creates a new Scene from user input. Raises SceneValidationError for empty title or text."""
        if not title.strip():
            raise SceneValidationError("title must not be empty")
        if not text.strip():
            raise SceneValidationError("text must not be empty")
        return cls(id=None, title=title, text=text, position=position)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Scene:
        """Reconstructs a Scene from a database record."""
        return cls(
            id=record["id"],
            title=record["title"],
            text=record["text"],
            position=record["position"],
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def text(self) -> str:
        return self._text

    @property
    def position(self) -> int:
        return self._position


class Narrative:
    """A narrative: an ordered collection of Scenes with a title.

    Scenes are added explicitly via add_scene(); direct list manipulation
    is not permitted.
    """

    def __init__(self, id: str | None, title: str) -> None:
        self._id = id
        self._title = title
        self._scenes: list[Scene] = []

    @classmethod
    def create(cls, title: str) -> Narrative:
        """Creates a new empty Narrative. Raises NarrativeValidationError for empty title."""
        if not title.strip():
            raise NarrativeValidationError("title must not be empty")
        return cls(id=None, title=title)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Narrative:
        """Reconstructs a Narrative from a database record."""
        return cls(id=record["id"], title=record["title"])

    def add_scene(self, scene: Scene) -> None:
        """Appends a Scene to the Narrative in the order it is called."""
        self._scenes.append(scene)

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def scenes(self) -> list[Scene]:
        return self._scenes
