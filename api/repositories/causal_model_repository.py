"""CausalModelRepository port — abstract interface for CausalModel persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.causal_model import Axiom, CausalModel


class CausalModelRepository(ABC):
    """Port — defines the contract for CausalModel data access."""

    @abstractmethod
    async def save(self, causal_model: CausalModel) -> CausalModel:
        """Persists a new CausalModel and returns it with IDs assigned."""

    @abstractmethod
    async def add_axiom(self, causal_model_id: str, axiom: Axiom) -> Axiom:
        """Adds an Axiom to an existing CausalModel and returns it with an ID."""

    @abstractmethod
    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Returns the CausalModel with its Axioms. Raises CausalModelNotFoundError if absent."""

    @abstractmethod
    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries (no axioms loaded)."""
