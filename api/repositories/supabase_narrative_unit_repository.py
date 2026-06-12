"""Adapter: persists and loads NarrativeUnit trees via Supabase (PostgREST)."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.narrative_unit import (
    NarrativeUnitNotFoundError,
    NarrativeUnitPersistenceError,
)
from api.models.narrative_unit import NarrativeUnit
from api.repositories._supabase import records
from api.repositories.narrative_unit_repository import NarrativeUnitRepository

_TABLE = "narrative_units"


class SupabaseNarrativeUnitRepository(NarrativeUnitRepository):
    """Reads and writes NarrativeUnit trees using the Supabase PostgREST API.

    Tree assembly algorithm:
    1. Fetch all rows for the narrative in a single SELECT ordered by position.
    2. Build a flat dict: unit_id → NarrativeUnit.
    3. Walk the dict — nodes with parent_id are attached to their parent;
       the node with typ='work' is the root.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def load_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Fetches all units and assembles the tree in Python. Returns root or None."""
        self.logger.debug(
            "SupabaseNarrativeUnitRepository.load_tree: narrative_id=%s", narrative_id
        )
        try:
            result = (
                await self._client.table(_TABLE)
                .select("*")
                .eq("narrative_id", narrative_id)
                .order("position")
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(
                f"Failed to load tree for narrative {narrative_id}: {e}"
            ) from e

        rows = records(result.data)
        if not rows:
            return None

        units: dict[str, NarrativeUnit] = {}
        for row in rows:
            unit = NarrativeUnit.from_record(row)
            if unit.id:
                units[unit.id] = unit

        # Attach children to parents; identify root by typ='work' to avoid
        # treating legacy Phase-1 scenes (parent_id=NULL) as roots.
        root: NarrativeUnit | None = None
        for unit in units.values():
            if unit.parent_id is None and unit.typ == "work":
                root = unit
            elif unit.parent_id is not None:
                parent = units.get(unit.parent_id)
                if parent is not None:
                    parent.add_child(unit)

        return root

    async def add(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Inserts a NarrativeUnit row. Returns the unit with an assigned ID."""
        self.logger.info(
            "SupabaseNarrativeUnitRepository.add: narrative_id=%s, typ=%s",
            unit.narrative_id,
            unit.typ,
        )
        try:
            result = (
                await self._client.table(_TABLE)
                .insert(
                    {
                        "narrative_id": unit.narrative_id,
                        "typ": unit.typ,
                        "title": unit.title,
                        "content": unit.content,
                        "position": unit.position,
                        "parent_id": unit.parent_id,
                    }
                )
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(f"Failed to add narrative unit: {e}") from e

        if not result.data:
            raise NarrativeUnitPersistenceError("Add narrative unit returned no data.")

        row = records(result.data)[0]
        return NarrativeUnit.from_record(row)

    async def update(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Updates title and content of the unit. Returns the updated row."""
        self.logger.info("SupabaseNarrativeUnitRepository.update: unit_id=%s", unit.id)
        try:
            result = (
                await self._client.table(_TABLE)
                .update({"title": unit.title, "content": unit.content})
                .eq("id", unit.id)
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(
                f"Failed to update narrative unit {unit.id}: {e}"
            ) from e

        if not result.data:
            raise NarrativeUnitNotFoundError(f"Narrative unit not found: {unit.id}")

        row = records(result.data)[0]
        return NarrativeUnit.from_record(row)

    async def remove(self, unit_id: str) -> None:
        """Deletes the unit row. Descendants removed by ON DELETE CASCADE.

        Raises NarrativeUnitNotFoundError if no row exists for unit_id.
        """
        self.logger.info("SupabaseNarrativeUnitRepository.remove: unit_id=%s", unit_id)
        try:
            result = await self._client.table(_TABLE).delete().eq("id", unit_id).execute()
        except Exception as e:
            raise NarrativeUnitPersistenceError(
                f"Failed to remove narrative unit {unit_id}: {e}"
            ) from e
        if not result.data:
            raise NarrativeUnitNotFoundError(f"Narrative unit not found: {unit_id}")
