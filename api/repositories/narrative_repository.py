"""Port: defines the contract for persisting and loading Narratives."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.narrative import Narrative, Scene


class NarrativeRepository(ABC):
    """Abstract base class for all NarrativeRepository implementations.

    Concrete adapters (e.g. SupabaseNarrativeRepository) implement the actual
    data access. Tests inject a FakeNarrativeRepository.
    """

    @abstractmethod
    async def save(self, narrative: Narrative) -> Narrative:
        """Persists the Narrative and all its Scenes.

        Returns the Narrative with IDs assigned to itself and every Scene.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Returns the Narrative with the given ID, including its Scenes.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def list_all(self) -> list[Narrative]:
        """Returns all persisted Narratives, without loading their Scenes.

        Returns an empty list when no Narratives have been saved yet.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def add_scene(self, narrative_id: str, scene: Scene) -> Scene:
        """Persists a new Scene and appends it to the Narrative with the given ID.

        Returns the Scene with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativePersistenceError on database failure.
        """
