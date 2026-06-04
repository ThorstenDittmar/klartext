"""FakeClaimRepository — in-memory ClaimRepository for unit tests."""

from __future__ import annotations

import uuid

from api.models.claim import Claim
from api.repositories.claim_repository import ClaimRepository


class FakeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository for unit tests.

    Stores claims keyed by scene_id. Assigns UUID strings as IDs on save.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[Claim]] = {}

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
        return saved

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns the claims for the given scene, or an empty list if none exist."""
        return self._store.get(scene_id, [])
