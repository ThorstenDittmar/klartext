"""Tests for the UserRepository contract.

Unit tests run against FakeUserRepository. Integration tests call the real
Supabase database and are marked @pytest.mark.integration.
Run integration tests separately: pytest -m integration
"""

from __future__ import annotations

import pytest

from api.exceptions.user import UserNotFoundError
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID, FakeUserRepository

# ---------------------------------------------------------------------------
# Unit tests — FakeUserRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_user_repository_find_default_returns_thorsten() -> None:
    """Expects find_default() to return the pre-seeded user Thorsten."""
    repo = FakeUserRepository()

    user = await repo.find_default()

    assert user.id == DEFAULT_USER_ID
    assert user.name == "Thorsten"


@pytest.mark.asyncio
async def test_user_repository_find_by_id_returns_user() -> None:
    """Expects find_by_id() to return Thorsten when queried by his UUID."""
    repo = FakeUserRepository()

    user = await repo.find_by_id(DEFAULT_USER_ID)

    assert user.id == DEFAULT_USER_ID
    assert user.name == "Thorsten"


@pytest.mark.asyncio
async def test_user_repository_find_by_id_raises_for_unknown_id() -> None:
    """Expects UserNotFoundError when querying with a non-existent UUID."""
    repo = FakeUserRepository()

    with pytest.raises(UserNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000099")


# ---------------------------------------------------------------------------
# Integration – requires a running Supabase instance
# Run with: pytest -m integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_user_repository_find_default_returns_thorsten() -> None:
    """Calls the real database. Expects find_default() to return the seeded user Thorsten.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_user_repository import SupabaseUserRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseUserRepository(client=client)

    user = await repo.find_default()

    assert user.id == DEFAULT_USER_ID
    assert user.name == "Thorsten"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_user_repository_find_by_id_returns_user() -> None:
    """Calls the real database. Expects find_by_id() to return Thorsten when queried by his UUID.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_user_repository import SupabaseUserRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseUserRepository(client=client)

    user = await repo.find_by_id(DEFAULT_USER_ID)

    assert user.id == DEFAULT_USER_ID
    assert user.name == "Thorsten"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_user_repository_find_by_id_raises_for_unknown_id() -> None:
    """Calls the real database. Expects UserNotFoundError for a non-existent UUID.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os

    from supabase import acreate_client

    from api.repositories.supabase_user_repository import SupabaseUserRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseUserRepository(client=client)

    with pytest.raises(UserNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000099")
