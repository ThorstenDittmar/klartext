"""FakeWirkmodellRepository — in-memory WirkmodellRepository for unit tests."""

from __future__ import annotations

import uuid

from api.exceptions.wirkmodell import WirkmodellNotFoundError
from api.models.wirkmodell import Axiom, Wirkmodell
from api.repositories.wirkmodell_repository import WirkmodellRepository


class FakeWirkmodellRepository(WirkmodellRepository):
    """In-memory WirkmodellRepository for unit tests.

    Assigns UUID strings as IDs on save. No database involved.
    """

    def __init__(self) -> None:
        self._store: dict[str, Wirkmodell] = {}

    async def save(self, wirkmodell: Wirkmodell) -> Wirkmodell:
        """Stores the Wirkmodell with a generated ID and returns it with IDs assigned."""
        wm_id = str(uuid.uuid4())
        saved = Wirkmodell(id=wm_id, titel=wirkmodell.titel, status=wirkmodell.status)
        for axiom in wirkmodell.axiome:
            saved.add_axiom(Axiom(id=str(uuid.uuid4()), label=axiom.label, beschreibung=axiom.beschreibung))
        self._store[wm_id] = saved
        return saved

    async def add_axiom(self, wirkmodell_id: str, axiom: Axiom) -> Axiom:
        """Adds an Axiom to the stored Wirkmodell and returns it with an ID."""
        if wirkmodell_id not in self._store:
            raise WirkmodellNotFoundError(f"Wirkmodell not found: {wirkmodell_id}")
        saved_axiom = Axiom(id=str(uuid.uuid4()), label=axiom.label, beschreibung=axiom.beschreibung)
        self._store[wirkmodell_id].add_axiom(saved_axiom)
        return saved_axiom

    async def find_by_id(self, wirkmodell_id: str) -> Wirkmodell:
        """Returns the Wirkmodell with its Axiome. Raises WirkmodellNotFoundError if absent."""
        if wirkmodell_id not in self._store:
            raise WirkmodellNotFoundError(f"Wirkmodell not found: {wirkmodell_id}")
        return self._store[wirkmodell_id]

    async def list_all(self) -> list[Wirkmodell]:
        """Returns all Wirkmodelle as title-only summaries."""
        return [Wirkmodell(id=wm.id, titel=wm.titel, status=wm.status) for wm in self._store.values()]
