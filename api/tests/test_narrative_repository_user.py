"""Tests for user-scoped narrative repository operations."""

from __future__ import annotations

import pytest

from api.tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID

DEFAULT_TITLE = "My Narrative"


class TestNarrativeRepositoryUser:
    def setup_method(self) -> None:
        """Sets up FakeNarrativeRepository for each test."""
        self._repo = FakeNarrativeRepository()

    @pytest.mark.asyncio
    async def test_list_for_user_returns_narratives_for_that_user(self) -> None:
        """Expects list_for_user() to return only narratives owned by the given user."""
        from api.models.narrative import Narrative

        narrative = Narrative.create(DEFAULT_TITLE)
        narrative.assign_user(DEFAULT_USER_ID)
        await self._repo.save(narrative)

        results = await self._repo.list_for_user(DEFAULT_USER_ID)
        assert len(results) == 1
        assert results[0].title == DEFAULT_TITLE

    @pytest.mark.asyncio
    async def test_list_for_user_returns_empty_for_unknown_user(self) -> None:
        """Expects list_for_user() to return an empty list when no narratives exist for the user."""
        results = await self._repo.list_for_user("00000000-0000-0000-0000-000000000099")
        assert results == []

    @pytest.mark.asyncio
    async def test_list_for_user_filters_by_user_id(self) -> None:
        """Expects list_for_user() to exclude narratives owned by other users."""
        from api.models.narrative import Narrative

        n1 = Narrative.create("User1 Narrative")
        n1.assign_user(DEFAULT_USER_ID)
        await self._repo.save(n1)

        n2 = Narrative.create("User2 Narrative")
        n2.assign_user("00000000-0000-0000-0000-000000000002")
        await self._repo.save(n2)

        results = await self._repo.list_for_user(DEFAULT_USER_ID)
        assert len(results) == 1
        assert results[0].title == "User1 Narrative"
