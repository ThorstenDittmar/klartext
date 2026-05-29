"""Service: extracts Claims from a Scene via a ClaimExtractionProvider."""

from __future__ import annotations

from api.exceptions.claim import ClaimExtractionError
from api.models.claim import Claim
from api.models.narrative import Scene
from api.providers.claim_extraction_provider import ClaimExtractionProvider


class ClaimExtractorService:
    """Orchestrates claim extraction for a single Scene.

    The service delegates all extraction logic to the injected provider
    and enforces that a scene must yield at least one claim.
    """

    def __init__(self, provider: ClaimExtractionProvider) -> None:
        self._provider = provider

    async def extract_from_scene(self, scene: Scene) -> list[Claim]:
        """Extracts claims from the given scene.

        Raises ClaimExtractionError if no claims are found.
        """
        claims = await self._provider.extract(scene)

        if not claims:
            raise ClaimExtractionError(f"No claims found in scene: {scene.title}")

        return claims
