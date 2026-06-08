"""Tests for the NarrativeRepository contract.

All unit tests run against FakeNarrativeRepository, which verifies the
contract itself. The SupabaseNarrativeRepository must satisfy the same
contract; those tests are marked @pytest.mark.integration.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative import ActorNotFoundError, NarrativeNotFoundError
from api.models.narrative import ActorType
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from tests.mothers.narrative_mother import NarrativeMother

# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_repository_save_assigns_id_to_narrative() -> None:
    """Expects the saved narrative to have a non-None ID assigned by the repository."""
    repo = FakeNarrativeRepository()

    saved = await repo.save(NarrativeMother.empty())

    assert saved.id is not None


@pytest.mark.asyncio
async def test_narrative_repository_save_assigns_ids_to_all_scenes() -> None:
    """Expects every scene in the saved narrative to have a non-None ID."""
    repo = FakeNarrativeRepository()

    saved = await repo.save(NarrativeMother.with_two_scenes())

    assert all(scene.id is not None for scene in saved.scenes)


@pytest.mark.asyncio
async def test_narrative_repository_save_works_for_narrative_without_scenes() -> None:
    """Expects save to succeed even when the narrative has no scenes."""
    repo = FakeNarrativeRepository()

    saved = await repo.save(NarrativeMother.empty())

    assert saved.id is not None
    assert saved.scenes == []


@pytest.mark.asyncio
async def test_narrative_repository_find_by_id_returns_saved_narrative() -> None:
    """Expects find_by_id to return the same narrative that was saved."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.empty())

    found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.id == saved.id
    assert found.title == "Klartext"


@pytest.mark.asyncio
async def test_narrative_repository_find_by_id_returns_narrative_with_scenes() -> None:
    """Expects find_by_id to return the narrative together with all its scenes."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_two_scenes())

    found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

    assert len(found.scenes) == 2
    assert found.scenes[0].title == "Szene 1"
    assert found.scenes[1].title == "Szene 2"


@pytest.mark.asyncio
async def test_narrative_repository_list_all_returns_all_saved_narratives() -> None:
    """Expects list_all to include every narrative that was previously saved."""
    repo = FakeNarrativeRepository()
    for narrative in NarrativeMother.collection():
        await repo.save(narrative)

    all_narratives = await repo.list_all()

    titles = {n.title for n in all_narratives}
    assert titles == {"Erstes Narrativ", "Zweites Narrativ", "Drittes Narrativ"}


@pytest.mark.asyncio
async def test_narrative_repository_list_all_returns_empty_list_when_empty() -> None:
    """Expects list_all to return an empty list when no narratives have been saved."""
    repo = FakeNarrativeRepository()

    all_narratives = await repo.list_all()

    assert all_narratives == []


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_repository_find_by_id_raises_for_unknown_id() -> None:
    """Expects NarrativeNotFoundError when no narrative exists for the given ID."""
    repo = FakeNarrativeRepository()

    with pytest.raises(NarrativeNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000000")


# ---------------------------------------------------------------------------
# add_actor / get_actor / update_actor / remove_actor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_repository_add_actor_assigns_id() -> None:
    """Expects the saved actor to have a non-None ID assigned by the repository."""
    repo = FakeNarrativeRepository()
    saved_narrative = await repo.save(NarrativeMother.empty())

    from api.models.narrative import Actor

    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)
    saved_actor = await repo.add_actor(saved_narrative.id, actor)  # type: ignore[arg-type]

    assert saved_actor.id is not None


@pytest.mark.asyncio
async def test_narrative_repository_add_actor_stores_label_and_actor_type() -> None:
    """Expects label and actor_type to be accessible on the saved actor."""
    repo = FakeNarrativeRepository()
    saved_narrative = await repo.save(NarrativeMother.empty())

    from api.models.narrative import Actor

    actor = Actor.create(label="CDU", actor_type=ActorType.ORGANISATION)
    saved_actor = await repo.add_actor(saved_narrative.id, actor)  # type: ignore[arg-type]

    assert saved_actor.label == "CDU"
    assert saved_actor.actor_type == ActorType.ORGANISATION


@pytest.mark.asyncio
async def test_narrative_repository_add_actor_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    repo = FakeNarrativeRepository()

    from api.models.narrative import Actor

    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)

    with pytest.raises(NarrativeNotFoundError):
        await repo.add_actor("00000000-0000-0000-0000-000000000000", actor)


@pytest.mark.asyncio
async def test_narrative_repository_get_actor_returns_saved_actor() -> None:
    """Expects get_actor to return the actor that was previously added."""
    repo = FakeNarrativeRepository()
    saved_narrative = await repo.save(NarrativeMother.empty())

    from api.models.narrative import Actor

    saved_actor = await repo.add_actor(
        saved_narrative.id, Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)
    )  # type: ignore[arg-type]
    found = await repo.get_actor(saved_narrative.id, saved_actor.id)  # type: ignore[arg-type]

    assert found.id == saved_actor.id
    assert found.label == "Max"


@pytest.mark.asyncio
async def test_narrative_repository_get_actor_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    repo = FakeNarrativeRepository()

    with pytest.raises(NarrativeNotFoundError):
        await repo.get_actor("00000000-0000-0000-0000-000000000000", "actor-id")


@pytest.mark.asyncio
async def test_narrative_repository_get_actor_raises_for_unknown_actor() -> None:
    """Expects ActorNotFoundError when the actor does not exist in the narrative."""
    repo = FakeNarrativeRepository()
    saved_narrative = await repo.save(NarrativeMother.empty())

    with pytest.raises(ActorNotFoundError):
        await repo.get_actor(saved_narrative.id, "00000000-0000-0000-0000-000000000000")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_narrative_repository_update_actor_returns_updated_actor() -> None:
    """Expects update_actor to return the actor with the new label and actor_type."""
    repo = FakeNarrativeRepository()
    saved_narrative = await repo.save(NarrativeMother.empty())

    from api.models.narrative import Actor

    saved_actor = await repo.add_actor(
        saved_narrative.id, Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)
    )  # type: ignore[arg-type]
    saved_actor.update(label="CDU", actor_type=ActorType.ORGANISATION, notes="A party.")
    updated = await repo.update_actor(saved_narrative.id, saved_actor)  # type: ignore[arg-type]

    assert updated.label == "CDU"
    assert updated.actor_type == ActorType.ORGANISATION
    assert updated.notes == "A party."


@pytest.mark.asyncio
async def test_narrative_repository_remove_actor_removes_actor() -> None:
    """Expects the actor to be absent after remove_actor is called."""
    repo = FakeNarrativeRepository()
    saved_narrative = await repo.save(NarrativeMother.empty())

    from api.models.narrative import Actor

    saved_actor = await repo.add_actor(
        saved_narrative.id, Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)
    )  # type: ignore[arg-type]
    await repo.remove_actor(saved_narrative.id, saved_actor.id)  # type: ignore[arg-type]

    with pytest.raises(ActorNotFoundError):
        await repo.get_actor(saved_narrative.id, saved_actor.id)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# link_to_causal_model
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_repository_link_to_causal_model_stores_id() -> None:
    """Expects the causal_model_id to be returned on the narrative after linking."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.empty())

    updated = await repo.link_to_causal_model(saved.id, "model-xyz")  # type: ignore[arg-type]

    assert updated.causal_model_id == "model-xyz"


@pytest.mark.asyncio
async def test_narrative_repository_link_to_causal_model_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    repo = FakeNarrativeRepository()

    with pytest.raises(NarrativeNotFoundError):
        await repo.link_to_causal_model("00000000-0000-0000-0000-000000000000", "model-xyz")


# ---------------------------------------------------------------------------
# Integration – requires a running Supabase instance
# Run with: pytest -m integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_save_and_find_by_id() -> None:
    """Calls the real database. Expects save to persist a Narrative retrievable by ID.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseNarrativeRepository(client=client)
    narrative = NarrativeMother.with_two_scenes()

    saved = await repo.save(narrative)
    try:
        found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

        assert found.title == "Klartext"
        assert len(found.scenes) == 2
    finally:
        await client.table("narrative_units").delete().eq("narrative_id", saved.id).execute()
        await client.table("narrative").delete().eq("id", saved.id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_list_all_includes_saved_narrative() -> None:
    """Calls the real database. Expects list_all to include the newly saved Narrative.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseNarrativeRepository(client=client)
    saved = await repo.save(NarrativeMother.with_title("List-All Test Narrativ"))

    try:
        all_narratives = await repo.list_all()

        ids = [n.id for n in all_narratives]
        assert saved.id in ids
    finally:
        await client.table("narrative").delete().eq("id", saved.id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_add_and_get_actor() -> None:
    """Calls the real database. Expects add_actor to persist an Actor retrievable by get_actor.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.models.narrative import Actor
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseNarrativeRepository(client=client)
    saved_narrative = await repo.save(NarrativeMother.empty())

    try:
        saved_actor = await repo.add_actor(
            saved_narrative.id,  # type: ignore[arg-type]
            Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL, notes="The protagonist."),
        )
        found = await repo.get_actor(saved_narrative.id, saved_actor.id)  # type: ignore[arg-type]

        assert found.id == saved_actor.id
        assert found.label == "Max"
        assert found.actor_type == ActorType.INDIVIDUAL
        assert found.notes == "The protagonist."
    finally:
        await (
            client.table("narrative_actors")
            .delete()
            .eq("narrative_id", saved_narrative.id)
            .execute()
        )
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_update_actor() -> None:
    """Calls the real database. Expects update_actor to persist the changed fields.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.models.narrative import Actor
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseNarrativeRepository(client=client)
    saved_narrative = await repo.save(NarrativeMother.empty())

    try:
        saved_actor = await repo.add_actor(
            saved_narrative.id,  # type: ignore[arg-type]
            Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL),
        )
        saved_actor.update(label="CDU", actor_type=ActorType.ORGANISATION, notes="A party.")
        updated = await repo.update_actor(saved_narrative.id, saved_actor)  # type: ignore[arg-type]

        assert updated.label == "CDU"
        assert updated.actor_type == ActorType.ORGANISATION
        assert updated.notes == "A party."
    finally:
        await (
            client.table("narrative_actors")
            .delete()
            .eq("narrative_id", saved_narrative.id)
            .execute()
        )
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_remove_actor() -> None:
    """Calls the real database. Expects remove_actor to delete the actor row.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.exceptions.narrative import ActorNotFoundError
    from api.models.narrative import Actor
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseNarrativeRepository(client=client)
    saved_narrative = await repo.save(NarrativeMother.empty())

    try:
        saved_actor = await repo.add_actor(
            saved_narrative.id,  # type: ignore[arg-type]
            Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL),
        )
        await repo.remove_actor(saved_narrative.id, saved_actor.id)  # type: ignore[arg-type]

        with pytest.raises(ActorNotFoundError):
            await repo.get_actor(saved_narrative.id, saved_actor.id)  # type: ignore[arg-type]
    finally:
        await (
            client.table("narrative_actors")
            .delete()
            .eq("narrative_id", saved_narrative.id)
            .execute()
        )
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_link_to_causal_model() -> None:
    """Calls the real database. Expects link_to_causal_model to persist the causal_model_id.

    Creates a real CausalModel first to satisfy the foreign key constraint.
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_causal_model_repository import SupabaseCausalModelRepository
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
    from tests.mothers.causal_model_mother import CausalModelMother

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    narrative_repo = SupabaseNarrativeRepository(client=client)
    causal_model_repo = SupabaseCausalModelRepository(client=client)

    saved_narrative = await narrative_repo.save(NarrativeMother.empty())
    saved_model = await causal_model_repo.save(CausalModelMother.empty())
    assert saved_narrative.id is not None
    assert saved_model.id is not None

    try:
        updated = await narrative_repo.link_to_causal_model(
            saved_narrative.id,
            saved_model.id,
        )

        assert updated.causal_model_id == saved_model.id
    finally:
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()
        await client.table("causal_models").delete().eq("id", saved_model.id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_narrative_repository_list_summaries_for_user() -> None:
    """Calls the real database. Expects list_summaries_for_user to resolve all embedded counts.

    This test uses the PostgREST embedded-count query (scenes, actors, claims) that
    requires FK relationships to be present in the schema cache. If any migration that
    adds or renames those FK columns was not applied correctly, this test fails with
    a PGRST200 error before reaching the assertions.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
    from api.repositories.supabase_user_repository import SupabaseUserRepository
    from tests.fakes.fake_user_repository import DEFAULT_USER_ID

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    narrative_repo = SupabaseNarrativeRepository(client=client)
    user_repo = SupabaseUserRepository(client=client)

    user = await user_repo.find_default()
    narrative = NarrativeMother.empty()
    narrative.assign_user(user.id)  # type: ignore[arg-type]
    saved = await narrative_repo.save(narrative)

    try:
        summaries = await narrative_repo.list_summaries_for_user(DEFAULT_USER_ID)

        ids = [s.id for s in summaries]
        assert saved.id in ids

        summary = next(s for s in summaries if s.id == saved.id)
        assert summary.title == saved.title
        assert summary.scene_count == 0
        assert summary.actor_count == 0
        assert summary.claim_count == 0
    finally:
        await client.table("narrative").delete().eq("id", saved.id).execute()
