"""Service: orchestrates narrative creation, import, and retrieval."""

from __future__ import annotations

from pathlib import Path

from api.models.narrative import Actor, ActorType, Narrative, Scene
from api.repositories.narrative_repository import NarrativeRepository
from api.services.narrative_import_service import NarrativeImportService


class NarrativeService:
    """Coordinates creation, file import, and database persistence for Narratives.

    Responsibilities:
    - Creates new empty Narratives via create().
    - Adds Scenes to existing Narratives via add_scene().
    - Delegates file reading and parsing to NarrativeImportService.
    - Delegates persistence to NarrativeRepository.
    - Provides find_by_id and list_all for read access.
    """

    def __init__(
        self,
        import_service: NarrativeImportService,
        repository: NarrativeRepository,
    ) -> None:
        self._import_service = import_service
        self._repository = repository

    async def create(self, title: str) -> Narrative:
        """Creates and persists a new empty Narrative with the given title.

        Returns the saved Narrative with an assigned ID and no scenes.
        Raises NarrativeValidationError if the title is empty.
        Raises NarrativePersistenceError on database failure.
        """
        narrative = Narrative.create(title)
        return await self._repository.save(narrative)

    async def add_scene(self, narrative_id: str, title: str, text: str) -> Scene:
        """Adds a new Scene to the Narrative with the given ID.

        The position is assigned automatically as the next sequential number.
        Returns the saved Scene with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises SceneValidationError if title or text is empty.
        Raises NarrativePersistenceError on database failure.
        """
        narrative = await self._repository.find_by_id(narrative_id)
        position = len(narrative.scenes) + 1
        scene = Scene.create(title=title, text=text, position=position)
        return await self._repository.add_scene(narrative_id, scene)

    async def import_from_file(self, path: Path) -> Narrative:
        """Reads, parses and persists a Narrative from the given file path.

        Returns the saved Narrative with IDs assigned to it and all its Scenes.
        Raises NarrativeFileNotFoundError if the file does not exist.
        Raises NarrativeParseError if the file is empty or contains no scenes.
        Raises NarrativePersistenceError on database failure.
        """
        narrative = self._import_service.import_from_file(path)
        return await self._repository.save(narrative)

    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Returns the Narrative with the given ID, including its Scenes.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        """
        return await self._repository.find_by_id(narrative_id)

    async def list_all(self) -> list[Narrative]:
        """Returns all persisted Narratives without their Scenes."""
        return await self._repository.list_all()

    async def add_actor(
        self,
        narrative_id: str,
        name: str,
        typ: ActorType,
        description: str | None = None,
    ) -> Actor:
        """Adds a new Actor to the Narrative with the given ID.

        Returns the saved Actor with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorValidationError if the name is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = Actor.create(name=name, typ=typ, description=description)
        return await self._repository.add_actor(narrative_id, actor)

    async def update_actor(
        self,
        narrative_id: str,
        actor_id: str,
        name: str,
        typ: ActorType,
        description: str | None,
    ) -> Actor:
        """Updates name, type and description of an existing Actor.

        Uses find → change → save: loads the actor, applies changes via the domain method,
        then persists the result.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises ActorValidationError if the new name is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = await self._repository.get_actor(narrative_id, actor_id)
        actor.update(name=name, typ=typ, description=description)
        return await self._repository.update_actor(narrative_id, actor)

    async def remove_actor(self, narrative_id: str, actor_id: str) -> None:
        """Removes an Actor from the Narrative with the given ID.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises NarrativePersistenceError on database failure.

        TODO: Referential integrity — when an Actor is deleted that still appears in scene text
        or is mapped to a causal model entity, the author should be warned.
        Options: (a) soft-delete with warning, (b) pre-delete validation,
        (c) consistency check in Transparenzbericht. Decision pending.
        """
        await self._repository.find_by_id(narrative_id)
        await self._repository.get_actor(narrative_id, actor_id)
        await self._repository.remove_actor(narrative_id, actor_id)

    async def link_to_causal_model(self, narrative_id: str, causal_model_id: str) -> Narrative:
        """Links the Narrative to a CausalModel by ID.

        Uses find → change → save: loads the narrative, validates and applies the link
        via the domain method, then persists the result.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativeValidationError if the causal_model_id is empty.
        Raises NarrativePersistenceError on database failure.
        """
        narrative = await self._repository.find_by_id(narrative_id)
        narrative.link_to_causal_model(causal_model_id)
        return await self._repository.link_to_causal_model(narrative_id, causal_model_id)
