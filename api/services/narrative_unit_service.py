"""NarrativeUnitService: business logic for the narrative content tree."""

from __future__ import annotations

from api.models.narrative_unit import NarrativeUnit
from api.repositories.narrative_unit_repository import NarrativeUnitRepository


class NarrativeUnitService:
    """Coordinates NarrativeUnit operations via the repository port."""

    def __init__(self, repository: NarrativeUnitRepository) -> None:
        self._repository = repository

    async def get_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Returns the fully assembled content tree for the narrative.

        Returns None if no units have been created for this narrative yet.
        """
        return await self._repository.load_tree(narrative_id)

    async def add_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Persists a new NarrativeUnit. Returns the unit with an assigned ID."""
        return await self._repository.add(unit)

    async def update_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Persists changes to an existing NarrativeUnit. Returns the updated unit."""
        return await self._repository.update(unit)

    async def remove_unit(self, unit_id: str) -> None:
        """Removes the unit and all its descendants (via ON DELETE CASCADE)."""
        await self._repository.remove(unit_id)
