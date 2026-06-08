"""Port: defines the contract for persisting and loading NarrativeUnit trees."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.narrative_unit import NarrativeUnit


class NarrativeUnitRepository(ABC):
    """Abstract base class for all NarrativeUnitRepository implementations.

    Concrete adapters (e.g. SupabaseNarrativeUnitRepository) implement data access.
    Tests inject a FakeNarrativeUnitRepository.
    """

    @abstractmethod
    async def load_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Loads the full content tree for the given Narrative.

        Fetches all units in a single query and assembles the tree in Python.
        Returns the root NarrativeUnit (Work) with all descendants attached via
        their .children list, or None if no units exist for this narrative.
        Raises NarrativeUnitPersistenceError on database failure.
        """

    @abstractmethod
    async def add(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Inserts a new NarrativeUnit row.

        Returns the unit with an ID assigned by the database.
        Raises NarrativeUnitPersistenceError on database failure.
        """

    @abstractmethod
    async def update(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Persists changes to title and/or content of an existing NarrativeUnit.

        Returns the updated unit as stored in the database.
        Raises NarrativeUnitNotFoundError if no row exists for unit.id.
        Raises NarrativeUnitPersistenceError on database failure.
        """

    @abstractmethod
    async def remove(self, unit_id: str) -> None:
        """Deletes the NarrativeUnit row with the given ID.

        Descendant rows are removed automatically by ON DELETE CASCADE
        (requires migration 20260608000001_narrative_units_cascade.sql).
        Raises NarrativeUnitPersistenceError on database failure.
        """
