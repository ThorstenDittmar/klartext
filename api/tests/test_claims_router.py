"""Tests for POST /extract-claims router.

The router receives text, builds a Scene, and delegates to ClaimExtractorService.
All tests inject a FakeClaimExtractorService via dependency_overrides so the
Claude API is never called.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_claim_extractor_service
from api.main import app
from api.models.claim import Claim, ClaimType
from api.models.narrative import Scene


class FakeClaimExtractorService:
    """Returns a fixed list of claims regardless of the scene content."""

    async def extract_from_scene(self, scene: Scene) -> list[Claim]:
        return [
            Claim.create(
                label="Inflation durch Geldmenge",
                text="Inflation entsteht durch Geldmenge.",
                typ=ClaimType.CAUSAL,
                confidence=0.9,
            ),
            Claim.create(
                label="Zinserhöhungen dämpfen Nachfrage",
                text="Zinserhöhungen dämpfen die Nachfrage.",
                typ=ClaimType.CAUSAL,
                confidence=0.85,
            ),
        ]


@pytest.fixture(autouse=True)
def override_dependency():
    """Replaces ClaimExtractorService with the fake for every test in this module."""
    app.dependency_overrides[get_claim_extractor_service] = lambda: FakeClaimExtractorService()
    yield
    app.dependency_overrides.clear()


SAMPLE_TEXT = (
    "Inflation entsteht, wenn zu viel Geld zu wenigen Gütern gegenübersteht. "
    "Die Zentralbank erhöht deshalb die Zinsen, um die Nachfrage zu dämpfen."
)


# --- Happy path ---


@pytest.mark.asyncio
async def test_extract_claims_returns_200() -> None:
    """Expects a 200 response for valid text input."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract-claims", json={"text": SAMPLE_TEXT})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_extract_claims_response_contains_claims_list() -> None:
    """Expects the response body to contain a 'claims' list with the extracted claims."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract-claims", json={"text": SAMPLE_TEXT})

    data = response.json()
    assert "claims" in data
    assert len(data["claims"]) == 2


@pytest.mark.asyncio
async def test_extract_claims_response_shape() -> None:
    """Expects each claim in the response to have text, typ, and confidence fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract-claims", json={"text": SAMPLE_TEXT})

    claim = response.json()["claims"][0]
    assert "text" in claim
    assert "typ" in claim
    assert "confidence" in claim
    assert isinstance(claim["confidence"], float)
    assert 0.0 <= claim["confidence"] <= 1.0


# --- Validation errors ---


@pytest.mark.asyncio
async def test_extract_claims_returns_422_for_empty_text() -> None:
    """Expects a 422 because empty text cannot contain any claims."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract-claims", json={"text": ""})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_extract_claims_returns_422_for_whitespace_only_text() -> None:
    """Expects a 422 because whitespace-only text is equivalent to empty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract-claims", json={"text": "   "})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_extract_claims_returns_422_for_missing_text_field() -> None:
    """Expects a 422 because the text field is required."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract-claims", json={})

    assert response.status_code == 422
