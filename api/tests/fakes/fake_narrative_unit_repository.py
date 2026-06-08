"""In-memory NarrativeUnitRepository for unit and service tests.

Does NOT simulate ON DELETE CASCADE — use only for tests that don't
test multi-node deletion.
"""

from __future__ import annotations

import uuid

from api.models.narrative_unit import NarrativeUnit
from api.repositories.narrative_unit_repository import NarrativeUnitRepository


def _clone_with_id(unit: NarrativeUnit) -> NarrativeUnit:
    """Returns a new instance of the same concrete type with a fresh UUID."""
    return unit.__class__(
        id=str(uuid.uuid4()),
        title=unit.title,
        content=unit.content,
        position=unit.position,
        narrative_id=unit.narrative_id,
        parent_id=unit.parent_id,
    )


class FakeNarrativeUnitRepository(NarrativeUnitRepository):
    """Stores trees and units in plain dicts for fast, isolated tests."""

    def __init__(self) -> None:
        self._trees: dict[str, NarrativeUnit] = {}  # narrative_id → root
        self._units: dict[str, NarrativeUnit] = {}  # unit_id → unit

    def set_tree(self, narrative_id: str, root: NarrativeUnit) -> None:
        """Pre-seeds a tree for a narrative. Call from test setUp before the subject."""
        self._trees[narrative_id] = root

    def set_unit(self, unit: NarrativeUnit) -> None:
        """Registers an individual unit by ID for update/remove tests."""
        if unit.id:
            self._units[unit.id] = unit

    async def load_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Returns the pre-seeded root node, or None."""
        return self._trees.get(narrative_id)

    async def add(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Clones the unit with a new UUID, stores and returns it."""
        saved = _clone_with_id(unit)
        assert saved.id is not None
        self._units[saved.id] = saved
        return saved

    async def update(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Stores the updated unit and returns it unchanged."""
        assert unit.id is not None
        self._units[unit.id] = unit
        return unit

    async def remove(self, unit_id: str) -> None:
        """Removes the unit from the store. Silent no-op for unknown IDs."""
        self._units.pop(unit_id, None)
