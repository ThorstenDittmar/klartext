"""WirkmodellRepository port — abstract interface for Wirkmodell persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.wirkmodell import Axiom, Wirkmodell


class WirkmodellRepository(ABC):
    """Port — defines the contract for Wirkmodell data access."""

    @abstractmethod
    async def save(self, wirkmodell: Wirkmodell) -> Wirkmodell:
        """Persists a new Wirkmodell and returns it with IDs assigned."""

    @abstractmethod
    async def add_axiom(self, wirkmodell_id: str, axiom: Axiom) -> Axiom:
        """Adds an Axiom to an existing Wirkmodell and returns it with an ID."""

    @abstractmethod
    async def find_by_id(self, wirkmodell_id: str) -> Wirkmodell:
        """Returns the Wirkmodell with its Axiome. Raises WirkmodellNotFoundError if absent."""

    @abstractmethod
    async def list_all(self) -> list[Wirkmodell]:
        """Returns all Wirkmodelle as title-only summaries (no axiome loaded)."""
