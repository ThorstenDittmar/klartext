"""Adapter: persists and loads Claims via Supabase (PostgREST)."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.claim import ClaimNotFoundError, ClaimPersistenceError
from api.models.claim import Claim
from api.repositories._supabase import records
from api.repositories.claim_repository import ClaimRepository

_CLAIM_TABLE = "claims"


class SupabaseClaimRepository(ClaimRepository):
    """Reads and writes Claims using the Supabase PostgREST API.

    Claims are stored in the 'claims' table and keyed by scene_id.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Inserts all Claims for the given scene. Returns Claims with assigned IDs.

        An empty input list is valid and returns an empty list immediately.
        Raises ClaimPersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseClaimRepository.save_all: scene_id=%s, count=%d",
            scene_id,
            len(claims),
        )
        if not claims:
            return []

        rows = [
            {
                "scene_id": scene_id,
                "label": claim.label,
                "text": claim.text,
                "typ": claim.typ.value,
                "confidence": claim.confidence,
                "status": claim.status.value,
                "wirkgefuege_ref": claim.wirkgefuege_ref,
            }
            for claim in claims
        ]

        try:
            result = await self._client.table(_CLAIM_TABLE).insert(rows).execute()
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to save claims for scene {scene_id}: {e}") from e

        if not result.data:
            raise ClaimPersistenceError(f"Save returned no data for claims of scene {scene_id}.")

        return [Claim.from_record(row) for row in records(result.data)]

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns all Claims stored for the given scene ID.

        Returns an empty list when no claims exist for that scene.
        Raises ClaimPersistenceError on database failure.
        """
        self.logger.debug("SupabaseClaimRepository.find_by_scene_id: scene_id=%s", scene_id)
        try:
            result = (
                await self._client.table(_CLAIM_TABLE)
                .select("*")
                .eq("scene_id", scene_id)
                .execute()
            )
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to load claims for scene {scene_id}: {e}") from e

        return [Claim.from_record(row) for row in records(result.data)]

    async def find_by_id(self, claim_id: str) -> Claim:
        """Returns the Claim with the given ID. Raises ClaimNotFoundError if absent."""
        self.logger.debug("SupabaseClaimRepository.find_by_id: claim_id=%s", claim_id)
        try:
            result = await self._client.table(_CLAIM_TABLE).select("*").eq("id", claim_id).execute()
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to load claim {claim_id}: {e}") from e
        if not result.data:
            raise ClaimNotFoundError(f"Claim not found: {claim_id}")
        return Claim.from_record(records(result.data)[0])

    async def update(self, claim: Claim) -> Claim:
        """Updates status and wirkgefuege_ref of an existing Claim."""
        self.logger.info("SupabaseClaimRepository.update: claim_id=%s", claim.id)
        try:
            result = (
                await self._client.table(_CLAIM_TABLE)
                .update(
                    {
                        "status": claim.status.value,
                        "wirkgefuege_ref": claim.wirkgefuege_ref,
                    }
                )
                .eq("id", claim.id)
                .execute()
            )
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to update claim {claim.id}: {e}") from e
        if not result.data:
            raise ClaimPersistenceError(f"Update returned no data for claim {claim.id}")
        return Claim.from_record(records(result.data)[0])

    async def save_for_narrative(self, claims: list[Claim], narrative_id: str) -> list[Claim]:
        """Inserts Claims for a Narrative without scene context. Returns claims with IDs.

        Raises ClaimPersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseClaimRepository.save_for_narrative: narrative_id=%s, count=%d",
            narrative_id,
            len(claims),
        )
        if not claims:
            return []

        rows = [
            {
                "narrative_id": narrative_id,
                "label": claim.label,
                "text": claim.text,
                "typ": claim.typ.value,
                "confidence": claim.confidence,
                "status": claim.status.value,
                "wirkgefuege_ref": claim.wirkgefuege_ref,
            }
            for claim in claims
        ]

        try:
            result = await self._client.table(_CLAIM_TABLE).insert(rows).execute()
        except Exception as e:
            raise ClaimPersistenceError(
                f"Failed to save claims for narrative {narrative_id}: {e}"
            ) from e

        if not result.data:
            raise ClaimPersistenceError(
                f"Save returned no data for claims of narrative {narrative_id}."
            )

        return [Claim.from_record(row) for row in records(result.data)]

    async def find_by_narrative_id(self, narrative_id: str) -> list[Claim]:
        """Returns all Claims stored for the given Narrative ID.

        Returns an empty list when no claims exist.
        Raises ClaimPersistenceError on database failure.
        """
        self.logger.debug(
            "SupabaseClaimRepository.find_by_narrative_id: narrative_id=%s", narrative_id
        )
        try:
            result = (
                await self._client.table(_CLAIM_TABLE)
                .select("*")
                .eq("narrative_id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise ClaimPersistenceError(
                f"Failed to load claims for narrative {narrative_id}: {e}"
            ) from e

        return [Claim.from_record(row) for row in records(result.data)]
