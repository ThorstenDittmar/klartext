"""Tests for the scene claims sub-resource endpoints.

POST /narratives/{narrative_id}/scenes/{scene_id}/extract-claims
GET  /narratives/{narrative_id}/scenes/{scene_id}/claims

Both the NarrativeService and the ClaimExtractorService + ClaimRepository
are replaced with fakes via app.dependency_overrides.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import (
    get_claim_extractor_service,
    get_claim_repository,
    get_narrative_service,
)
from api.exceptions.claim import ClaimNotFoundError
from api.exceptions.narrative import NarrativeNotFoundError
from api.main import app
from api.models.claim import Claim, ClaimType
from api.models.narrative import Narrative, Scene
from api.repositories.claim_repository import ClaimRepository

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NARRATIVE_ID = "aaaa-1111"
SCENE_ID = "bbbb-2222"
UNKNOWN_ID = "0000-0000"


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


def make_narrative_with_scene() -> Narrative:
    narrative = Narrative(id=NARRATIVE_ID, title="Klartext")
    narrative.add_scene(Scene(id=SCENE_ID, title="Szene 1", text="Inflation entsteht.", position=1))
    return narrative


class FakeNarrativeService:
    """Returns a preset Narrative; raises NarrativeNotFoundError for the unknown ID."""

    async def import_from_file(self, path: object) -> Narrative:
        return make_narrative_with_scene()

    async def find_by_id(self, narrative_id: str) -> Narrative:
        if narrative_id == UNKNOWN_ID:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        return make_narrative_with_scene()

    async def list_all(self) -> list[Narrative]:
        return [make_narrative_with_scene()]


class FakeClaimExtractorService:
    """Returns one preset Claim without calling the Claude API."""

    def __init__(self, claims: list[Claim] | None = None) -> None:
        self._claims = claims or [
            Claim.create(
                label="Money supply causes inflation",
                text="Inflation entsteht durch Geldmenge.",
                typ=ClaimType.CAUSAL,
                confidence=0.9,
            )
        ]
        self.received_scene: Scene | None = None

    async def extract_from_scene(self, scene: Scene) -> list[Claim]:
        self.received_scene = scene
        return self._claims


class FakeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository that records saved claims."""

    def __init__(self, existing: list[Claim] | None = None) -> None:
        self._store: dict[str, list[Claim]] = {}
        if existing:
            self._store[SCENE_ID] = existing

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        import uuid

        saved = [
            Claim(
                id=str(uuid.uuid4()), label=c.label, text=c.text, typ=c.typ, confidence=c.confidence
            )
            for c in claims
        ]
        self._store[scene_id] = saved
        return saved

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        return self._store.get(scene_id, [])

    async def find_by_id(self, claim_id: str) -> Claim:
        """Finds a claim by ID across all scenes."""
        for claims in self._store.values():
            for claim in claims:
                if claim.id == claim_id:
                    return claim
        raise ClaimNotFoundError(f"Claim not found: {claim_id}")

    async def update(self, claim: Claim) -> Claim:
        """Replaces the stored claim entry with the updated one."""
        for scene_id, claims in self._store.items():
            for i, c in enumerate(claims):
                if c.id == claim.id:
                    self._store[scene_id][i] = claim
                    return claim
        return claim


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def setup_overrides(
    narrative_service: object | None = None,
    extractor_service: object | None = None,
    claim_repository: object | None = None,
) -> None:
    app.dependency_overrides[get_narrative_service] = lambda: (
        narrative_service or FakeNarrativeService()
    )
    app.dependency_overrides[get_claim_extractor_service] = lambda: (
        extractor_service or FakeClaimExtractorService()
    )
    app.dependency_overrides[get_claim_repository] = lambda: (
        claim_repository or FakeClaimRepository()
    )


def clear_overrides() -> None:
    app.dependency_overrides.clear()


EXTRACT_URL = f"/narratives/{NARRATIVE_ID}/scenes/{SCENE_ID}/extract-claims"
CLAIMS_URL = f"/narratives/{NARRATIVE_ID}/scenes/{SCENE_ID}/claims"


# ---------------------------------------------------------------------------
# POST extract-claims – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_scene_claims_returns_201() -> None:
    """Expects 201 when the narrative and scene exist and extraction succeeds."""
    setup_overrides()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(EXTRACT_URL)
    finally:
        clear_overrides()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_extract_scene_claims_returns_claims_list() -> None:
    """Expects the response to contain a non-empty list of claims."""
    setup_overrides()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(EXTRACT_URL)
    finally:
        clear_overrides()

    data = response.json()
    assert "claims" in data
    assert len(data["claims"]) == 1


@pytest.mark.asyncio
async def test_extract_scene_claims_response_shape() -> None:
    """Expects each claim in the response to have text, typ and confidence."""
    setup_overrides()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(EXTRACT_URL)
    finally:
        clear_overrides()

    claim = response.json()["claims"][0]
    assert "text" in claim
    assert "typ" in claim
    assert "confidence" in claim
    assert isinstance(claim["confidence"], float)


# ---------------------------------------------------------------------------
# POST extract-claims – error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_scene_claims_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the narrative does not exist."""
    setup_overrides()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{UNKNOWN_ID}/scenes/{SCENE_ID}/extract-claims"
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_extract_scene_claims_returns_404_for_unknown_scene() -> None:
    """Expects 404 when the narrative exists but the scene ID is not among its scenes."""
    setup_overrides()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/narratives/{NARRATIVE_ID}/scenes/{UNKNOWN_ID}/extract-claims"
            )
    finally:
        clear_overrides()

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET claims – happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_scene_claims_returns_200() -> None:
    """Expects 200 and a list of claims for a known scene."""
    existing = [
        Claim(
            id="cccc-3333",
            label="Money supply causes inflation",
            text="Inflation entsteht durch Geldmenge.",
            typ=ClaimType.CAUSAL,
            confidence=0.9,
        )
    ]
    setup_overrides(claim_repository=FakeClaimRepository(existing=existing))
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(CLAIMS_URL)
    finally:
        clear_overrides()

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_scene_claims_returns_empty_list_when_no_claims_exist() -> None:
    """Expects 200 with an empty list when no claims have been extracted yet."""
    setup_overrides(claim_repository=FakeClaimRepository())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(CLAIMS_URL)
    finally:
        clear_overrides()

    assert response.status_code == 200
    assert response.json() == []
