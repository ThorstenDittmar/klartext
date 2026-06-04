"""Tests for ClaimService."""

from __future__ import annotations

import pytest

from api.exceptions.claim import ClaimNotFoundError
from api.models.claim import ClaimStatus
from api.services.claim_service import ClaimService
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.mothers.claim_mother import ClaimMother

SCENE_ID = "scene-001"


def make_service() -> ClaimService:
    """Builds a ClaimService with an in-memory repository."""
    return ClaimService(repository=FakeClaimRepository())


@pytest.mark.asyncio
async def test_link_to_wirkgefuege_sets_status_to_linked() -> None:
    """Expects link_to_wirkgefuege to set the claim status to LINKED."""
    repo = FakeClaimRepository()
    [saved] = await repo.save_all([ClaimMother.causal()], scene_id=SCENE_ID)
    service = ClaimService(repository=repo)

    updated = await service.link_to_wirkgefuege(
        claim_id=saved.id,  # type: ignore[arg-type]
        wirkgefuege_ref="slot-abc",
    )

    assert updated.status == ClaimStatus.LINKED
    assert updated.wirkgefuege_ref == "slot-abc"


@pytest.mark.asyncio
async def test_link_to_wirkgefuege_raises_for_unknown_claim() -> None:
    """Expects ClaimNotFoundError when no Claim exists for the given ID."""
    service = make_service()

    with pytest.raises(ClaimNotFoundError):
        await service.link_to_wirkgefuege(
            claim_id="00000000-0000-0000-0000-000000000000",
            wirkgefuege_ref="slot-abc",
        )
