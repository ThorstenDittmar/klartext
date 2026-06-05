"""Tests for the ClaimRepository contract.

All unit tests run against FakeClaimRepository, which verifies the contract
itself. The SupabaseClaimRepository must satisfy the same contract;
those tests are marked @pytest.mark.integration.
"""

from __future__ import annotations

import pytest

from api.exceptions.claim import ClaimNotFoundError
from api.models.claim import Claim, ClaimType
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.mothers.claim_mother import ClaimMother

SCENE_ID = "scene-aaa-111"
OTHER_SCENE_ID = "scene-bbb-222"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_claim_repository_save_all_assigns_ids_to_claims() -> None:
    """Expects every saved claim to have a non-None ID assigned by the repository."""
    repo = FakeClaimRepository()

    saved = await repo.save_all(ClaimMother.collection(), scene_id=SCENE_ID)

    assert all(c.id is not None for c in saved)


@pytest.mark.asyncio
async def test_claim_repository_save_all_returns_all_claims() -> None:
    """Expects save_all to return exactly as many claims as were passed in."""
    repo = FakeClaimRepository()

    saved = await repo.save_all(ClaimMother.collection(), scene_id=SCENE_ID)

    assert len(saved) == 3


@pytest.mark.asyncio
async def test_claim_repository_save_all_accepts_empty_list() -> None:
    """Expects save_all to succeed with an empty input list and return an empty list."""
    repo = FakeClaimRepository()

    saved = await repo.save_all([], scene_id=SCENE_ID)

    assert saved == []


@pytest.mark.asyncio
async def test_claim_repository_find_by_scene_id_returns_saved_claims() -> None:
    """Expects find_by_scene_id to return the claims that were previously saved."""
    repo = FakeClaimRepository()
    await repo.save_all(ClaimMother.collection(), scene_id=SCENE_ID)

    found = await repo.find_by_scene_id(SCENE_ID)

    assert len(found) == 3
    assert all(isinstance(c, Claim) for c in found)


@pytest.mark.asyncio
async def test_claim_repository_find_by_scene_id_returns_empty_list_for_unknown_scene() -> None:
    """Expects find_by_scene_id to return an empty list when no claims exist for that scene."""
    repo = FakeClaimRepository()

    found = await repo.find_by_scene_id("unknown-scene-id")

    assert found == []


@pytest.mark.asyncio
async def test_claim_repository_find_by_scene_id_isolates_claims_by_scene() -> None:
    """Expects find_by_scene_id to return only the claims for the requested scene."""
    repo = FakeClaimRepository()
    await repo.save_all(ClaimMother.collection(), scene_id=SCENE_ID)
    await repo.save_all([ClaimMother.causal(), ClaimMother.empirical()], scene_id=OTHER_SCENE_ID)

    found = await repo.find_by_scene_id(SCENE_ID)

    assert len(found) == 3


@pytest.mark.asyncio
async def test_claim_repository_find_by_id_returns_saved_claim() -> None:
    """Expects find_by_id to return the Claim that was previously saved."""
    repo = FakeClaimRepository()
    [saved] = await repo.save_all([ClaimMother.causal()], scene_id=SCENE_ID)

    found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.id == saved.id
    assert found.label == saved.label


@pytest.mark.asyncio
async def test_claim_repository_find_by_id_raises_for_unknown_id() -> None:
    """Expects ClaimNotFoundError when no Claim exists for the given ID."""
    repo = FakeClaimRepository()

    with pytest.raises(ClaimNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_claim_repository_update_persists_status_and_wirkgefuege_ref() -> None:
    """Expects update to persist status and wirkgefuege_ref changes."""
    repo = FakeClaimRepository()
    [saved] = await repo.save_all([ClaimMother.causal()], scene_id=SCENE_ID)
    saved.link_to_wirkgefuege("slot-abc")

    updated = await repo.update(saved)

    refetched = await repo.find_by_id(updated.id)  # type: ignore[arg-type]
    assert refetched.status.value == "linked"
    assert refetched.wirkgefuege_ref == "slot-abc"


# ---------------------------------------------------------------------------
# Integration – requires a running Supabase instance
# Run with: pytest -m integration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_for_narrative_returns_claims_with_ids() -> None:
    """Expects save_for_narrative to persist claims and return them with IDs assigned."""
    repo = FakeClaimRepository()
    claims = [Claim.create("Label", "Full text here", ClaimType.CAUSAL, 0.9)]
    saved = await repo.save_for_narrative(claims, narrative_id="narr-001")
    assert len(saved) == 1
    assert saved[0].id is not None


@pytest.mark.asyncio
async def test_find_by_narrative_id_returns_saved_claims() -> None:
    """Expects find_by_narrative_id to return all claims saved for the given narrative."""
    repo = FakeClaimRepository()
    claims = [Claim.create("Label", "Full text here", ClaimType.CAUSAL, 0.9)]
    await repo.save_for_narrative(claims, narrative_id="narr-001")
    found = await repo.find_by_narrative_id("narr-001")
    assert len(found) == 1
    assert found[0].label == "Label"


@pytest.mark.asyncio
async def test_find_by_narrative_id_returns_empty_for_unknown() -> None:
    """Expects find_by_narrative_id to return an empty list for an unknown narrative."""
    repo = FakeClaimRepository()
    result = await repo.find_by_narrative_id("unknown-narrative")
    assert result == []


# ---------------------------------------------------------------------------
# Integration – requires a running Supabase instance
# Run with: pytest -m integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_claim_repository_save_all_and_find_by_scene_id() -> None:
    """Calls the real database. Expects saved Claims to be retrievable by scene ID.

    Saves a Narrative and a Scene first to satisfy the foreign key constraint.
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_claim_repository import SupabaseClaimRepository
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
    from tests.mothers.narrative_mother import NarrativeMother

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    narrative_repo = SupabaseNarrativeRepository(client=client)
    claim_repo = SupabaseClaimRepository(client=client)

    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]

    saved_claims = await claim_repo.save_all(ClaimMother.collection(), scene_id=scene_id)

    try:
        found = await claim_repo.find_by_scene_id(scene_id)

        assert len(found) == 3
        assert all(isinstance(c, Claim) for c in found)
        assert all(0.0 <= c.confidence <= 1.0 for c in found)
    finally:
        await client.table("claims").delete().eq("scene_id", scene_id).execute()
        await (
            client.table("narrative_units")
            .delete()
            .eq("narrative_id", saved_narrative.id)
            .execute()
        )
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()

    _ = saved_claims


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_claim_repository_find_by_id_and_update() -> None:
    """Calls the real database. Expects find_by_id to retrieve a saved Claim by ID.

    Also verifies that update persists status and wirkgefuege_ref changes.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_claim_repository import SupabaseClaimRepository
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
    from tests.mothers.narrative_mother import NarrativeMother

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    narrative_repo = SupabaseNarrativeRepository(client=client)
    claim_repo = SupabaseClaimRepository(client=client)

    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]
    [saved_claim] = await claim_repo.save_all([ClaimMother.causal()], scene_id=scene_id)

    try:
        # find_by_id
        found = await claim_repo.find_by_id(saved_claim.id)  # type: ignore[arg-type]
        assert found.id == saved_claim.id
        assert found.label == saved_claim.label

        # update (link to wirkgefuege)
        found.link_to_wirkgefuege("slot-test-ref")
        updated = await claim_repo.update(found)

        assert updated.status.value == "linked"
        assert updated.wirkgefuege_ref == "slot-test-ref"

        # verify persisted
        refetched = await claim_repo.find_by_id(saved_claim.id)  # type: ignore[arg-type]
        assert refetched.status.value == "linked"
        assert refetched.wirkgefuege_ref == "slot-test-ref"
    finally:
        await client.table("claims").delete().eq("scene_id", scene_id).execute()
        await (
            client.table("narrative_units")
            .delete()
            .eq("narrative_id", saved_narrative.id)
            .execute()
        )
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()
