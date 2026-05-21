"""Tests for the ClaimRepository contract.

The FakeClaimRepository below implements the full port in memory.
All tests run against the Fake, which verifies the contract itself.

The SupabaseClaimRepository must satisfy the same contract;
those tests are marked @pytest.mark.integration and hit the real database.
"""

from __future__ import annotations

import uuid

import pytest

from api.models.claim import Claim, ClaimType
from api.repositories.claim_repository import ClaimRepository


# ---------------------------------------------------------------------------
# Fake implementation
# ---------------------------------------------------------------------------


class FakeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository for unit tests.

    Stores claims keyed by scene_id. Assigns UUID strings as IDs.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[Claim]] = {}

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Assigns a new UUID to each claim, then stores them under the given scene_id."""
        saved = [
            Claim(
                id=str(uuid.uuid4()),
                text=c.text,
                typ=c.typ,
                confidence=c.confidence,
            )
            for c in claims
        ]
        self._store[scene_id] = saved
        return saved

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns the claims for the given scene, or an empty list if none exist."""
        return self._store.get(scene_id, [])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_claims(count: int = 2) -> list[Claim]:
    return [
        Claim.create(
            text=f"Claim Nummer {i + 1}.",
            typ=ClaimType.EMPIRICAL,
            confidence=0.8,
        )
        for i in range(count)
    ]


SCENE_ID = "scene-aaa-111"
OTHER_SCENE_ID = "scene-bbb-222"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_claim_repository_save_all_assigns_ids_to_claims() -> None:
    """Expects every saved claim to have a non-None ID assigned by the repository."""
    repo = FakeClaimRepository()

    saved = await repo.save_all(make_claims(), scene_id=SCENE_ID)

    assert all(c.id is not None for c in saved)


@pytest.mark.asyncio
async def test_claim_repository_save_all_returns_all_claims() -> None:
    """Expects save_all to return exactly as many claims as were passed in."""
    repo = FakeClaimRepository()

    saved = await repo.save_all(make_claims(3), scene_id=SCENE_ID)

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
    await repo.save_all(make_claims(2), scene_id=SCENE_ID)

    found = await repo.find_by_scene_id(SCENE_ID)

    assert len(found) == 2
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
    await repo.save_all(make_claims(2), scene_id=SCENE_ID)
    await repo.save_all(make_claims(3), scene_id=OTHER_SCENE_ID)

    found = await repo.find_by_scene_id(SCENE_ID)

    assert len(found) == 2


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
    Cleans up all inserted rows after the assertion.
    """
    import os

    from supabase import acreate_client

    from api.models.narrative import Narrative, Scene
    from api.repositories.supabase_claim_repository import SupabaseClaimRepository
    from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    narrative_repo = SupabaseNarrativeRepository(client=client)
    claim_repo = SupabaseClaimRepository(client=client)

    narrative = Narrative.create(title="Claim-Integration-Test")
    narrative.add_scene(Scene.create(title="Szene 1", text="Test.", position=1))
    saved_narrative = await narrative_repo.save(narrative)
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]

    claims_to_save = make_claims(2)
    saved_claims = await claim_repo.save_all(claims_to_save, scene_id=scene_id)

    try:
        found = await claim_repo.find_by_scene_id(scene_id)

        assert len(found) == 2
        assert all(isinstance(c, Claim) for c in found)
        assert all(0.0 <= c.confidence <= 1.0 for c in found)
    finally:
        await client.table("claims").delete().eq("scene_id", scene_id).execute()
        await client.table("narrative_einheiten").delete().eq(
            "narrativ_id", saved_narrative.id
        ).execute()
        await client.table("narrative").delete().eq("id", saved_narrative.id).execute()

    _ = saved_claims  # used implicitly via find_by_scene_id
