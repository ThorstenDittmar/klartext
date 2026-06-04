"""Tests for WirkgefuegeSuggestionService.

Uses FakeNarrativeRepository, FakeClaimRepository, and FakeWirkgefuegeSuggestionProvider
— no DB or API calls.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative import NarrativeNotFoundError
from api.models.claim import ClaimStatus
from api.providers.wirkgefuege_suggestion_provider import WirkgefuegeSuggestionResult
from api.services.wirkgefuege_suggestion_service import WirkgefuegeSuggestionService
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from tests.fakes.fake_wirkgefuege_suggestion_provider import FakeWirkgefuegeSuggestionProvider
from tests.mothers.claim_mother import ClaimMother
from tests.mothers.narrative_mother import NarrativeMother


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_returns_result() -> None:
    """Expects a WirkgefuegeSuggestionResult for a narrative with DRAFT claims."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]
    await claim_repo.save_all(ClaimMother.collection(), scene_id=scene_id)

    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    result = await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert isinstance(result, WirkgefuegeSuggestionResult)
    assert len(result.suggested_slots) == 2


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_includes_claim_ids_in_result() -> None:
    """Expects from_claims to reference the IDs of the DRAFT claims passed to the provider."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]
    saved_claims = await claim_repo.save_all(ClaimMother.collection(), scene_id=scene_id)

    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    result = await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert set(result.from_claims) == {c.id for c in saved_claims}


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_returns_empty_when_no_draft_claims() -> None:
    """Expects an empty WirkgefuegeSuggestionResult when no DRAFT claims exist."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]

    # Save one claim and mark it LINKED — not DRAFT
    [saved_claim] = await claim_repo.save_all([ClaimMother.causal()], scene_id=scene_id)
    saved_claim.link_to_wirkgefuege("slot-xyz")
    await claim_repo.update(saved_claim)

    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    result = await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert result.suggested_slots == []
    assert result.suggested_relations == []
    assert result.from_claims == []


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_only_passes_draft_claims() -> None:
    """Expects only DRAFT claims to be passed to the provider (not LINKED or UNRESOLVED)."""

    class CapturingProvider(FakeWirkgefuegeSuggestionProvider):
        def __init__(self) -> None:
            self.received_claims: list = []

        async def suggest(self, claims):  # type: ignore[override]
            self.received_claims = list(claims)
            return await super().suggest(claims)

    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]

    [draft_claim, linked_claim, unresolved_claim] = await claim_repo.save_all(
        ClaimMother.collection(), scene_id=scene_id
    )
    linked_claim.link_to_wirkgefuege("slot-abc")
    await claim_repo.update(linked_claim)
    unresolved_claim.mark_unresolved()
    await claim_repo.update(unresolved_claim)

    provider = CapturingProvider()
    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=provider,
    )

    await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert len(provider.received_claims) == 1
    assert provider.received_claims[0].status == ClaimStatus.DRAFT


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    with pytest.raises(NarrativeNotFoundError):
        await service.suggest_for_narrative("00000000-0000-0000-0000-000000000000")
