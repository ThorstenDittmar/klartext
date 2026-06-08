"""Infrastructure tests: schema integrity checks for PostgREST FK relationships.

These tests make real calls to the local Supabase instance and run under
the ``@pytest.mark.integration`` marker. They must pass after every
``klartext db reset`` — if they fail, a migration is either missing or
contains a stale table/column reference.

Why these tests exist
---------------------
PostgREST resolves embedded resource names (e.g. ``claims(count)``) at
*runtime* from the schema cache. If the FK relationship is not present
in the schema cache, PostgREST returns PGRST200 and the API raises a
500 error. A stale table name in the backfill step of a migration can
silently succeed on an incremental apply (the backfill updates 0 rows)
but fail on a clean ``db reset`` because the old name no longer exists.

These tests reproduce the actual PostgREST query that ``list_summaries_for_user``
uses so that the exact failure mode is caught by CI before it reaches a
human tester.
"""

from __future__ import annotations

import os

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgrest_resolves_claims_count_on_narrative() -> None:
    """Verifies that PostgREST can resolve claims(count) embedded on narrative.

    This requires claims.narrative_id to be a real FK to narrative.id in
    the schema cache. If the migration that adds that column failed or was
    not applied, PostgREST returns PGRST200 and this test fails.
    """
    from supabase import acreate_client

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )

    # Mirrors exactly what SupabaseNarrativeRepository.list_summaries_for_user does
    response = await client.table("narrative").select("id, title, claims(count)").limit(1).execute()

    # If PostgREST cannot resolve the FK the call raises an exception before we
    # get here. Reaching this assertion means the relationship is intact.
    assert response.data is not None, "PostgREST returned no data — FK not resolved"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgrest_resolves_narrative_units_count_on_narrative() -> None:
    """Verifies that PostgREST can resolve narrative_units(count) embedded on narrative.

    Ensures the scene-count part of the summary query also works.
    """
    from supabase import acreate_client

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )

    response = (
        await client.table("narrative")
        .select("id, title, narrative_units(count)")
        .limit(1)
        .execute()
    )

    assert response.data is not None, "PostgREST returned no data — FK not resolved"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgrest_resolves_narrative_actors_count_on_narrative() -> None:
    """Verifies that PostgREST can resolve narrative_actors(count) embedded on narrative.

    Ensures the actor-count part of the summary query also works.
    """
    from supabase import acreate_client

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )

    response = (
        await client.table("narrative")
        .select("id, title, narrative_actors(count)")
        .limit(1)
        .execute()
    )

    assert response.data is not None, "PostgREST returned no data — FK not resolved"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_units_health_endpoint_returns_ok() -> None:
    """GET /narrative-units/health returns 200 for the narrative-units router."""
    from httpx import ASGITransport, AsyncClient

    from api.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/narrative-units/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_claims_narrative_id_column_exists() -> None:
    """Verifies that claims.narrative_id column was added by the migration.

    Selecting the column directly is the simplest check that the ALTER TABLE
    in 20260605000002_claims_narrative_id.sql was applied.
    """
    from supabase import acreate_client

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )

    # Select only the narrative_id column — PostgREST returns 400 if it
    # doesn't exist, which causes an exception before the assertion runs.
    response = await client.table("claims").select("narrative_id").limit(0).execute()

    assert response.data is not None, "claims.narrative_id column does not exist"
