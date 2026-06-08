"""Tests for NarrativeUnitService.

All tests use FakeNarrativeUnitRepository — no database involved.
"""

from __future__ import annotations

import pytest

from api.services.narrative_unit_service import NarrativeUnitService
from api.tests.fakes.fake_narrative_unit_repository import FakeNarrativeUnitRepository
from api.tests.mothers.narrative_unit_mother import (
    TEST_NARRATIVE_ID,
    NarrativeUnitMother,
)


@pytest.fixture
def repository() -> FakeNarrativeUnitRepository:
    return FakeNarrativeUnitRepository()


@pytest.fixture
def service(repository: FakeNarrativeUnitRepository) -> NarrativeUnitService:
    return NarrativeUnitService(repository=repository)


class TestGetTree:
    async def test_returns_none_when_no_units_exist(self, service: NarrativeUnitService) -> None:
        """get_tree() returns None when no units have been added to the narrative."""
        result = await service.get_tree(TEST_NARRATIVE_ID)
        assert result is None

    async def test_returns_tree_when_pre_seeded(
        self,
        service: NarrativeUnitService,
        repository: FakeNarrativeUnitRepository,
    ) -> None:
        """get_tree() returns the root node from the repository."""
        tree = NarrativeUnitMother.work_with_scene_and_fragment()
        repository.set_tree(TEST_NARRATIVE_ID, tree)
        result = await service.get_tree(TEST_NARRATIVE_ID)
        assert result is tree


class TestAddUnit:
    async def test_add_unit_assigns_id(self, service: NarrativeUnitService) -> None:
        """add_unit() returns the unit with a non-None ID assigned by the repository."""
        unit = NarrativeUnitMother.unsaved_fragment()
        result = await service.add_unit(unit)
        assert result.id is not None

    async def test_add_unit_preserves_content(self, service: NarrativeUnitService) -> None:
        """add_unit() preserves the unit's content after save."""
        unit = NarrativeUnitMother.unsaved_fragment()
        result = await service.add_unit(unit)
        assert result.content == "Ein neuer Absatz."


class TestUpdateUnit:
    async def test_update_unit_persists_content(self, service: NarrativeUnitService) -> None:
        """update_unit() persists the updated content via the repository."""
        unit = NarrativeUnitMother.unsaved_fragment()
        saved = await service.add_unit(unit)
        saved.update_content("Geänderter Absatz.")
        result = await service.update_unit(saved)
        assert result.content == "Geänderter Absatz."

    async def test_update_unit_returns_updated_unit(self, service: NarrativeUnitService) -> None:
        """update_unit() returns the unit as it came back from the repository."""
        # Use Work — Fragment.update_title() raises InvalidOperationError by design.
        unit = NarrativeUnitMother.minimal_work()
        saved = await service.add_unit(unit)
        saved.update_title("Neuer Titel")
        result = await service.update_unit(saved)
        assert result.title == "Neuer Titel"


class TestRemoveUnit:
    async def test_remove_unit_does_not_raise(self, service: NarrativeUnitService) -> None:
        """remove_unit() completes without error for a known unit ID."""
        unit = NarrativeUnitMother.unsaved_fragment()
        saved = await service.add_unit(unit)
        assert saved.id is not None
        await service.remove_unit(saved.id)  # must not raise
