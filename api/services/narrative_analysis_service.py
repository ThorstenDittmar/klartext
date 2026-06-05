"""Service: analyses a Narrative by calling a NarrativeAnalysisProvider."""

from __future__ import annotations

import logging

from api.models.claim import Claim, ClaimType
from api.providers.narrative_analysis_provider import (
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
)
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository


class NarrativeAnalysisService:
    """Finds the Narrative, delegates analysis to the provider, and persists claims as DRAFT.

    Claims returned by the provider are saved immediately so that
    WirkgefuegeSuggestionService can read them without a subsequent explicit
    save step.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        repository: NarrativeRepository,
        provider: NarrativeAnalysisProvider,
        claim_repository: ClaimRepository,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._claim_repository = claim_repository

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        """Analyses the Narrative and persists all extracted claims as DRAFT.

        Returns the full NarrativeAnalysisResult (actors + claims).
        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        """
        self.logger.debug("NarrativeAnalysisService.analyse: narrative_id=%s", narrative_id)
        narrative = await self._repository.find_by_id(narrative_id)
        result = await self._provider.analyse(narrative)

        if result.claims:
            claims_to_save = [
                Claim.create(
                    label=c.label,
                    text=c.text,
                    typ=ClaimType(c.claim_type),
                    confidence=c.confidence,
                )
                for c in result.claims
            ]
            await self._claim_repository.save_for_narrative(claims_to_save, narrative_id)

        return result
