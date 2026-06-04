"""FakeCausalModelRepository — in-memory CausalModelRepository for unit tests."""

from __future__ import annotations

import logging
import uuid

from api.exceptions.causal_model import CausalModelNotFoundError
from api.models.causal_model import Axiom, CausalModel, CausalRelation, Slot
from api.repositories.causal_model_repository import CausalModelRepository


class FakeCausalModelRepository(CausalModelRepository):
    """In-memory CausalModelRepository for unit tests.

    Assigns UUID strings as IDs on save. No database involved.
    """

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._store: dict[str, CausalModel] = {}
        self._slots: dict[str, list[Slot]] = {}
        self._relations: dict[str, list[CausalRelation]] = {}

    async def save(self, causal_model: CausalModel) -> CausalModel:
        """Stores the CausalModel with a generated ID and returns it with IDs assigned."""
        cm_id = str(uuid.uuid4())
        saved = CausalModel(id=cm_id, title=causal_model.title, status=causal_model.status)
        for axiom in causal_model.axioms:
            saved.add_axiom(
                Axiom(id=str(uuid.uuid4()), label=axiom.label, description=axiom.description)
            )
        self._store[cm_id] = saved
        return saved

    async def add_axiom(self, causal_model_id: str, axiom: Axiom) -> Axiom:
        """Adds an Axiom to the stored CausalModel and returns it with an ID."""
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        saved_axiom = Axiom(id=str(uuid.uuid4()), label=axiom.label, description=axiom.description)
        self._store[causal_model_id].add_axiom(saved_axiom)
        return saved_axiom

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Returns the CausalModel with its Axioms. Raises CausalModelNotFoundError if absent."""
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        return self._store[causal_model_id]

    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries."""
        return [
            CausalModel(id=cm.id, title=cm.title, status=cm.status) for cm in self._store.values()
        ]

    async def add_slot(self, causal_model_id: str, slot: Slot) -> Slot:
        """Adds a Slot to the given CausalModel and returns it with an assigned ID."""
        self.logger.info(
            "FakeCausalModelRepository.add_slot: causal_model_id=%s, identifier=%s",
            causal_model_id,
            slot.identifier,
        )
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        saved = Slot(
            id=str(uuid.uuid4()),
            identifier=slot.identifier,
            slot_type=slot.slot_type,
            epistemic_status=slot.epistemic_status,
        )
        self._slots.setdefault(causal_model_id, []).append(saved)
        return saved

    async def find_slots_by_model_id(self, causal_model_id: str) -> list[Slot]:
        """Returns all Slots for the given CausalModel ID."""
        self.logger.debug(
            "FakeCausalModelRepository.find_slots_by_model_id: causal_model_id=%s",
            causal_model_id,
        )
        return list(self._slots.get(causal_model_id, []))

    async def update_slot(self, slot: Slot) -> Slot:
        """Persists the current state of a Slot (in-memory: already mutated in place)."""
        self.logger.info("FakeCausalModelRepository.update_slot: slot_id=%s", slot.id)
        return slot

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Removes a Slot from the in-memory store."""
        self.logger.info(
            "FakeCausalModelRepository.remove_slot: causal_model_id=%s, slot_id=%s",
            causal_model_id,
            slot_id,
        )
        if causal_model_id in self._slots:
            self._slots[causal_model_id] = [
                s for s in self._slots[causal_model_id] if s.id != slot_id
            ]
