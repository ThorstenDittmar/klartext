"""FakeNarrativeRepository — in-memory NarrativeRepository for unit tests."""

from __future__ import annotations

import uuid

from api.exceptions.narrative import NarrativeNotFoundError
from api.models.narrative import Narrative, Scene
from api.repositories.narrative_repository import NarrativeRepository


class FakeNarrativeRepository(NarrativeRepository):
    """In-memory NarrativeRepository for unit tests.

    Assigns UUID strings as IDs on save. No database involved.
    """

    def __init__(self) -> None:
        self._store: dict[str, Narrative] = {}

    async def save(self, narrative: Narrative) -> Narrative:
        """Stores the narrative with a generated ID and returns it with IDs assigned."""
        narrative_id = str(uuid.uuid4())
        saved = Narrative(id=narrative_id, title=narrative.title)
        for scene in narrative.scenes:
            saved.add_scene(
                Scene(
                    id=str(uuid.uuid4()),
                    title=scene.title,
                    text=scene.text,
                    position=scene.position,
                )
            )
        self._store[narrative_id] = saved
        return saved

    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Returns the narrative for the given ID. Raises NarrativeNotFoundError if absent."""
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        return self._store[narrative_id]

    async def list_all(self) -> list[Narrative]:
        """Returns all saved narratives as title-only summaries."""
        return [Narrative(id=n.id, title=n.title) for n in self._store.values()]
