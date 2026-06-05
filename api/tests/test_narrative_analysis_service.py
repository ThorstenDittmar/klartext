"""Tests for NarrativeAnalysisService.

Uses FakeNarrativeRepository and FakeNarrativeAnalysisProvider — no DB or API calls.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative import NarrativeNotFoundError
from api.providers.narrative_analysis_provider import (
    NarrativeAnalysisResult,
)
from api.services.narrative_analysis_service import NarrativeAnalysisService
from tests.fakes.fake_narrative_analysis_provider import FakeNarrativeAnalysisProvider
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from tests.mothers.narrative_mother import NarrativeMother


@pytest.mark.asyncio
async def test_narrative_analysis_service_returns_analysis_result() -> None:
    """Expects the service to return a NarrativeAnalysisResult for a known narrative."""
    from tests.fakes.fake_claim_repository import FakeClaimRepository

    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(
        repository=repo,
        provider=FakeNarrativeAnalysisProvider(),
        claim_repository=FakeClaimRepository(),
    )

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert isinstance(result, NarrativeAnalysisResult)


@pytest.mark.asyncio
async def test_narrative_analysis_service_result_contains_actors() -> None:
    """Expects at least one actor in the result when the provider returns actors."""
    from tests.fakes.fake_claim_repository import FakeClaimRepository

    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(
        repository=repo,
        provider=FakeNarrativeAnalysisProvider(),
        claim_repository=FakeClaimRepository(),
    )

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert len(result.actors) == 1
    assert result.actors[0].label == "Central Bank"


@pytest.mark.asyncio
async def test_narrative_analysis_service_result_contains_claims() -> None:
    """Expects at least one claim in the result when the provider returns claims."""
    from tests.fakes.fake_claim_repository import FakeClaimRepository

    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(
        repository=repo,
        provider=FakeNarrativeAnalysisProvider(),
        claim_repository=FakeClaimRepository(),
    )

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert len(result.claims) == 1
    assert result.claims[0].claim_type == "causal"


@pytest.mark.asyncio
async def test_narrative_analysis_service_passes_narrative_to_provider() -> None:
    """Expects the service to pass the correct Narrative to the provider."""

    class CapturingProvider(FakeNarrativeAnalysisProvider):
        def __init__(self) -> None:
            self.received_id: str | None = None

        async def analyse(self, narrative):  # type: ignore[override]
            self.received_id = narrative.id
            return await super().analyse(narrative)

    from tests.fakes.fake_claim_repository import FakeClaimRepository

    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    provider = CapturingProvider()
    service = NarrativeAnalysisService(
        repository=repo,
        provider=provider,
        claim_repository=FakeClaimRepository(),
    )

    await service.analyse(saved.id)  # type: ignore[arg-type]

    assert provider.received_id == saved.id


@pytest.mark.asyncio
async def test_narrative_analysis_service_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    from tests.fakes.fake_claim_repository import FakeClaimRepository

    repo = FakeNarrativeRepository()
    service = NarrativeAnalysisService(
        repository=repo,
        provider=FakeNarrativeAnalysisProvider(),
        claim_repository=FakeClaimRepository(),
    )

    with pytest.raises(NarrativeNotFoundError):
        await service.analyse("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_narrative_analysis_service_saves_claims_to_repository() -> None:
    """Expects analyse() to persist the extracted claims as DRAFT in the ClaimRepository."""
    from tests.fakes.fake_claim_repository import FakeClaimRepository

    repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(
        repository=repo,
        provider=FakeNarrativeAnalysisProvider(),
        claim_repository=claim_repo,
    )

    await service.analyse(saved.id)  # type: ignore[arg-type]

    claims = await claim_repo.find_by_narrative_id(saved.id)  # type: ignore[arg-type]
    assert len(claims) == 1
    assert claims[0].label == "Money supply causes inflation"
    assert claims[0].status.value == "draft"
