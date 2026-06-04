"""Service: suggests a minimal Wirkgefüge from DRAFT Claims of a Narrative."""

from __future__ import annotations

from api.models.claim import Claim, ClaimStatus
from api.providers.wirkgefuege_suggestion_provider import (
    WirkgefuegeSuggestionProvider,
    WirkgefuegeSuggestionResult,
)
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository


class WirkgefuegeSuggestionService:
    """Aggregates DRAFT Claims for a Narrative and delegates suggestion to the injected provider.

    Does not persist any results — the caller decides what to do with the suggestions.
    Returns an empty WirkgefuegeSuggestionResult when no DRAFT Claims exist.
    """

    def __init__(
        self,
        narrative_repository: NarrativeRepository,
        claim_repository: ClaimRepository,
        provider: WirkgefuegeSuggestionProvider,
    ) -> None:
        self._narrative_repository = narrative_repository
        self._claim_repository = claim_repository
        self._provider = provider

    async def suggest_for_narrative(self, narrative_id: str) -> WirkgefuegeSuggestionResult:
        """Suggests a minimal Wirkgefüge from all DRAFT Claims of the Narrative.

        Loads the Narrative to get scene IDs, then fetches DRAFT Claims for each scene.
        Returns an empty result when no DRAFT Claims exist (no API call made).
        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        """
        narrative = await self._narrative_repository.find_by_id(narrative_id)

        draft_claims: list[Claim] = []
        for scene in narrative.scenes:
            claims = await self._claim_repository.find_by_scene_id(scene.id)  # type: ignore[arg-type]
            draft_claims.extend(c for c in claims if c.status == ClaimStatus.DRAFT)

        if not draft_claims:
            return WirkgefuegeSuggestionResult()

        return await self._provider.suggest(draft_claims)
