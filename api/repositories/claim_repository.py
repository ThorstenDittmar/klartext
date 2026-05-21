"""Port: defines the contract for persisting and loading Claims."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.claim import Claim


class ClaimRepository(ABC):
    """Abstract base class for all ClaimRepository implementations.

    Concrete adapters (e.g. SupabaseClaimRepository) implement the actual
    data access. Tests inject a FakeClaimRepository.
    """

    @abstractmethod
    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Persists all given Claims for the specified scene.

        Returns the Claims with IDs assigned.
        An empty input list is valid and returns an empty list.
        Raises ClaimPersistenceError on database failure.
        """

    @abstractmethod
    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns all Claims that belong to the given scene.

        Returns an empty list when no Claims have been saved for that scene.
        Raises ClaimPersistenceError on database failure.
        """
