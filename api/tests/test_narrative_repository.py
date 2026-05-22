"""Tests for the NarrativeRepository contract.

All unit tests run against FakeNarrativeRepository, which verifies the
contract itself. The SupabaseNarrativeRepository must satisfy the same
contract; those tests are marked @pytest.mark.integration.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative import NarrativeNotFoundError
from api.models.narrative import Narrative
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
        await client.table("narrative_einheiten").delete().eq("narrativ_id", saved.id).execute()
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
