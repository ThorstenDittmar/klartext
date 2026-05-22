"""SupabaseWirkmodellRepository — Supabase adapter for Wirkmodell persistence."""

from __future__ import annotations

from supabase import AsyncClient

from api.exceptions.wirkmodell import WirkmodellNotFoundError, WirkmodellPersistenceError
from api.models.wirkmodell import Axiom, Wirkmodell
from api.repositories.wirkmodell_repository import WirkmodellRepository


class SupabaseWirkmodellRepository(WirkmodellRepository):
    """Adapter — persists Wirkmodelle and Axiome in Supabase.

    Table mapping:
      wirkmodelle  →  Wirkmodell (id, titel, status)
      modellelemente (typ='axiom', ist_axiomatisch=True)  →  Axiom (id, label, beschreibung)
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, wirkmodell: Wirkmodell) -> Wirkmodell:
        """Inserts the Wirkmodell and all its Axiome. Returns both with IDs assigned."""
        try:
            result = await self._client.table("wirkmodelle").insert({
                "titel": wirkmodell.titel,
                "status": wirkmodell.status.value,
            }).execute()
        except Exception as exc:
            raise WirkmodellPersistenceError(f"Failed to save Wirkmodell: {exc}") from exc

        row = result.data[0]
        saved = Wirkmodell.from_record(row)

        for axiom in wirkmodell.axiome:
            saved_axiom = await self.add_axiom(saved.id, axiom)  # type: ignore[arg-type]
            saved.add_axiom(saved_axiom)

        return saved

    async def add_axiom(self, wirkmodell_id: str, axiom: Axiom) -> Axiom:
        """Inserts an Axiom as a Modellelement and returns it with an ID."""
        try:
            result = await self._client.table("modellelemente").insert({
                "wirkmodell_id": wirkmodell_id,
                "typ": "axiom",
                "label": axiom.label,
                "beschreibung": axiom.beschreibung,
                "ist_axiomatisch": True,
            }).execute()
        except Exception as exc:
            raise WirkmodellPersistenceError(f"Failed to save Axiom: {exc}") from exc

        row = result.data[0]
        return Axiom.from_record({
            "id": row["id"],
            "label": row["label"],
            "beschreibung": row["beschreibung"],
        })

    async def find_by_id(self, wirkmodell_id: str) -> Wirkmodell:
        """Loads the Wirkmodell and all its Axiome from Supabase."""
        try:
            wm_result = await self._client.table("wirkmodelle").select("*").eq(
                "id", wirkmodell_id
            ).execute()
        except Exception as exc:
            raise WirkmodellPersistenceError(f"Failed to load Wirkmodell: {exc}") from exc

        if not wm_result.data:
            raise WirkmodellNotFoundError(f"Wirkmodell not found: {wirkmodell_id}")

        wm = Wirkmodell.from_record(wm_result.data[0])

        try:
            axiom_result = await self._client.table("modellelemente").select("*").eq(
                "wirkmodell_id", wirkmodell_id
            ).eq("typ", "axiom").execute()
        except Exception as exc:
            raise WirkmodellPersistenceError(f"Failed to load Axiome: {exc}") from exc

        for row in axiom_result.data:
            wm.add_axiom(Axiom.from_record({
                "id": row["id"],
                "label": row["label"],
                "beschreibung": row["beschreibung"],
            }))

        return wm

    async def list_all(self) -> list[Wirkmodell]:
        """Returns all Wirkmodelle as title-only summaries."""
        try:
            result = await self._client.table("wirkmodelle").select("id, titel, status").execute()
        except Exception as exc:
            raise WirkmodellPersistenceError(f"Failed to list Wirkmodelle: {exc}") from exc

        return [Wirkmodell.from_record(row) for row in result.data]
