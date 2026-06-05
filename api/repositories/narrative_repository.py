"""Port: defines the contract for persisting and loading Narratives."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.narrative import Actor, Narrative, NarrativeSummary, Scene


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

    @abstractmethod
    async def add_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Persists a new Actor and appends it to the Narrative with the given ID.

        Returns the Actor with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def get_actor(self, narrative_id: str, actor_id: str) -> Actor:
        """Returns the Actor with the given ID from the Narrative.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def update_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Persists changes to an existing Actor.

        Returns the updated Actor.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def remove_actor(self, narrative_id: str, actor_id: str) -> None:
        """Deletes the Actor with the given ID from the Narrative.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def link_to_causal_model(self, narrative_id: str, causal_model_id: str) -> Narrative:
        """Stores the causal_model_id on the Narrative with the given ID.

        Returns the updated Narrative.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def list_for_user(self, user_id: str) -> list[Narrative]:
        """Returns all Narratives owned by the given user.

        Returns an empty list if no narratives exist for that user.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def list_summaries_for_user(self, user_id: str) -> list[NarrativeSummary]:
        """Returns Narrative summaries with precomputed counts for the given user.

        Returns an empty list if no narratives exist for that user.
        Raises NarrativePersistenceError on database failure.
        """

    @abstractmethod
    async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
        """Returns all Narratives linked to the given CausalModel.

        Returns an empty list when no Narratives are linked.
        Raises NarrativePersistenceError on database failure.
        """
