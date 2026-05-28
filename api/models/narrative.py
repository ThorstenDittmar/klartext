"""Domain objects for narratives, their scenes and their actors."""

from __future__ import annotations

from enum import Enum
from typing import Any

from api.exceptions.narrative import ActorValidationError, NarrativeValidationError, SceneValidationError


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


class ActorType(str, Enum):
    """The type of an Actor within a Narrative.

    Values align with the Wirkmodell entity taxonomy so that actors
    can be mapped to corresponding model elements.
    """

    INDIVIDUAL = "figur"
    ORGANISATION = "organisation"
    GROUP = "gruppe"
    INSTITUTION = "institution"
    ABSTRACT = "abstrakte_entitaet"


class Actor:
    """A participant in a Narrative: a person, organisation, group, institution
    or abstract entity that acts or is acted upon within the story.

    Actors can be mapped to Entitäten in the linked CausalModel, forming the
    connection between concrete narrative figures and abstract model elements.

    Invariants enforced at construction time:
    - name must not be empty
    """

    def __init__(
        self,
        id: str | None,
        name: str,
        typ: ActorType,
        description: str | None,
    ) -> None:
        self._id = id
        self._name = name
        self._typ = typ
        self._description = description

    @classmethod
    def create(
        cls,
        name: str,
        typ: ActorType,
        description: str | None = None,
    ) -> Actor:
        """Creates a new Actor from user input. Raises ActorValidationError for empty name."""
        if not name.strip():
            raise ActorValidationError("name must not be empty")
        return cls(id=None, name=name, typ=typ, description=description)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Actor:
        """Reconstructs an Actor from a database record."""
        return cls(
            id=record["id"],
            name=record["name"],
            typ=ActorType(record["typ"]),
            description=record.get("description"),
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def typ(self) -> ActorType:
        return self._typ

    @property
    def description(self) -> str | None:
        return self._description


class Narrative:
    """A narrative: an ordered collection of Scenes and Actors with a title.

    Scenes are added explicitly via add_scene(); Actors via add_actor().
    The optional causal_model_id links this Narrative to a CausalModel,
    forming the basis for consistency checking and the Transparenzbericht.
    """

    def __init__(
        self,
        id: str | None,
        title: str,
        causal_model_id: str | None = None,
    ) -> None:
        self._id = id
        self._title = title
        self._causal_model_id = causal_model_id
        self._scenes: list[Scene] = []
        self._actors: list[Actor] = []

    @classmethod
    def create(cls, title: str) -> Narrative:
        """Creates a new empty Narrative. Raises NarrativeValidationError for empty title."""
        if not title.strip():
            raise NarrativeValidationError("title must not be empty")
        return cls(id=None, title=title)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Narrative:
        """Reconstructs a Narrative from a database record."""
        return cls(
            id=record["id"],
            title=record["title"],
            causal_model_id=record.get("causal_model_id"),
        )

    def add_scene(self, scene: Scene) -> None:
        """Appends a Scene to the Narrative in the order it is called."""
        self._scenes.append(scene)

    def add_actor(self, actor: Actor) -> None:
        """Appends an Actor to the Narrative in the order it is called."""
        self._actors.append(actor)

    def link_to_causal_model(self, causal_model_id: str) -> None:
        """Links this Narrative to a CausalModel by ID.

        This is the foundational connection that enables consistency checking,
        implicit assumption detection and the Transparenzbericht.
        """
        self._causal_model_id = causal_model_id

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def causal_model_id(self) -> str | None:
        return self._causal_model_id

    @property
    def scenes(self) -> list[Scene]:
        return self._scenes

    @property
    def actors(self) -> list[Actor]:
        return self._actors
