"""Adapter: persists and loads Claims via Supabase (PostgREST)."""

from __future__ import annotations

from supabase import AsyncClient

from api.exceptions.claim import ClaimPersistenceError
from api.models.claim import Claim
from api.repositories.claim_repository import ClaimRepository

_CLAIM_TABLE = "claims"


class SupabaseClaimRepository(ClaimRepository):
    """Reads and writes Claims using the Supabase PostgREST API.

    Claims are stored in the 'claims' table and keyed by scene_id
    (which references narrative_einheiten.id).
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Inserts all Claims for the given scene. Returns Claims with assigned IDs.

        An empty input list is valid and returns an empty list immediately.
        Raises ClaimPersistenceError on database failure.
        """
        if not claims:
            return []

        rows = [
            {
                "scene_id": scene_id,
                "text": claim.text,
                "typ": claim.typ.value,
                "confidence": claim.confidence,
            }
            for claim in claims
        ]

        try:
            result = await self._client.table(_CLAIM_TABLE).insert(rows).execute()
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to save claims for scene {scene_id}: {e}") from e

        if not result.data:
            raise ClaimPersistenceError(f"Save returned no data for claims of scene {scene_id}.")

        return [Claim.from_record(row) for row in result.data]

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns all Claims stored for the given scene ID.

        Returns an empty list when no claims exist for that scene.
        Raises ClaimPersistenceError on database failure.
        """
        try:
            result = (
                await self._client.table(_CLAIM_TABLE)
                .select("*")
                .eq("scene_id", scene_id)
                .execute()
            )
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to load claims for scene {scene_id}: {e}") from e

        return [Claim.from_record(row) for row in result.data]
