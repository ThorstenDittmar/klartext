"""SupabaseCausalModelRepository — Supabase adapter for CausalModel persistence."""

from __future__ import annotations

from supabase import AsyncClient

from api.exceptions.causal_model import CausalModelNotFoundError, CausalModelPersistenceError
from api.models.causal_model import Axiom, CausalModel
from api.repositories.causal_model_repository import CausalModelRepository


class SupabaseCausalModelRepository(CausalModelRepository):
    """Adapter — persists CausalModels and Axioms in Supabase.

    Table mapping:
      wirkmodelle  →  CausalModel (id, title, status)
      modellelemente (typ='axiom', ist_axiomatisch=True)  →  Axiom (id, label, description)
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, causal_model: CausalModel) -> CausalModel:
        """Inserts the CausalModel and all its Axioms. Returns both with IDs assigned."""
        try:
            result = await self._client.table("wirkmodelle").insert({
                "title": causal_model.title,
                "status": causal_model.status.value,
            }).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save CausalModel: {exc}") from exc

        row = result.data[0]
        saved = CausalModel.from_record(row)

        for axiom in causal_model.axioms:
            saved_axiom = await self.add_axiom(saved.id, axiom)  # type: ignore[arg-type]
            saved.add_axiom(saved_axiom)

        return saved

    async def add_axiom(self, causal_model_id: str, axiom: Axiom) -> Axiom:
        """Inserts an Axiom as a model element and returns it with an ID."""
        try:
            result = await self._client.table("modellelemente").insert({
                "wirkmodell_id": causal_model_id,
                "typ": "axiom",
                "label": axiom.label,
                "beschreibung": axiom.description,
                "ist_axiomatisch": True,
            }).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save Axiom: {exc}") from exc

        row = result.data[0]
        return Axiom.from_record({
            "id": row["id"],
            "label": row["label"],
            "beschreibung": row["beschreibung"],
        })

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Loads the CausalModel and all its Axioms from Supabase."""
        try:
            cm_result = await self._client.table("wirkmodelle").select("*").eq(
                "id", causal_model_id
            ).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load CausalModel: {exc}") from exc

        if not cm_result.data:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")

        cm = CausalModel.from_record(cm_result.data[0])

        try:
            axiom_result = await self._client.table("modellelemente").select("*").eq(
                "wirkmodell_id", causal_model_id
            ).eq("typ", "axiom").execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load Axioms: {exc}") from exc

        for row in axiom_result.data:
            cm.add_axiom(Axiom.from_record({
                "id": row["id"],
                "label": row["label"],
                "beschreibung": row["beschreibung"],
            }))

        return cm

    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries."""
        try:
            result = await self._client.table("wirkmodelle").select("id, title, status").execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to list CausalModels: {exc}") from exc

        return [CausalModel.from_record(row) for row in result.data]
