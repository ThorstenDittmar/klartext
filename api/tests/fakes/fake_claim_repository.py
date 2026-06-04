"""FakeClaimRepository — in-memory ClaimRepository for unit tests."""

from __future__ import annotations

import uuid

from api.exceptions.claim import ClaimNotFoundError, ClaimPersistenceError
from api.models.claim import Claim
from api.repositories.claim_repository import ClaimRepository


class FakeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository for unit tests.

    Stores claims keyed by scene_id and indexed by claim ID for fast lookup.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[Claim]] = {}  # scene_id → list[Claim]
        self._index: dict[str, Claim] = {}  # claim_id → Claim

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Assigns a new UUID to each claim and stores them under the given scene_id."""
        saved = [
            Claim(
                id=str(uuid.uuid4()),
                label=c.label,
                text=c.text,
                typ=c.typ,
                confidence=c.confidence,
                status=c.status,
                wirkgefuege_ref=c.wirkgefuege_ref,
            )
            for c in claims
        ]
        self._store[scene_id] = saved
        for claim in saved:
            self._index[claim.id] = claim  # type: ignore[index]
        return saved

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns the claims for the given scene, or an empty list if none exist."""
        return self._store.get(scene_id, [])

    async def find_by_id(self, claim_id: str) -> Claim:
        """Returns the Claim with the given ID. Raises ClaimNotFoundError if absent."""
        if claim_id not in self._index:
            raise ClaimNotFoundError(f"Claim not found: {claim_id}")
        return self._index[claim_id]

    async def update(self, claim: Claim) -> Claim:
        """Persists the current state of a Claim by replacing both index and store entries."""
        if claim.id not in self._index:
            raise ClaimPersistenceError(f"Claim not found for update: {claim.id}")
        self._index[claim.id] = claim  # type: ignore[index]
        # keep _store consistent
        for claims_list in self._store.values():
            for i, c in enumerate(claims_list):
                if c.id == claim.id:
                    claims_list[i] = claim
                    break
        return claim
