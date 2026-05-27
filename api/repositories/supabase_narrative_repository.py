"""Adapter: persists and loads Narratives via Supabase (PostgREST)."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.narrative import NarrativeNotFoundError, NarrativePersistenceError
from api.models.narrative import Narrative, Scene
from api.repositories.narrative_repository import NarrativeRepository

_NARRATIVE_TABLE = "narrative"
_SCENE_TABLE = "narrative_einheiten"
_SCENE_TYPE = "szene"


class SupabaseNarrativeRepository(NarrativeRepository):
    """Reads and writes Narratives and their Scenes using the Supabase PostgREST API.

    Column mapping (DB uses German names):
      narrative.titel       → Narrative.title
      narrative_einheiten.titel  → Scene.title
      narrative_einheiten.inhalt → Scene.text
    """

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, narrative: Narrative) -> Narrative:
        """Inserts the Narrative row and all Scene rows. Returns the Narrative with assigned IDs.

        Raises NarrativePersistenceError on database failure.
        """
        self.logger.info("SupabaseNarrativeRepository.save: title=%s", narrative.title)
        try:
            narrative_result = (
                await self._client.table(_NARRATIVE_TABLE)
                .insert({"titel": narrative.title})
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(f"Failed to save narrative: {e}") from e

        if not narrative_result.data:
            raise NarrativePersistenceError("Save returned no data for narrative.")

        narrative_id: str = narrative_result.data[0]["id"]
        saved = Narrative(id=narrative_id, title=narrative.title)

        for scene in narrative.scenes:
            try:
                scene_result = (
                    await self._client.table(_SCENE_TABLE)
                    .insert(
                        {
                            "narrativ_id": narrative_id,
                            "typ": _SCENE_TYPE,
                            "titel": scene.title,
                            "inhalt": scene.text,
                            "position": scene.position,
                        }
                    )
                    .execute()
                )
            except Exception as e:
                raise NarrativePersistenceError(
                    f"Failed to save scene '{scene.title}': {e}"
                ) from e

            if not scene_result.data:
                raise NarrativePersistenceError(
                    f"Save returned no data for scene '{scene.title}'."
                )

            scene_record = scene_result.data[0]
            saved.add_scene(
                Scene.from_record(
                    {
                        "id": scene_record["id"],
                        "title": scene_record["titel"],
                        "text": scene_record["inhalt"],
                        "position": scene_record["position"],
                    }
                )
            )

        return saved

    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Loads the Narrative and all its Scenes from the database.

        Raises NarrativeNotFoundError if no row exists for the given ID.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.debug("SupabaseNarrativeRepository.find_by_id: narrative_id=%s", narrative_id)
        try:
            narrative_result = (
                await self._client.table(_NARRATIVE_TABLE)
                .select("*")
                .eq("id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(
                f"Failed to load narrative {narrative_id}: {e}"
            ) from e

        if not narrative_result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        row = narrative_result.data[0]
        narrative = Narrative.from_record({"id": row["id"], "title": row["titel"]})

        try:
            scene_result = (
                await self._client.table(_SCENE_TABLE)
                .select("*")
                .eq("narrativ_id", narrative_id)
                .eq("typ", _SCENE_TYPE)
                .order("position")
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(
                f"Failed to load scenes for narrative {narrative_id}: {e}"
            ) from e

        for scene_row in scene_result.data:
            narrative.add_scene(
                Scene.from_record(
                    {
                        "id": scene_row["id"],
                        "title": scene_row["titel"],
                        "text": scene_row["inhalt"],
                        "position": scene_row["position"],
                    }
                )
            )

        return narrative

    async def list_all(self) -> list[Narrative]:
        """Returns all Narrative rows without their scenes.

        Raises NarrativePersistenceError on database failure.
        """
        self.logger.debug("SupabaseNarrativeRepository.list_all")
        try:
            result = (
                await self._client.table(_NARRATIVE_TABLE)
                .select("id, titel")
                .order("created_at")
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(f"Failed to list narratives: {e}") from e

        return [
            Narrative.from_record({"id": row["id"], "title": row["titel"]})
            for row in result.data
        ]

    async def add_scene(self, narrative_id: str, scene: Scene) -> Scene:
        """Inserts a new Scene row for the given Narrative. Returns the Scene with an assigned ID.

        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseNarrativeRepository.add_scene: narrative_id=%s, title=%s",
            narrative_id,
            scene.title,
        )
        # Verify the narrative exists before inserting the scene.
        narrative_result = await self._client.table(_NARRATIVE_TABLE).select("id").eq("id", narrative_id).execute()
        if not narrative_result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        try:
            scene_result = (
                await self._client.table(_SCENE_TABLE)
                .insert(
                    {
                        "narrativ_id": narrative_id,
                        "typ": _SCENE_TYPE,
                        "titel": scene.title,
                        "inhalt": scene.text,
                        "position": scene.position,
                    }
                )
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(
                f"Failed to add scene '{scene.title}' to narrative {narrative_id}: {e}"
            ) from e

        if not scene_result.data:
            raise NarrativePersistenceError(
                f"Add scene returned no data for '{scene.title}'."
            )

        row = scene_result.data[0]
        return Scene.from_record(
            {
                "id": row["id"],
                "title": row["titel"],
                "text": row["inhalt"],
                "position": row["position"],
            }
        )
