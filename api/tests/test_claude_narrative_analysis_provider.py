"""Integration test for ClaudeNarrativeAnalysisProvider.

Requires a real Anthropic API key (ANTHROPIC_API_KEY environment variable).
Run with: pytest -m integration
"""

from __future__ import annotations

import pytest

from api.models.narrative import Narrative, Scene
from api.providers.narrative_analysis_provider import NarrativeAnalysisResult


@pytest.mark.integration
@pytest.mark.asyncio
async def test_claude_narrative_analysis_provider_returns_actors_and_claims() -> None:
    """Calls the real Claude API. Expects at least one actor and one claim to be returned."""
    import os

    import anthropic

    from api.providers.claude_narrative_analysis_provider import (
        ClaudeNarrativeAnalysisProvider,
    )

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    provider = ClaudeNarrativeAnalysisProvider(client=client)

    narrative = Narrative(id="test-id", title="Inflation Test")
    scene = Scene(
        id="scene-1",
        title="Scene 1",
        text=(
            "Die Europäische Zentralbank erhöhte die Zinsen auf 4 Prozent. "
            "Ökonomen erwarten dass höhere Zinsen die Inflation dämpfen werden, "
            "weil Kredite teurer werden und die Nachfrage sinkt."
        ),
        position=1,
    )
    narrative.add_scene(scene)

    result = await provider.analyse(narrative)

    assert isinstance(result, NarrativeAnalysisResult)
    assert len(result.actors) >= 1
    assert len(result.claims) >= 1
    assert all(a.label for a in result.actors)
    assert all(c.confidence >= 0.0 for c in result.claims)
    assert all(c.confidence <= 1.0 for c in result.claims)
