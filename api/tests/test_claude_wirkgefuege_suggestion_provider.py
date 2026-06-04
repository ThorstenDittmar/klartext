"""Integration test for ClaudeWirkgefuegeSuggestionProvider.

Requires a real Anthropic API key (ANTHROPIC_API_KEY environment variable).
Run with: pytest -m integration
"""

from __future__ import annotations

import pytest

from api.providers.wirkgefuege_suggestion_provider import WirkgefuegeSuggestionResult


@pytest.mark.integration
@pytest.mark.asyncio
async def test_claude_wirkgefuege_suggestion_provider_returns_slots_and_relations() -> None:
    """Calls the real Claude API. Expects at least one slot and one relation."""
    import os

    import anthropic

    from api.models.claim import Claim, ClaimType
    from api.providers.claude_wirkgefuege_suggestion_provider import (
        ClaudeWirkgefuegeSuggestionProvider,
    )

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    provider = ClaudeWirkgefuegeSuggestionProvider(client=client)

    claims = [
        Claim(
            id="claim-1",
            label="Interest rate hikes dampen demand",
            text=(
                "Higher interest rates reduce consumer demand because loans become more expensive."
            ),
            typ=ClaimType.CAUSAL,
            confidence=0.85,
        ),
        Claim(
            id="claim-2",
            label="Reduced demand lowers inflation",
            text="Lower consumer demand reduces price pressure and thereby lowers inflation.",
            typ=ClaimType.CAUSAL,
            confidence=0.80,
        ),
    ]

    result = await provider.suggest(claims)

    assert isinstance(result, WirkgefuegeSuggestionResult)
    assert len(result.suggested_slots) >= 2
    assert len(result.suggested_relations) >= 1
    assert all(s.identifier for s in result.suggested_slots)
    assert all(r.source and r.target for r in result.suggested_relations)
    # All source/target identifiers must reference a suggested slot
    slot_identifiers = {s.identifier for s in result.suggested_slots}
    for rel in result.suggested_relations:
        assert rel.source in slot_identifiers
        assert rel.target in slot_identifiers
