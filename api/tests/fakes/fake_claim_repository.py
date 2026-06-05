"""FakeClaimRepository — in-memory ClaimRepository for unit tests."""

from __future__ import annotations

import logging
import uuid

from api.exceptions.claim import ClaimNotFoundError, ClaimPersistenceError
from api.models.claim import Claim
from api.repositories.claim_repository import ClaimRepository


class FakeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository for unit tests.

    Stores claims keyed by scene_id and indexed by claim ID for fast lookup.
    Also supports narrative-level claim storage via _narrative_index.
    """

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._store: dict[str, list[Claim]] = {}  # scene_id → list[Claim]
        self._index: dict[str, Claim] = {}  # claim_id → Claim
        self._narrative_index: dict[str, list[str]] = {}  # narrative_id → list[claim_id]

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

    async def save_for_narrative(self, claims: list[Claim], narrative_id: str) -> list[Claim]:
        """Persists Claims for a Narrative without scene context. Returns claims with IDs."""
        self.logger.info(
            "FakeClaimRepository.save_for_narrative: narrative_id=%s, count=%d",
            narrative_id,
            len(claims),
        )
        if not claims:
            return []
        saved = []
        for claim in claims:
            new_id = str(uuid.uuid4())
            saved_claim = Claim(
                id=new_id,
                label=claim.label,
                text=claim.text,
                typ=claim.typ,
                confidence=claim.confidence,
                status=claim.status,
                wirkgefuege_ref=claim.wirkgefuege_ref,
            )
            self._index[new_id] = saved_claim
            self._narrative_index.setdefault(narrative_id, []).append(new_id)
            saved.append(saved_claim)
        return saved

    async def find_by_narrative_id(self, narrative_id: str) -> list[Claim]:
        """Returns all Claims saved for the given Narrative ID."""
        self.logger.debug("FakeClaimRepository.find_by_narrative_id: narrative_id=%s", narrative_id)
        claim_ids = self._narrative_index.get(narrative_id, [])
        return [self._index[cid] for cid in claim_ids if cid in self._index]
