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
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert isinstance(result, NarrativeAnalysisResult)


@pytest.mark.asyncio
async def test_narrative_analysis_service_result_contains_actors() -> None:
    """Expects at least one actor in the result when the provider returns actors."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert len(result.actors) == 1
    assert result.actors[0].label == "Central Bank"


@pytest.mark.asyncio
async def test_narrative_analysis_service_result_contains_claims() -> None:
    """Expects at least one claim in the result when the provider returns claims."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

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

    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    provider = CapturingProvider()
    service = NarrativeAnalysisService(repository=repo, provider=provider)

    await service.analyse(saved.id)  # type: ignore[arg-type]

    assert provider.received_id == saved.id


@pytest.mark.asyncio
async def test_narrative_analysis_service_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    repo = FakeNarrativeRepository()
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    with pytest.raises(NarrativeNotFoundError):
        await service.analyse("00000000-0000-0000-0000-000000000000")
