"""Tests for the WirkmodellRepository contract.

All unit tests run against FakeWirkmodellRepository.
The SupabaseWirkmodellRepository must satisfy the same contract;
those tests are marked @pytest.mark.integration.
"""

from __future__ import annotations

import pytest

from api.exceptions.wirkmodell import WirkmodellNotFoundError
from api.models.wirkmodell import Wirkmodell
from tests.fakes.fake_wirkmodell_repository import FakeWirkmodellRepository
from tests.mothers.wirkmodell_mother import AxiomMother, WirkmodellMother


@pytest.mark.asyncio
async def test_wirkmodell_repository_save_assigns_id() -> None:
    """Expects the saved Wirkmodell to have a non-None ID."""
    repo = FakeWirkmodellRepository()

    saved = await repo.save(WirkmodellMother.empty())

    assert saved.id is not None


@pytest.mark.asyncio
async def test_wirkmodell_repository_save_preserves_titel() -> None:
    """Expects the saved Wirkmodell to retain its titel."""
    repo = FakeWirkmodellRepository()

    saved = await repo.save(WirkmodellMother.empty())

    assert saved.titel == "Klartext Wirkmodell"


@pytest.mark.asyncio
async def test_wirkmodell_repository_save_assigns_ids_to_axiome() -> None:
    """Expects all axiome of the saved Wirkmodell to have IDs."""
    repo = FakeWirkmodellRepository()

    saved = await repo.save(WirkmodellMother.with_axiome())

    assert all(a.id is not None for a in saved.axiome)


@pytest.mark.asyncio
async def test_wirkmodell_repository_add_axiom_assigns_id() -> None:
    """Expects add_axiom to return the Axiom with a non-None ID."""
    repo = FakeWirkmodellRepository()
    saved_wm = await repo.save(WirkmodellMother.empty())

    saved_axiom = await repo.add_axiom(saved_wm.id, AxiomMother.zins())  # type: ignore[arg-type]

    assert saved_axiom.id is not None


@pytest.mark.asyncio
async def test_wirkmodell_repository_add_axiom_makes_it_retrievable() -> None:
    """Expects added Axiom to appear in find_by_id result."""
    repo = FakeWirkmodellRepository()
    saved_wm = await repo.save(WirkmodellMother.empty())
    await repo.add_axiom(saved_wm.id, AxiomMother.zins())  # type: ignore[arg-type]

    found = await repo.find_by_id(saved_wm.id)  # type: ignore[arg-type]

    assert len(found.axiome) == 1
    assert found.axiome[0].label == "A-01"


@pytest.mark.asyncio
async def test_wirkmodell_repository_find_by_id_returns_wirkmodell_with_axiome() -> None:
    """Expects find_by_id to return the Wirkmodell with all its Axiome."""
    repo = FakeWirkmodellRepository()
    saved = await repo.save(WirkmodellMother.with_axiome())

    found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.titel == "Klartext Wirkmodell"
    assert len(found.axiome) == 3


@pytest.mark.asyncio
async def test_wirkmodell_repository_list_all_returns_all() -> None:
    """Expects list_all to include every saved Wirkmodell."""
    repo = FakeWirkmodellRepository()
    for wm in WirkmodellMother.collection():
        await repo.save(wm)

    all_wm = await repo.list_all()

    titles = {wm.titel for wm in all_wm}
    assert titles == {"Erstes Wirkmodell", "Zweites Wirkmodell", "Drittes Wirkmodell"}


@pytest.mark.asyncio
async def test_wirkmodell_repository_find_by_id_raises_for_unknown_id() -> None:
    """Expects WirkmodellNotFoundError when no Wirkmodell exists for the given ID."""
    repo = FakeWirkmodellRepository()

    with pytest.raises(WirkmodellNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000000")


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_wirkmodell_repository_save_and_find_by_id() -> None:
    """Calls the real database. Expects save to persist a Wirkmodell retrievable by ID.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_wirkmodell_repository import SupabaseWirkmodellRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseWirkmodellRepository(client=client)
    wm = WirkmodellMother.with_axiome()

    saved = await repo.save(wm)
    try:
        found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

        assert found.titel == "Klartext Wirkmodell"
        assert len(found.axiome) == 3
    finally:
        await client.table("modellelemente").delete().eq("wirkmodell_id", saved.id).execute()
        await client.table("wirkmodelle").delete().eq("id", saved.id).execute()
