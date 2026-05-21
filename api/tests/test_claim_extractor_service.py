"""Tests for ClaimExtractorService.

The service takes a Scene and returns a list of Claims. It delegates the
actual extraction to a ClaimExtractionProvider – in these tests a fake that
returns deterministic results without calling the Claude API.
"""

import pytest

from api.exceptions.claim import ClaimExtractionError
from api.models.claim import Claim, ClaimType
from api.models.narrative import Scene
from api.providers.claim_extraction_provider import ClaimExtractionProvider
from api.services.claim_extractor_service import ClaimExtractorService


class FakeClaimExtractionProvider(ClaimExtractionProvider):
    """Returns a fixed list of claims regardless of input."""

    async def extract(self, scene: Scene) -> list[Claim]:
        return [
            Claim.create(text="Inflation entsteht durch Geldmenge.", typ=ClaimType.CAUSAL, confidence=0.9),
            Claim.create(text="Zinserhöhungen dämpfen die Nachfrage.", typ=ClaimType.CAUSAL, confidence=0.85),
        ]


class FakeClaimExtractionProviderReturnsNothing(ClaimExtractionProvider):
    """Simulates a provider that finds no claims in a scene."""

    async def extract(self, scene: Scene) -> list[Claim]:
        return []


@pytest.fixture
def scene() -> Scene:
    return Scene.create(
        title="Szene 1",
        text="Inflation entsteht, wenn zu viel Geld zu wenigen Gütern gegenübersteht.",
        position=1,
    )


# --- Happy path ---


@pytest.mark.asyncio
async def test_claim_extractor_service_returns_claims_for_scene(scene: Scene) -> None:
    """Expects the service to return the claims produced by the provider."""
    service = ClaimExtractorService(provider=FakeClaimExtractionProvider())

    claims = await service.extract_from_scene(scene)

    assert len(claims) == 2


@pytest.mark.asyncio
async def test_claim_extractor_service_returns_claim_objects(scene: Scene) -> None:
    """Expects the returned items to be proper Claim domain objects."""
    service = ClaimExtractorService(provider=FakeClaimExtractionProvider())

    claims = await service.extract_from_scene(scene)

    assert all(isinstance(claim, Claim) for claim in claims)


@pytest.mark.asyncio
async def test_claim_extractor_service_passes_scene_to_provider(scene: Scene) -> None:
    """Expects the provider to receive exactly the scene that was passed to the service."""

    class CapturingProvider(ClaimExtractionProvider):
        def __init__(self) -> None:
            self.received_scene: Scene | None = None

        async def extract(self, scene: Scene) -> list[Claim]:
            self.received_scene = scene
            return [Claim.create(text="Dummy claim.", typ=ClaimType.EMPIRICAL, confidence=0.5)]

    provider = CapturingProvider()
    service = ClaimExtractorService(provider=provider)

    await service.extract_from_scene(scene)

    assert provider.received_scene is scene


# --- Error cases ---


@pytest.mark.asyncio
async def test_claim_extractor_service_raises_for_scene_with_no_claims(scene: Scene) -> None:
    """Expects a ClaimExtractionError when the provider finds no claims in the scene."""
    service = ClaimExtractorService(provider=FakeClaimExtractionProviderReturnsNothing())

    with pytest.raises(ClaimExtractionError):
        await service.extract_from_scene(scene)
