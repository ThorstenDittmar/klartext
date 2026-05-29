"""Adapter: persists and loads Narratives via Supabase (PostgREST)."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.narrative import (
    ActorNotFoundError,
    NarrativeNotFoundError,
    NarrativePersistenceError,
)
from api.models.narrative import Actor, Narrative, Scene
from api.repositories.narrative_repository import NarrativeRepository

_NARRATIVE_TABLE = "narrative"
_SCENE_TABLE = "narrative_units"
_ACTOR_TABLE = "narrative_actors"
_SCENE_TYPE = "scene"


class SupabaseNarrativeRepository(NarrativeRepository):
    """Reads and writes Narratives and their Scenes using the Supabase PostgREST API."""

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
                .insert({"title": narrative.title})
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
                            "narrative_id": narrative_id,
                            "typ": _SCENE_TYPE,
                            "title": scene.title,
                            "content": scene.text,
                            "position": scene.position,
                        }
                    )
                    .execute()
                )
            except Exception as e:
                raise NarrativePersistenceError(f"Failed to save scene '{scene.title}': {e}") from e

            if not scene_result.data:
                raise NarrativePersistenceError(f"Save returned no data for scene '{scene.title}'.")

            scene_record = scene_result.data[0]
            saved.add_scene(
                Scene.from_record(
                    {
                        "id": scene_record["id"],
                        "title": scene_record["title"],
                        "text": scene_record["content"],
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
            raise NarrativePersistenceError(f"Failed to load narrative {narrative_id}: {e}") from e

        if not narrative_result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        row = narrative_result.data[0]
        narrative = Narrative.from_record(
            {
                "id": row["id"],
                "title": row["title"],
                "causal_model_id": row.get("causal_model_id"),
            }
        )

        try:
            scene_result = (
                await self._client.table(_SCENE_TABLE)
                .select("*")
                .eq("narrative_id", narrative_id)
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
                        "title": scene_row["title"],
                        "text": scene_row["content"],
                        "position": scene_row["position"],
                    }
                )
            )

        try:
            actor_result = (
                await self._client.table(_ACTOR_TABLE)
                .select("*")
                .eq("narrative_id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(
                f"Failed to load actors for narrative {narrative_id}: {e}"
            ) from e

        for actor_row in actor_result.data:
            narrative.add_actor(
                Actor.from_record(
                    {
                        "id": actor_row["id"],
                        "name": actor_row["name"],
                        "typ": actor_row["typ"],
                        "description": actor_row.get("description"),
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
                .select("id, title")
                .order("created_at")
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(f"Failed to list narratives: {e}") from e

        return [
            Narrative.from_record({"id": row["id"], "title": row["title"]}) for row in result.data
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
        narrative_result = (
            await self._client.table(_NARRATIVE_TABLE).select("id").eq("id", narrative_id).execute()
        )
        if not narrative_result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        try:
            scene_result = (
                await self._client.table(_SCENE_TABLE)
                .insert(
                    {
                        "narrative_id": narrative_id,
                        "typ": _SCENE_TYPE,
                        "title": scene.title,
                        "content": scene.text,
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
            raise NarrativePersistenceError(f"Add scene returned no data for '{scene.title}'.")

        row = scene_result.data[0]
        return Scene.from_record(
            {
                "id": row["id"],
                "title": row["title"],
                "text": row["content"],
                "position": row["position"],
            }
        )

    async def add_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Inserts a new Actor row for the given Narrative. Returns the Actor with an assigned ID.

        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseNarrativeRepository.add_actor: narrative_id=%s, name=%s",
            narrative_id,
            actor.name,
        )
        narrative_result = (
            await self._client.table(_NARRATIVE_TABLE).select("id").eq("id", narrative_id).execute()
        )
        if not narrative_result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        try:
            result = (
                await self._client.table(_ACTOR_TABLE)
                .insert(
                    {
                        "narrative_id": narrative_id,
                        "name": actor.name,
                        "typ": actor.typ.value,
                        "description": actor.description,
                    }
                )
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(
                f"Failed to add actor '{actor.name}' to narrative {narrative_id}: {e}"
            ) from e

        if not result.data:
            raise NarrativePersistenceError(f"Add actor returned no data for '{actor.name}'.")

        row = result.data[0]
        return Actor.from_record(
            {
                "id": row["id"],
                "name": row["name"],
                "typ": row["typ"],
                "description": row.get("description"),
            }
        )

    async def get_actor(self, narrative_id: str, actor_id: str) -> Actor:
        """Returns the Actor with the given ID from the Narrative.

        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.debug(
            "SupabaseNarrativeRepository.get_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor_id,
        )
        narrative_result = (
            await self._client.table(_NARRATIVE_TABLE).select("id").eq("id", narrative_id).execute()
        )
        if not narrative_result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        try:
            result = (
                await self._client.table(_ACTOR_TABLE)
                .select("*")
                .eq("id", actor_id)
                .eq("narrative_id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(f"Failed to load actor {actor_id}: {e}") from e

        if not result.data:
            raise ActorNotFoundError(f"Actor not found: {actor_id}")

        row = result.data[0]
        return Actor.from_record(
            {
                "id": row["id"],
                "name": row["name"],
                "typ": row["typ"],
                "description": row.get("description"),
            }
        )

    async def update_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Persists changes to an existing Actor. Returns the updated Actor.

        Raises NarrativePersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseNarrativeRepository.update_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor.id,
        )
        try:
            result = (
                await self._client.table(_ACTOR_TABLE)
                .update(
                    {
                        "name": actor.name,
                        "typ": actor.typ.value,
                        "description": actor.description,
                    }
                )
                .eq("id", actor.id)
                .eq("narrative_id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(f"Failed to update actor {actor.id}: {e}") from e

        if not result.data:
            raise NarrativePersistenceError(f"Update actor returned no data for {actor.id}.")

        row = result.data[0]
        return Actor.from_record(
            {
                "id": row["id"],
                "name": row["name"],
                "typ": row["typ"],
                "description": row.get("description"),
            }
        )

    async def remove_actor(self, narrative_id: str, actor_id: str) -> None:
        """Deletes the Actor with the given ID from the Narrative.

        Raises NarrativePersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseNarrativeRepository.remove_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor_id,
        )
        try:
            await (
                self._client.table(_ACTOR_TABLE)
                .delete()
                .eq("id", actor_id)
                .eq("narrative_id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(f"Failed to remove actor {actor_id}: {e}") from e

    async def link_to_causal_model(self, narrative_id: str, causal_model_id: str) -> Narrative:
        """Updates the causal_model_id column on the Narrative row. Returns the updated Narrative.

        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        Raises NarrativePersistenceError on database failure.
        """
        self.logger.info(
            "SupabaseNarrativeRepository.link_to_causal_model: narrative_id=%s",
            narrative_id,
        )
        try:
            result = (
                await self._client.table(_NARRATIVE_TABLE)
                .update({"causal_model_id": causal_model_id})
                .eq("id", narrative_id)
                .execute()
            )
        except Exception as e:
            raise NarrativePersistenceError(
                f"Failed to link causal model for narrative {narrative_id}: {e}"
            ) from e

        if not result.data:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")

        row = result.data[0]
        return Narrative.from_record(
            {
                "id": row["id"],
                "title": row["title"],
                "causal_model_id": row.get("causal_model_id"),
            }
        )
