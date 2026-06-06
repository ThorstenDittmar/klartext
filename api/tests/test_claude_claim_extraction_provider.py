"""Tests for ClaudeClaimExtractionProvider.

Unit tests inject a mock Anthropic client – no real API calls, no token costs.
The single integration test (marked with @pytest.mark.integration) calls the
real Claude API and is excluded from the default test run.
Run it explicitly with: pytest -m integration
"""

import json
from unittest.mock import AsyncMock, MagicMock

import anthropic
import pytest

from api.exceptions.claim import ClaimExtractionError
from api.models.claim import Claim, ClaimType
from api.models.narrative import Scene
from api.providers.claude_claim_extraction_provider import ClaudeClaimExtractionProvider


def make_mock_client(response_text: str) -> AsyncMock:
    """Builds a mock AsyncAnthropic client that returns the given text as Claude's response."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(spec=anthropic.types.TextBlock, text=response_text)]

    mock_client = AsyncMock(spec=anthropic.AsyncAnthropic)
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


@pytest.fixture
def scene() -> Scene:
    return Scene.create(
        title="Szene 1",
        text="Inflation entsteht, wenn zu viel Geld zu wenigen Gütern gegenübersteht.",
        position=1,
    )


# --- Happy path ---


@pytest.mark.asyncio
async def test_claude_provider_returns_claim_objects(scene: Scene) -> None:
    """Expects the provider to parse the API response into proper Claim domain objects."""
    response = json.dumps(
        [
            {
                "text": "Inflation entsteht durch Geldmenge.",
                "typ": "causal",
                "confidence": 0.9,
            }
        ]
    )
    provider = ClaudeClaimExtractionProvider(client=make_mock_client(response))

    claims = await provider.extract(scene)

    assert len(claims) == 1
    assert isinstance(claims[0], Claim)


@pytest.mark.asyncio
async def test_claude_provider_maps_typ_to_claim_type_enum(scene: Scene) -> None:
    """Expects the 'typ' string from the API to be converted to a ClaimType enum value."""
    response = json.dumps(
        [
            {
                "text": "Inflation entsteht durch Geldmenge.",
                "typ": "causal",
                "confidence": 0.9,
            }
        ]
    )
    provider = ClaudeClaimExtractionProvider(client=make_mock_client(response))

    claims = await provider.extract(scene)

    assert claims[0].typ == ClaimType.CAUSAL


@pytest.mark.asyncio
async def test_claude_provider_clamps_confidence_within_valid_range(scene: Scene) -> None:
    """Expects confidence values outside 0.0–1.0 to be clamped, not rejected."""
    response = json.dumps(
        [
            {"text": "Ein Claim.", "typ": "empirical", "confidence": 1.5},
            {"text": "Noch ein Claim.", "typ": "empirical", "confidence": -0.2},
        ]
    )
    provider = ClaudeClaimExtractionProvider(client=make_mock_client(response))

    claims = await provider.extract(scene)

    assert claims[0].confidence == 1.0
    assert claims[1].confidence == 0.0


@pytest.mark.asyncio
async def test_claude_provider_passes_scene_text_to_api(scene: Scene) -> None:
    """Expects the scene text to appear in the prompt sent to the Claude API."""
    response = json.dumps([{"text": "Ein Claim.", "typ": "empirical", "confidence": 0.8}])
    mock_client = make_mock_client(response)
    provider = ClaudeClaimExtractionProvider(client=mock_client)

    await provider.extract(scene)

    call_kwargs = mock_client.messages.create.call_args.kwargs
    user_message = call_kwargs["messages"][0]["content"]
    assert scene.text in user_message


@pytest.mark.asyncio
async def test_claude_provider_strips_markdown_code_fences(scene: Scene) -> None:
    """Expects the provider to handle Claude responses wrapped in markdown code fences."""
    raw = json.dumps([{"text": "Ein Claim.", "typ": "empirical", "confidence": 0.8}])
    response = f"```json\n{raw}\n```"
    provider = ClaudeClaimExtractionProvider(client=make_mock_client(response))

    claims = await provider.extract(scene)

    assert len(claims) == 1


# --- Error cases ---


@pytest.mark.asyncio
async def test_claude_provider_raises_for_malformed_json_response(scene: Scene) -> None:
    """Expects a ClaimExtractionError when the API returns text that cannot be parsed as JSON."""
    provider = ClaudeClaimExtractionProvider(client=make_mock_client("das ist kein json"))

    with pytest.raises(ClaimExtractionError):
        await provider.extract(scene)


@pytest.mark.asyncio
async def test_claude_provider_raises_for_json_object_instead_of_array(scene: Scene) -> None:
    """Expects a ClaimExtractionError when the API returns a JSON object instead of an array."""
    response = json.dumps({"error": "unexpected format"})
    provider = ClaudeClaimExtractionProvider(client=make_mock_client(response))

    with pytest.raises(ClaimExtractionError):
        await provider.extract(scene)


@pytest.mark.asyncio
async def test_claude_provider_raises_for_unknown_claim_type_in_response(scene: Scene) -> None:
    """Expects a ClaimExtractionError when the API returns an unrecognised claim type string."""
    response = json.dumps([{"text": "Ein Claim.", "typ": "unbekannter_claim", "confidence": 0.8}])
    provider = ClaudeClaimExtractionProvider(client=make_mock_client(response))

    with pytest.raises(ClaimExtractionError):
        await provider.extract(scene)


# --- Integration ---


@pytest.mark.integration
@pytest.mark.claude
@pytest.mark.asyncio
async def test_claude_provider_extracts_claims_from_real_scene() -> None:
    """Calls the real Claude API. Expects at least one Claim with valid fields.

    Requires ANTHROPIC_API_KEY to be set. Run with: pytest -m integration
    """
    import os

    real_client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    provider = ClaudeClaimExtractionProvider(client=real_client)
    scene = Scene.create(
        title="Szene 1",
        text="Inflation entsteht, wenn zu viel Geld zu wenigen Gütern gegenübersteht. "
        "Die Zentralbank erhöht deshalb die Zinsen, um die Nachfrage zu dämpfen.",
        position=1,
    )

    claims = await provider.extract(scene)

    assert len(claims) > 0
    assert all(isinstance(c, Claim) for c in claims)
    assert all(0.0 <= c.confidence <= 1.0 for c in claims)
