"""CausalModelService — business logic for CausalModel management and consistency checking."""

from __future__ import annotations

from api.exceptions.causal_model import (
    CausalRelationNotFoundError,
    SlotNotFoundError,
)
from api.models.causal_model import (
    Axiom,
    CausalModel,
    CausalRelation,
    EpistemicStatus,
    Polarity,
    Slot,
    SlotType,
)
from api.providers.consistency_checker import ConsistencyChecker, ConsistencyResult
from api.repositories.causal_model_repository import CausalModelRepository


class CausalModelService:
    """Orchestrates CausalModel persistence and consistency checking."""

    def __init__(
        self,
        repository: CausalModelRepository,
        consistency_checker: ConsistencyChecker,
    ) -> None:
        self._repository = repository
        self._checker = consistency_checker

    async def create(self, title: str) -> CausalModel:
        """Creates and persists a new CausalModel."""
        causal_model = CausalModel.create(title=title)
        return await self._repository.save(causal_model)

    async def add_axiom(self, causal_model_id: str, label: str, description: str) -> Axiom:
        """Adds an Axiom to an existing CausalModel. Raises CausalModelNotFoundError if absent."""
        await self._repository.find_by_id(causal_model_id)
        axiom = Axiom.create(label=label, description=description)
        return await self._repository.add_axiom(causal_model_id, axiom)

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Returns a CausalModel with all its Axioms. Raises CausalModelNotFoundError if absent."""
        return await self._repository.find_by_id(causal_model_id)

    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries."""
        return await self._repository.list_all()

    async def check_consistency(self, causal_model_id: str, scene_text: str) -> ConsistencyResult:
        """Checks a scene text against all Axioms of the given CausalModel.

        Raises CausalModelNotFoundError if the CausalModel does not exist.
        Returns a ConsistencyResult with conflicts if inconsistencies are detected.
        """
        causal_model = await self._repository.find_by_id(causal_model_id)
        return await self._checker.check(scene_text, causal_model.axioms)

    async def add_slot(
        self,
        causal_model_id: str,
        identifier: str,
        slot_type: SlotType,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> Slot:
        """Adds a Slot to the CausalModel. Raises CausalModelNotFoundError if absent."""
        await self._repository.find_by_id(causal_model_id)
        slot = Slot.create(
            identifier=identifier,
            slot_type=slot_type,
            epistemic_status=epistemic_status,
        )
        return await self._repository.add_slot(causal_model_id, slot)

    async def update_slot(
        self,
        causal_model_id: str,
        slot_id: str,
        epistemic_status: EpistemicStatus,
        identifier: str | None = None,
    ) -> Slot:
        """Updates the epistemic_status and optionally renames the identifier of a Slot.

        Raises CausalModelNotFoundError or SlotNotFoundError if either is absent.
        """
        await self._repository.find_by_id(causal_model_id)
        slots = await self._repository.find_slots_by_model_id(causal_model_id)
        slot = next((s for s in slots if s.id == slot_id), None)
        if slot is None:
            raise SlotNotFoundError(f"Slot not found: {slot_id}")
        slot.update(epistemic_status=epistemic_status, identifier=identifier)
        return await self._repository.update_slot(slot)

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Removes a Slot from the CausalModel."""
        await self._repository.find_by_id(causal_model_id)
        await self._repository.remove_slot(causal_model_id, slot_id)

    async def add_relation(
        self,
        causal_model_id: str,
        identifier: str,
        source_slot_id: str,
        target_slot_id: str,
        mechanism: str | None = None,
        polarity: Polarity | None = None,
    ) -> CausalRelation:
        """Adds a CausalRelation between two Slots.

        Raises CausalModelNotFoundError or SlotNotFoundError if any ID is absent.
        """
        await self._repository.find_by_id(causal_model_id)
        slots = await self._repository.find_slots_by_model_id(causal_model_id)
        slot_index: dict[str, Slot] = {s.id: s for s in slots if s.id}
        source = slot_index.get(source_slot_id)
        target = slot_index.get(target_slot_id)
        if source is None:
            raise SlotNotFoundError(f"Source slot not found: {source_slot_id}")
        if target is None:
            raise SlotNotFoundError(f"Target slot not found: {target_slot_id}")
        relation = CausalRelation.create(
            identifier=identifier,
            source=source,
            target=target,
            mechanism=mechanism,
            polarity=polarity,
        )
        return await self._repository.add_relation(causal_model_id, relation)

    async def update_relation(
        self,
        causal_model_id: str,
        relation_id: str,
        mechanism: str | None,
        polarity: Polarity | None,
        epistemic_status: EpistemicStatus,
    ) -> CausalRelation:
        """Updates an existing CausalRelation.

        Raises CausalModelNotFoundError or CausalRelationNotFoundError if absent.
        """
        await self._repository.find_by_id(causal_model_id)
        relations = await self._repository.find_relations_by_model_id(causal_model_id)
        relation = next((r for r in relations if r.id == relation_id), None)
        if relation is None:
            raise CausalRelationNotFoundError(f"CausalRelation not found: {relation_id}")
        relation.update(
            mechanism=mechanism,
            polarity=polarity,
            epistemic_status=epistemic_status,
        )
        return await self._repository.update_relation(relation)

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Removes a CausalRelation from the CausalModel."""
        await self._repository.find_by_id(causal_model_id)
        await self._repository.remove_relation(causal_model_id, relation_id)
