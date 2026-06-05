"""Service: orchestrates narrative creation, import, and retrieval."""

from __future__ import annotations

import logging
from pathlib import Path

from api.models.narrative import Actor, ActorType, Narrative, NarrativeSummary, Scene
from api.repositories.narrative_repository import NarrativeRepository
from api.services.narrative_import_service import NarrativeImportService


class NarrativeService:
    """Coordinates creation, file import, and database persistence for Narratives.

    Responsibilities:
    - Creates new empty Narratives via create().
    - Adds Scenes to existing Narratives via add_scene().
    - Delegates file reading and parsing to NarrativeImportService.
    - Delegates persistence to NarrativeRepository.
    - Provides find_by_id, list_all, and list_for_user for read access.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        import_service: NarrativeImportService,
        repository: NarrativeRepository,
    ) -> None:
        self._import_service = import_service
        self._repository = repository

    async def create(self, title: str, user_id: str | None = None) -> Narrative:
        """Creates and persists a new empty Narrative with the given title.

        If user_id is provided, the Narrative is assigned to that user before saving.
        Returns the saved Narrative with an assigned ID and no scenes.
        Raises NarrativeValidationError if the title is empty.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.debug("NarrativeService.create: title=%s, user_id=%s", title, user_id)
        narrative = Narrative.create(title)
        if user_id is not None:
            narrative.assign_user(user_id)
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

    async def import_from_file(self, path: Path, user_id: str | None = None) -> Narrative:
        """Reads, parses and persists a Narrative from the given file path.

        If user_id is provided, the Narrative is assigned to that user before saving.
        Returns the saved Narrative with IDs assigned to it and all its Scenes.
        Raises NarrativeFileNotFoundError if the file does not exist.
        Raises NarrativeParseError if the file is empty or contains no scenes.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.debug("NarrativeService.import_from_file: path=%s, user_id=%s", path, user_id)
        narrative = self._import_service.import_from_file(path)
        if user_id is not None:
            narrative.assign_user(user_id)
        return await self._repository.save(narrative)

    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Returns the Narrative with the given ID, including its Scenes.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        """
        return await self._repository.find_by_id(narrative_id)

    async def list_all(self) -> list[Narrative]:
        """Returns all persisted Narratives without their Scenes."""
        return await self._repository.list_all()

    async def list_for_user(self, user_id: str) -> list[Narrative]:
        """Returns all Narratives owned by the given user."""
        self.logger.debug("NarrativeService.list_for_user: user_id=%s", user_id)
        return await self._repository.list_for_user(user_id)

    async def list_summaries_for_user(self, user_id: str) -> list[NarrativeSummary]:
        """Returns NarrativeSummary objects with counts for the given user.

        Raises NarrativePersistenceError on database failure.
        """
        self.logger.debug("NarrativeService.list_summaries_for_user: user_id=%s", user_id)
        return await self._repository.list_summaries_for_user(user_id)

    async def add_actor(
        self,
        narrative_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None = None,
        entity_ref: str | None = None,
    ) -> Actor:
        """Adds a new Actor to the Narrative with the given ID.

        Returns the saved Actor with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorValidationError if the label is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = Actor.create(label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref)
        return await self._repository.add_actor(narrative_id, actor)

    async def update_actor(
        self,
        narrative_id: str,
        actor_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None,
        entity_ref: str | None = None,
    ) -> Actor:
        """Updates label, actor_type, notes and entity_ref of an existing Actor.

        Uses find → change → save: loads the actor, applies changes via the domain method,
        then persists the result.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises ActorValidationError if the new label is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = await self._repository.get_actor(narrative_id, actor_id)
        actor.update(label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref)
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

    async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
        """Returns all Narratives linked to the given CausalModel.

        Returns an empty list when no Narratives are linked.
        """
        self.logger.debug(
            "NarrativeService.find_by_causal_model_id: causal_model_id=%s", causal_model_id
        )
        return await self._repository.find_by_causal_model_id(causal_model_id)

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
