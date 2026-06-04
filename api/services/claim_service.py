"""ClaimService — business logic for Claim lifecycle operations."""

from __future__ import annotations

from api.models.claim import Claim
from api.repositories.claim_repository import ClaimRepository


class ClaimService:
    """Orchestrates Claim persistence and lifecycle changes."""

    def __init__(self, repository: ClaimRepository) -> None:
        self._repository = repository

    async def link_to_wirkgefuege(self, claim_id: str, wirkgefuege_ref: str) -> Claim:
        """Links a Claim to a Wirkgefüge component by reference ID.

        Sets the Claim's status to LINKED and stores the wirkgefuege_ref.
        Raises ClaimNotFoundError if no Claim exists for that ID.
        """
        claim = await self._repository.find_by_id(claim_id)
        claim.link_to_wirkgefuege(wirkgefuege_ref)
        return await self._repository.update(claim)
