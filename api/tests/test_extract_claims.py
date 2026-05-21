"""Tests for POST /extract-claims endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from api.main import app


@pytest.fixture
def sample_text():
    return (
        "Inflation entsteht, wenn zu viel Geld zu wenigen Gütern gegenübersteht. "
        "Die Zentralbank erhöht deshalb die Zinsen, um die Nachfrage zu dämpfen."
    )


@pytest.mark.asyncio
async def test_extract_claims_returns_200(sample_text):
    mock_claims = [
        {
            "text": "Inflation entsteht wenn zu viel Geld zu wenigen Gütern gegenübersteht",
            "typ": "kausaler_claim",
            "konfidenz": 0.9,
        },
        {
            "text": "Zinserhöhungen dämpfen die Nachfrage",
            "typ": "kausaler_claim",
            "konfidenz": 0.85,
        },
    ]

    with patch(
        "api.services.claim_extractor.extract_claims_from_text",
        new_callable=AsyncMock,
        return_value=mock_claims,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/extract-claims",
                json={"text": sample_text},
            )

    assert response.status_code == 200
    data = response.json()
    assert "claims" in data
    assert len(data["claims"]) == 2
    assert data["claims"][0]["typ"] == "kausaler_claim"


@pytest.mark.asyncio
async def test_extract_claims_empty_text_returns_422():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/extract-claims",
            json={"text": ""},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_extract_claims_missing_text_returns_422():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/extract-claims", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_extract_claims_response_shape(sample_text):
    mock_claims = [
        {
            "text": "Zinserhöhungen dämpfen die Nachfrage",
            "typ": "kausaler_claim",
            "konfidenz": 0.85,
        }
    ]

    with patch(
        "api.services.claim_extractor.extract_claims_from_text",
        new_callable=AsyncMock,
        return_value=mock_claims,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/extract-claims",
                json={"text": sample_text},
            )

    data = response.json()
    claim = data["claims"][0]
    assert "text" in claim
    assert "typ" in claim
    assert "konfidenz" in claim
    assert isinstance(claim["konfidenz"], float)
    assert 0.0 <= claim["konfidenz"] <= 1.0
