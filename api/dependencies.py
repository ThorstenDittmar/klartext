"""Dependency wiring for FastAPI.

Each get_* function is the single place where a concrete implementation
is chosen. Tests override these via app.dependency_overrides.

DI chain:
  get_supabase_client ─┬─► get_narrative_repository ─► get_narrative_service
                       └─► get_claim_repository ────────► get_claim_service
                       └─► get_health_checker
                       └─► get_causal_model_repository ─► get_causal_model_service
  get_narrative_import_service ────────────────────────► get_narrative_service
  get_consistency_checker ─────────────────────────────► get_causal_model_service
  (standalone) ────────────────────────────────────────► get_claim_extractor_service
"""

from __future__ import annotations

import os
import ssl

import anthropic
import httpx
from fastapi import Depends
from supabase import AsyncClient, acreate_client

from api.parsers.docx_narrative_parser import DocxNarrativeParser
from api.parsers.markdown_narrative_parser import MarkdownNarrativeParser
from api.providers.claude_claim_extraction_provider import ClaudeClaimExtractionProvider
from api.providers.claude_consistency_checker import ClaudeConsistencyChecker
from api.providers.consistency_checker import ConsistencyChecker
from api.repositories.causal_model_repository import CausalModelRepository
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository
from api.repositories.supabase_causal_model_repository import SupabaseCausalModelRepository
from api.repositories.supabase_claim_repository import SupabaseClaimRepository
from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
from api.services.causal_model_service import CausalModelService
from api.services.claim_extractor_service import ClaimExtractorService
from api.services.claim_service import ClaimService
from api.services.health_service import HealthChecker, SupabaseHealthChecker
from api.services.narrative_analysis_service import NarrativeAnalysisService
from api.services.narrative_import_service import NarrativeImportService
from api.services.narrative_service import NarrativeService
from api.services.wirkgefuege_suggestion_service import WirkgefuegeSuggestionService


def _make_anthropic_client() -> anthropic.AsyncAnthropic:
    """Creates an AsyncAnthropic client with the system SSL certificate bundle.

    The default httpx client uses certifi's CA bundle which may not include
    all certificates needed on this system. Passing the system SSL context
    fixes connection errors on macOS.
    """
    return anthropic.AsyncAnthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        http_client=httpx.AsyncClient(verify=ssl.create_default_context()),
    )


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
    """Wires text and binary parsers into NarrativeImportService."""
    return NarrativeImportService(
        parser=MarkdownNarrativeParser(),
        file_parsers={".docx": DocxNarrativeParser()},
    )


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
    client = _make_anthropic_client()
    provider = ClaudeClaimExtractionProvider(client=client)
    return ClaimExtractorService(provider=provider)


async def get_claim_service(
    repository: ClaimRepository = Depends(get_claim_repository),
) -> ClaimService:
    """Wires ClaimRepository into ClaimService."""
    return ClaimService(repository=repository)


async def get_causal_model_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> CausalModelRepository:
    """Wires SupabaseCausalModelRepository with the injected Supabase client."""
    return SupabaseCausalModelRepository(client=client)


def get_consistency_checker() -> ConsistencyChecker:
    """Wires ClaudeConsistencyChecker with an Anthropic async client."""
    client = _make_anthropic_client()
    return ClaudeConsistencyChecker(client=client)


async def get_causal_model_service(
    repository: CausalModelRepository = Depends(get_causal_model_repository),
    checker: ConsistencyChecker = Depends(get_consistency_checker),
) -> CausalModelService:
    """Wires CausalModelRepository and ConsistencyChecker into CausalModelService."""
    return CausalModelService(repository=repository, consistency_checker=checker)


async def get_narrative_analysis_service(
    repository: NarrativeRepository = Depends(get_narrative_repository),
) -> NarrativeAnalysisService:
    """Wires NarrativeRepository and ClaudeNarrativeAnalysisProvider into NarrativeAnalysisService.

    Uses a lazy import for ClaudeNarrativeAnalysisProvider so the module can be loaded
    even before the Claude provider file is created (Task 6).
    """
    from api.providers.claude_narrative_analysis_provider import (
        ClaudeNarrativeAnalysisProvider,  # noqa: PLC0415
    )

    client = _make_anthropic_client()
    provider = ClaudeNarrativeAnalysisProvider(client=client)
    return NarrativeAnalysisService(repository=repository, provider=provider)


async def get_wirkgefuege_suggestion_service(
    narrative_repository: NarrativeRepository = Depends(get_narrative_repository),
    claim_repository: ClaimRepository = Depends(get_claim_repository),
) -> WirkgefuegeSuggestionService:
    """Wires repositories and ClaudeWirkgefuegeSuggestionProvider into WirkgefuegeSuggestionService.

    Uses a lazy import for ClaudeWirkgefuegeSuggestionProvider so the module can be loaded
    even before the Claude provider file is created (Task 6).
    """
    from api.providers.claude_wirkgefuege_suggestion_provider import (
        ClaudeWirkgefuegeSuggestionProvider,  # noqa: PLC0415
    )

    client = _make_anthropic_client()
    provider = ClaudeWirkgefuegeSuggestionProvider(client=client)
    return WirkgefuegeSuggestionService(
        narrative_repository=narrative_repository,
        claim_repository=claim_repository,
        provider=provider,
    )
