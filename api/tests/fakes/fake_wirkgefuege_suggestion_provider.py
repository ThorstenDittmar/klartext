"""Fake WirkgefuegeSuggestionProvider for use in service and router tests."""

from __future__ import annotations

from api.models.claim import Claim
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionProvider,
    WirkgefuegeSuggestionResult,
)


class FakeWirkgefuegeSuggestionProvider(WirkgefuegeSuggestionProvider):
    """Returns a fixed deterministic result without calling any external API.

    Used in service and router tests to avoid Claude API calls.
    """

    async def suggest(self, claims: list[Claim]) -> WirkgefuegeSuggestionResult:
        """Returns two slots and one relation, referencing the provided claim IDs."""
        return WirkgefuegeSuggestionResult(
            suggested_slots=[
                SuggestedSlot(identifier="money_supply", slot_type="physical_quantity"),
                SuggestedSlot(identifier="inflation", slot_type="trend"),
            ],
            suggested_relations=[
                SuggestedRelation(
                    source="money_supply",
                    target="inflation",
                    source_condition="high",
                    target_effect="rising",
                    mechanism="quantity_theory",
                    epistemic_status="incomplete",
                )
            ],
            from_claims=[c.id for c in claims if c.id is not None],
        )
