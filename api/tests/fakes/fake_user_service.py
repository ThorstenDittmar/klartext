"""Fake UserService for use in router tests that need a UserService dependency."""

from __future__ import annotations

from api.models.user import User
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID


class FakeUserService:
    """Returns the pre-seeded default user without hitting the database.

    Use this in router tests to satisfy get_user_service dependencies
    without triggering a real Supabase connection.
    """

    async def get_default(self) -> User:
        """Returns a User with the default ID used in test fixtures."""
        return User(id=DEFAULT_USER_ID, name="Thorsten")
