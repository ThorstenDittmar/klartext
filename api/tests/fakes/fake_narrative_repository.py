"""FakeNarrativeRepository — in-memory NarrativeRepository for unit tests."""

from __future__ import annotations

import logging
import uuid

from api.exceptions.narrative import ActorNotFoundError, NarrativeNotFoundError
from api.models.narrative import Actor, Narrative, Scene
from api.repositories.narrative_repository import NarrativeRepository


class FakeNarrativeRepository(NarrativeRepository):
    """In-memory NarrativeRepository for unit tests.

    Assigns UUID strings as IDs on save. No database involved.
    """

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._store: dict[str, Narrative] = {}

    async def save(self, narrative: Narrative) -> Narrative:
        """Stores the narrative with a generated ID and returns it with IDs assigned."""
        self.logger.info("FakeNarrativeRepository.save: title=%s", narrative.title)
        narrative_id = str(uuid.uuid4())
        saved = Narrative(id=narrative_id, title=narrative.title, user_id=narrative.user_id)
        for scene in narrative.scenes:
            saved.add_scene(
                Scene(
                    id=str(uuid.uuid4()),
                    title=scene.title,
                    text=scene.text,
                    position=scene.position,
                )
            )
        self._store[narrative_id] = saved
        return saved

    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Returns the narrative for the given ID. Raises NarrativeNotFoundError if absent."""
        self.logger.debug("FakeNarrativeRepository.find_by_id: narrative_id=%s", narrative_id)
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        return self._store[narrative_id]

    async def list_all(self) -> list[Narrative]:
        """Returns all saved narratives as title-only summaries."""
        self.logger.debug("FakeNarrativeRepository.list_all")
        return [Narrative(id=n.id, title=n.title) for n in self._store.values()]

    async def add_scene(self, narrative_id: str, scene: Scene) -> Scene:
        """Appends a scene to the stored narrative and returns it with an assigned ID."""
        self.logger.info("FakeNarrativeRepository.add_scene: narrative_id=%s", narrative_id)
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        saved_scene = Scene(
            id=str(uuid.uuid4()),
            title=scene.title,
            text=scene.text,
            position=scene.position,
        )
        self._store[narrative_id].add_scene(saved_scene)
        return saved_scene

    async def add_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Appends an actor to the stored narrative and returns it with an assigned ID."""
        self.logger.info("FakeNarrativeRepository.add_actor: narrative_id=%s", narrative_id)
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        saved_actor = Actor(
            id=str(uuid.uuid4()),
            label=actor.label,
            actor_type=actor.actor_type,
            notes=actor.notes,
            entity_ref=actor.entity_ref,
        )
        self._store[narrative_id].add_actor(saved_actor)
        return saved_actor

    async def get_actor(self, narrative_id: str, actor_id: str) -> Actor:
        """Returns the actor with the given ID from the stored narrative."""
        self.logger.debug(
            "FakeNarrativeRepository.get_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor_id,
        )
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        for actor in self._store[narrative_id].actors:
            if actor.id == actor_id:
                return actor
        raise ActorNotFoundError(f"Actor not found: {actor_id}")

    async def update_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Persists the already-mutated actor and returns it."""
        self.logger.info(
            "FakeNarrativeRepository.update_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor.id,
        )
        # The actor object in the store was already mutated in-place by Actor.update().
        return actor

    async def remove_actor(self, narrative_id: str, actor_id: str) -> None:
        """Removes the actor with the given ID from the stored narrative."""
        self.logger.info(
            "FakeNarrativeRepository.remove_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor_id,
        )
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        self._store[narrative_id].remove_actor(actor_id)

    async def link_to_causal_model(self, narrative_id: str, causal_model_id: str) -> Narrative:
        """Stores the causal_model_id on the narrative and returns the updated narrative."""
        self.logger.info(
            "FakeNarrativeRepository.link_to_causal_model: narrative_id=%s", narrative_id
        )
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        # Always apply — covers both direct repository calls (tests) and service-mediated calls.
        self._store[narrative_id].link_to_causal_model(causal_model_id)
        return self._store[narrative_id]

    async def list_for_user(self, user_id: str) -> list[Narrative]:
        """Returns all Narratives in the store owned by the given user."""
        self.logger.debug("FakeNarrativeRepository.list_for_user: user_id=%s", user_id)
        return [n for n in self._store.values() if n.user_id == user_id]
