"""SupabaseCausalModelRepository — Supabase adapter for CausalModel persistence."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.causal_model import (
    CausalModelNotFoundError,
    CausalModelPersistenceError,
    NamespaceConflictError,
)
from api.models.causal_model import (
    Axiom,
    CausalModel,
    CausalRelation,
    Entity,
    EpistemicStatus,
    Polarity,
    Slot,
)
from api.repositories._supabase import records
from api.repositories.causal_model_repository import CausalModelRepository


class SupabaseCausalModelRepository(CausalModelRepository):
    """Adapter — persists CausalModels and Axioms in Supabase.

    Table mapping:
      causal_models  →  CausalModel (id, title, status)
      model_elements (typ='axiom', is_axiomatic=True)  →  Axiom
      slots  →  Slot / Entity
      causal_relations  →  CausalRelation
    """

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, causal_model: CausalModel) -> CausalModel:
        """Inserts the CausalModel and all its Axioms. Returns both with IDs assigned."""
        try:
            result = (
                await self._client.table("causal_models")
                .insert(
                    {
                        "title": causal_model.title,
                        "status": causal_model.status.value,
                    }
                )
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save CausalModel: {exc}") from exc

        row = records(result.data)[0]
        saved = CausalModel.from_record(row)

        for axiom in causal_model.axioms:
            saved_axiom = await self.add_axiom(saved.id, axiom)  # type: ignore[arg-type]
            saved.add_axiom(saved_axiom)

        return saved

    async def add_axiom(self, causal_model_id: str, axiom: Axiom) -> Axiom:
        """Inserts an Axiom as a model element and returns it with an ID."""
        try:
            result = (
                await self._client.table("model_elements")
                .insert(
                    {
                        "causal_model_id": causal_model_id,
                        "typ": "axiom",
                        "label": axiom.label,
                        "description": axiom.description,
                        "is_axiomatic": True,
                    }
                )
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save Axiom: {exc}") from exc

        row = records(result.data)[0]
        return Axiom.from_record(
            {
                "id": row["id"],
                "label": row["label"],
                "description": row["description"],
            }
        )

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Loads the CausalModel and all its Axioms, Slots and CausalRelations from Supabase."""
        try:
            cm_result = (
                await self._client.table("causal_models")
                .select("*")
                .eq("id", causal_model_id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load CausalModel: {exc}") from exc

        if not cm_result.data:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")

        cm = CausalModel.from_record(records(cm_result.data)[0])

        try:
            axiom_result = (
                await self._client.table("model_elements")
                .select("*")
                .eq("causal_model_id", causal_model_id)
                .eq("typ", "axiom")
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load Axioms: {exc}") from exc

        for row in records(axiom_result.data):
            cm.add_axiom(
                Axiom.from_record(
                    {
                        "id": row["id"],
                        "label": row["label"],
                        "description": row["description"],
                    }
                )
            )

        # Load slots and relations into the model
        for slot in await self.find_slots_by_model_id(causal_model_id):
            try:
                cm.add(slot)
            except NamespaceConflictError:
                pass  # namespace conflict — slot already present, skip
        for relation in await self.find_relations_by_model_id(causal_model_id):
            try:
                cm.add(relation)
            except NamespaceConflictError:
                pass  # namespace conflict — relation already present, skip

        return cm

    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries."""
        try:
            result = await self._client.table("causal_models").select("id, title, status").execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to list CausalModels: {exc}") from exc

        return [CausalModel.from_record(row) for row in records(result.data)]

    async def add_slot(self, causal_model_id: str, slot: Slot) -> Slot:
        """Inserts a Slot into the 'slots' table and returns it with an ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.add_slot: causal_model_id=%s, identifier=%s",
            causal_model_id,
            slot.identifier,
        )
        try:
            result = (
                await self._client.table("slots")
                .insert(
                    {
                        "causal_model_id": causal_model_id,
                        "identifier": slot.identifier,
                        "slot_type": slot.slot_type.value,
                        "epistemic_status": slot.epistemic_status.value,
                        "is_entity": isinstance(slot, Entity),
                    }
                )
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save Slot: {exc}") from exc
        return Slot.from_record(records(result.data)[0])

    async def find_slots_by_model_id(self, causal_model_id: str) -> list[Slot]:
        """Returns all Slots for the given CausalModel ID."""
        self.logger.debug(
            "SupabaseCausalModelRepository.find_slots_by_model_id: causal_model_id=%s",
            causal_model_id,
        )
        try:
            result = (
                await self._client.table("slots")
                .select("*")
                .eq("causal_model_id", causal_model_id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load Slots: {exc}") from exc
        return [Slot.from_record(row) for row in records(result.data)]

    async def update_slot(self, slot: Slot) -> Slot:
        """Updates the epistemic_status of an existing Slot."""
        self.logger.info("SupabaseCausalModelRepository.update_slot: slot_id=%s", slot.id)
        try:
            result = (
                await self._client.table("slots")
                .update({"epistemic_status": slot.epistemic_status.value})
                .eq("id", slot.id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to update Slot: {exc}") from exc
        return Slot.from_record(records(result.data)[0])

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Deletes a Slot by ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.remove_slot: causal_model_id=%s, slot_id=%s",
            causal_model_id,
            slot_id,
        )
        try:
            await self._client.table("slots").delete().eq("id", slot_id).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to remove Slot: {exc}") from exc

    async def add_relation(self, causal_model_id: str, relation: CausalRelation) -> CausalRelation:
        """Inserts a CausalRelation and returns it with an ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.add_relation: causal_model_id=%s, identifier=%s",
            causal_model_id,
            relation.identifier,
        )
        try:
            result = (
                await self._client.table("causal_relations")
                .insert(
                    {
                        "causal_model_id": causal_model_id,
                        "identifier": relation.identifier,
                        "source_slot_id": relation.source.id,
                        "target_slot_id": relation.target.id,
                        "mechanism": relation.mechanism,
                        "polarity": relation.polarity.value if relation.polarity else None,
                        "epistemic_status": relation.epistemic_status.value,
                    }
                )
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save CausalRelation: {exc}") from exc
        row = records(result.data)[0]
        return CausalRelation(
            id=row["id"],
            identifier=row["identifier"],
            source=relation.source,
            target=relation.target,
            mechanism=row.get("mechanism"),
            polarity=Polarity(row["polarity"]) if row.get("polarity") else None,
            epistemic_status=EpistemicStatus(row.get("epistemic_status", "incomplete")),
        )

    async def find_relations_by_model_id(self, causal_model_id: str) -> list[CausalRelation]:
        """Returns CausalRelations for the given CausalModel, with Slots resolved.

        Loads all Slots first, then reconstructs each relation from the joined rows.
        Orphaned relations (whose source or target Slot was deleted) are skipped.
        """
        self.logger.debug(
            "SupabaseCausalModelRepository.find_relations_by_model_id: causal_model_id=%s",
            causal_model_id,
        )
        slots = await self.find_slots_by_model_id(causal_model_id)
        slot_index: dict[str, Slot] = {s.id: s for s in slots if s.id}
        try:
            result = (
                await self._client.table("causal_relations")
                .select("*")
                .eq("causal_model_id", causal_model_id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load CausalRelations: {exc}") from exc
        relations: list[CausalRelation] = []
        for row in records(result.data):
            source = slot_index.get(row["source_slot_id"])
            target = slot_index.get(row["target_slot_id"])
            if source is None or target is None:
                continue
            relations.append(
                CausalRelation(
                    id=row["id"],
                    identifier=row["identifier"],
                    source=source,
                    target=target,
                    mechanism=row.get("mechanism"),
                    polarity=Polarity(row["polarity"]) if row.get("polarity") else None,
                    epistemic_status=EpistemicStatus(row.get("epistemic_status", "incomplete")),
                )
            )
        return relations

    async def update_relation(self, relation: CausalRelation) -> CausalRelation:
        """Updates mechanism, polarity and epistemic_status of an existing CausalRelation."""
        self.logger.info(
            "SupabaseCausalModelRepository.update_relation: relation_id=%s", relation.id
        )
        try:
            result = await (
                self._client.table("causal_relations")
                .update(
                    {
                        "mechanism": relation.mechanism,
                        "polarity": relation.polarity.value if relation.polarity else None,
                        "epistemic_status": relation.epistemic_status.value,
                    }
                )
                .eq("id", relation.id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to update CausalRelation: {exc}") from exc
        if not result.data:
            raise CausalModelPersistenceError(
                f"Failed to update CausalRelation: no row returned for id={relation.id}"
            )
        return relation

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Deletes a CausalRelation by ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.remove_relation: causal_model_id=%s, relation_id=%s",
            causal_model_id,
            relation_id,
        )
        try:
            await self._client.table("causal_relations").delete().eq("id", relation_id).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to remove CausalRelation: {exc}") from exc
