"""Dependency wiring for FastAPI.

Each get_* function is the single place where a concrete implementation
is chosen. Tests override these via app.dependency_overrides.

DI chain:
  get_supabase_client ─┬─► get_narrative_repository ─► get_narrative_service
                       └─► get_claim_repository
                       └─► get_health_checker
  get_narrative_import_service ────────────────────────► get_narrative_service
  (standalone) ────────────────────────────────────────► get_claim_extractor_service
"""

from __future__ import annotations

import os

import anthropic
from fastapi import Depends
from supabase import AsyncClient, acreate_client

from api.parsers.markdown_narrative_parser import MarkdownNarrativeParser
from api.providers.claude_claim_extraction_provider import ClaudeClaimExtractionProvider
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository
from api.repositories.supabase_claim_repository import SupabaseClaimRepository
from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
from api.services.claim_extractor_service import ClaimExtractorService
from api.services.health_service import HealthChecker, SupabaseHealthChecker
from api.services.narrative_import_service import NarrativeImportService
from api.services.narrative_service import NarrativeService


async def get_supabase_client() -> AsyncClient:
    """Creates an authenticated Supabase async client from environment variables.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    return await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )


async def get_narrative_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> NarrativeRepository:
    """Wires SupabaseNarrativeRepository with the injected Supabase client."""
    return SupabaseNarrativeRepository(client=client)


async def get_claim_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> ClaimRepository:
    """Wires SupabaseClaimRepository with the injected Supabase client."""
    return SupabaseClaimRepository(client=client)


def get_narrative_import_service() -> NarrativeImportService:
    """Wires MarkdownNarrativeParser into NarrativeImportService."""
    return NarrativeImportService(parser=MarkdownNarrativeParser())


async def get_narrative_service(
    import_service: NarrativeImportService = Depends(get_narrative_import_service),
    repository: NarrativeRepository = Depends(get_narrative_repository),
) -> NarrativeService:
    """Wires NarrativeImportService and NarrativeRepository into NarrativeService."""
    return NarrativeService(import_service=import_service, repository=repository)


async def get_health_checker(
    client: AsyncClient = Depends(get_supabase_client),
) -> HealthChecker:
    """Wires SupabaseHealthChecker with the injected Supabase client."""
    return SupabaseHealthChecker(supabase_client=client)


def get_claim_extractor_service() -> ClaimExtractorService:
    """Wires ClaudeClaimExtractionProvider into ClaimExtractorService."""
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    provider = ClaudeClaimExtractionProvider(client=client)
    return ClaimExtractorService(provider=provider)
