"""Dependency wiring for FastAPI.

Each get_* function is the single place where a concrete implementation
is chosen. Tests override these via app.dependency_overrides.
"""

from __future__ import annotations

import os

import anthropic

from api.providers.claude_claim_extraction_provider import ClaudeClaimExtractionProvider
from api.services.claim_extractor_service import ClaimExtractorService


def get_claim_extractor_service() -> ClaimExtractorService:
    """Wires ClaudeClaimExtractionProvider into ClaimExtractorService."""
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    provider = ClaudeClaimExtractionProvider(client=client)
    return ClaimExtractorService(provider=provider)
