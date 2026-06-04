"""CausalModelRepository port — abstract interface for CausalModel persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.causal_model import Axiom, CausalModel, CausalRelation, Slot


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

    @abstractmethod
    async def add_slot(self, causal_model_id: str, slot: Slot) -> Slot:
        """Adds a Slot to the CausalModel and returns it with an ID assigned.

        Raises CausalModelNotFoundError if the CausalModel does not exist.
        """

    @abstractmethod
    async def find_slots_by_model_id(self, causal_model_id: str) -> list[Slot]:
        """Returns all Slots belonging to the given CausalModel."""

    @abstractmethod
    async def update_slot(self, slot: Slot) -> Slot:
        """Persists the current state of an existing Slot. Returns the updated Slot."""

    @abstractmethod
    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Removes a Slot from the CausalModel. Silent no-op for unknown IDs."""

    @abstractmethod
    async def add_relation(self, causal_model_id: str, relation: CausalRelation) -> CausalRelation:
        """Adds a CausalRelation to the CausalModel and returns it with an ID assigned.

        Raises CausalModelNotFoundError if the CausalModel does not exist.
        """

    @abstractmethod
    async def find_relations_by_model_id(self, causal_model_id: str) -> list[CausalRelation]:
        """Returns all CausalRelations belonging to the given CausalModel."""

    @abstractmethod
    async def update_relation(self, relation: CausalRelation) -> CausalRelation:
        """Persists the current state of an existing CausalRelation."""

    @abstractmethod
    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Removes a CausalRelation from the CausalModel. Silent no-op for unknown IDs."""
