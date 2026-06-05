"""Tests for UserService."""

from __future__ import annotations

import pytest

from api.exceptions.user import UserNotFoundError
from api.services.user_service import UserService
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID, FakeUserRepository


class TestUserService:
    def setup_method(self) -> None:
        """Sets up a UserService backed by a FakeUserRepository for each test."""
        self._repo = FakeUserRepository()
        self._service = UserService(self._repo)

    @pytest.mark.asyncio
    async def test_get_default_returns_thorsten(self) -> None:
        """Expects get_default() to return the pre-seeded user Thorsten."""
        user = await self._service.get_default()
        assert user.id == DEFAULT_USER_ID
        assert user.name == "Thorsten"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_user(self) -> None:
        """Expects get_by_id() to return the user when found."""
        user = await self._service.get_by_id(DEFAULT_USER_ID)
        assert user.id == DEFAULT_USER_ID

    @pytest.mark.asyncio
    async def test_get_by_id_raises_for_unknown_id(self) -> None:
        """Expects UserNotFoundError when querying a non-existent user ID."""
        with pytest.raises(UserNotFoundError):
            await self._service.get_by_id("00000000-0000-0000-0000-000000000099")
