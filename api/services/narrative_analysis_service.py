"""Service: analyses a Narrative by calling a NarrativeAnalysisProvider."""

from __future__ import annotations

from api.providers.narrative_analysis_provider import (
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
)
from api.repositories.narrative_repository import NarrativeRepository


class NarrativeAnalysisService:
    """Finds the Narrative and delegates analysis to the injected provider.

    Does not persist any results — the caller decides what to do with the suggestions.
    """

    def __init__(
        self,
        repository: NarrativeRepository,
        provider: NarrativeAnalysisProvider,
    ) -> None:
        self._repository = repository
        self._provider = provider

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        """Analyses the Narrative with the given ID.

        Returns suggested actors and claims. Does not persist anything.
        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        """
        narrative = await self._repository.find_by_id(narrative_id)
        return await self._provider.analyse(narrative)
