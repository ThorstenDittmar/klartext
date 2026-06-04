"""Domain objects for narratives, their scenes and their actors."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from api.exceptions.narrative import (
    ActorValidationError,
    NarrativeValidationError,
    SceneValidationError,
)


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
        """Creates a new Scene from user input.

        Raises SceneValidationError for empty title or text.
        """
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


class ActorType(StrEnum):
    """The type of an Actor within a Narrative.

    Values align with the Wirkmodell entity taxonomy so that actors
    can be mapped to corresponding model elements.
    """

    INDIVIDUAL = "individual"
    ORGANISATION = "organisation"
    GROUP = "group"
    INSTITUTION = "institution"
    ABSTRACT = "abstract_entity"


class Actor:
    """A participant in a Narrative.

    A person, organisation, group, institution or abstract entity that acts or is
    acted upon within the story. The optional entity_ref links this actor to a
    causal model Entity, forming the bridge between narrative figure and formal model.

    Invariants enforced at construction time:
    - label must not be empty
    """

    def __init__(
        self,
        id: str | None,
        label: str,
        actor_type: ActorType,
        notes: str | None,
        entity_ref: str | None = None,
    ) -> None:
        self._id = id
        self._label = label
        self._actor_type = actor_type
        self._notes = notes
        self._entity_ref = entity_ref

    @classmethod
    def create(
        cls,
        label: str,
        actor_type: ActorType,
        notes: str | None = None,
        entity_ref: str | None = None,
    ) -> Actor:
        """Creates a new Actor from user input. Raises ActorValidationError for empty label."""
        if not label.strip():
            raise ActorValidationError("label must not be empty")
        return cls(id=None, label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Actor:
        """Reconstructs an Actor from a database record.

        Raises ActorValidationError for an unrecognised actor_type value.
        """
        try:
            actor_type = ActorType(record["actor_type"])
        except ValueError as e:
            raise ActorValidationError(
                f"Unknown actor type in record: {record['actor_type']}"
            ) from e
        return cls(
            id=record["id"],
            label=record["label"],
            actor_type=actor_type,
            notes=record.get("notes"),
            entity_ref=record.get("entity_ref"),
        )

    def update(self, label: str, actor_type: ActorType, notes: str | None) -> None:
        """Updates label, actor_type and notes. Raises ActorValidationError for empty label."""
        if not label.strip():
            raise ActorValidationError("label must not be empty")
        self._label = label
        self._actor_type = actor_type
        self._notes = notes

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def actor_type(self) -> ActorType:
        return self._actor_type

    @property
    def notes(self) -> str | None:
        return self._notes

    @property
    def entity_ref(self) -> str | None:
        return self._entity_ref


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

    def remove_actor(self, actor_id: str) -> None:
        """Removes the Actor with the given id from this Narrative. Silent no-op for unknown ids."""
        self._actors = [a for a in self._actors if a.id != actor_id]

    def link_to_causal_model(self, causal_model_id: str) -> None:
        """Links this Narrative to a CausalModel by ID.

        This is the foundational connection that enables consistency checking,
        implicit assumption detection and the Transparenzbericht.
        Raises NarrativeValidationError for empty or whitespace-only IDs.
        """
        if not causal_model_id.strip():
            raise NarrativeValidationError("causal_model_id must not be empty")
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
