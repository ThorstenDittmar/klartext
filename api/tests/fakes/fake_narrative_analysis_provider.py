"""Fake NarrativeAnalysisProvider for use in service and router tests."""

from __future__ import annotations

from api.models.narrative import Narrative
from api.providers.narrative_analysis_provider import (
    ActorOccurrence,
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
    WirkgefuegeSuggestion,
)


class FakeNarrativeAnalysisProvider(NarrativeAnalysisProvider):
    """Returns a fixed deterministic result without calling any external API.

    Used in service tests to avoid Claude API calls.
    """

    async def analyse(self, narrative: Narrative) -> NarrativeAnalysisResult:
        """Returns one actor and one causal claim regardless of input."""
        return NarrativeAnalysisResult(
            actors=[
                ActorSuggestion(
                    label="Central Bank",
                    actor_type="institution",
                    occurrences=[
                        ActorOccurrence(
                            scene_title="Scene 1",
                            start_offset=0,
                            end_offset=12,
                        )
                    ],
                    entity_suggestion="central_bank",
                )
            ],
            claims=[
                ClaimSuggestion(
                    label="Money supply causes inflation",
                    text="An increase in money supply leads to higher inflation.",
                    claim_type="causal",
                    confidence=0.87,
                    wirkgefuege_suggestion=WirkgefuegeSuggestion(
                        suggestion_type="causal_relation",
                        source_slot="money_supply",
                        source_condition="high",
                        target_slot="inflation",
                        target_effect="rising",
                        mechanism="quantity_theory",
                    ),
                    scene_title="Scene 1",
                    start_offset=0,
                    end_offset=52,
                )
            ],
        )
