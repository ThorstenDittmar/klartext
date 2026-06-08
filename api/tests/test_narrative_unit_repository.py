"""Integration tests for SupabaseNarrativeUnitRepository.

These tests hit the real Supabase dev database. Each test creates a fresh
Narrative row, runs the assertion, and cleans up — no shared state.

Run with: pytest api/tests/test_narrative_unit_repository.py -v -m integration
"""

from __future__ import annotations

import os

import pytest
from supabase import AsyncClient, acreate_client

from api.models.narrative_unit import Fragment, Scene, Work
from api.repositories.supabase_narrative_repository import SupabaseNarrativeRepository
from api.repositories.supabase_narrative_unit_repository import (
    SupabaseNarrativeUnitRepository,
)
from api.tests.mothers.narrative_mother import NarrativeMother


async def _make_client() -> AsyncClient:
    return await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )


async def _setup() -> tuple[SupabaseNarrativeUnitRepository, str]:
    """Creates a fresh Narrative and returns (repository, narrative_id)."""
    client = await _make_client()
    narrative_repo = SupabaseNarrativeRepository(client=client)
    saved_narrative = await narrative_repo.save(NarrativeMother.empty())
    assert saved_narrative.id is not None
    repo = SupabaseNarrativeUnitRepository(client=client)
    return repo, saved_narrative.id


async def _teardown(repo: SupabaseNarrativeUnitRepository, narrative_id: str) -> None:
    """Removes all narrative_units and the narrative row itself."""
    await repo._client.table("narrative_units").delete().eq("narrative_id", narrative_id).execute()
    await repo._client.table("narrative").delete().eq("id", narrative_id).execute()


@pytest.mark.integration
@pytest.mark.asyncio
class TestLoadTree:
    async def test_load_tree_returns_none_when_empty(self) -> None:
        """load_tree() returns None when no units exist for the narrative."""
        repo, narrative_id = await _setup()
        try:
            result = await repo.load_tree(narrative_id)
            assert result is None
        finally:
            await _teardown(repo, narrative_id)

    async def test_load_tree_returns_assembled_work(self) -> None:
        """load_tree() returns a Work with its Scene children attached."""
        repo, narrative_id = await _setup()
        try:
            work_result = await repo.add(
                Work.create(title="Integration Work", narrative_id=narrative_id)
            )
            assert work_result.id is not None

            scene_result = await repo.add(
                Scene.create(
                    title="Integration Scene",
                    narrative_id=narrative_id,
                    parent_id=work_result.id,
                    position=1,
                )
            )
            assert scene_result.id is not None

            tree = await repo.load_tree(narrative_id)
            assert tree is not None
            assert isinstance(tree, Work)
            assert tree.title == "Integration Work"
            assert len(tree.children) == 1
            assert isinstance(tree.children[0], Scene)
            assert tree.children[0].title == "Integration Scene"
        finally:
            await _teardown(repo, narrative_id)


@pytest.mark.integration
@pytest.mark.asyncio
class TestAdd:
    async def test_add_assigns_id(self) -> None:
        """add() inserts a Work and returns it with a database-assigned ID."""
        repo, narrative_id = await _setup()
        try:
            work = Work.create(title="New Work", narrative_id=narrative_id)
            saved = await repo.add(work)
            assert saved.id is not None
            assert saved.title == "New Work"
            assert saved.typ == "work"
        finally:
            await _teardown(repo, narrative_id)

    async def test_add_fragment_preserves_content(self) -> None:
        """add() persists Fragment content correctly."""
        repo, narrative_id = await _setup()
        try:
            work = await repo.add(Work.create(title="Work", narrative_id=narrative_id))
            scene = await repo.add(
                Scene.create(
                    title="Scene",
                    narrative_id=narrative_id,
                    parent_id=work.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            fragment = await repo.add(
                Fragment.create(
                    content="Ein Absatz.",
                    narrative_id=narrative_id,
                    parent_id=scene.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            assert fragment.content == "Ein Absatz."
        finally:
            await _teardown(repo, narrative_id)


@pytest.mark.integration
@pytest.mark.asyncio
class TestUpdate:
    async def test_update_persists_new_content(self) -> None:
        """update() saves new content and returns the updated fragment."""
        repo, narrative_id = await _setup()
        try:
            work = await repo.add(Work.create(title="Work", narrative_id=narrative_id))
            scene = await repo.add(
                Scene.create(
                    title="Scene",
                    narrative_id=narrative_id,
                    parent_id=work.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            fragment = await repo.add(
                Fragment.create(
                    content="Original.",
                    narrative_id=narrative_id,
                    parent_id=scene.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            fragment.update_content("Updated.")
            updated = await repo.update(fragment)
            assert updated.content == "Updated."
        finally:
            await _teardown(repo, narrative_id)


@pytest.mark.integration
@pytest.mark.asyncio
class TestRemove:
    async def test_remove_deletes_leaf_node(self) -> None:
        """remove() deletes a fragment row; subsequent load_tree shows it gone."""
        repo, narrative_id = await _setup()
        try:
            work = await repo.add(Work.create(title="Work", narrative_id=narrative_id))
            scene = await repo.add(
                Scene.create(
                    title="Scene",
                    narrative_id=narrative_id,
                    parent_id=work.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            fragment = await repo.add(
                Fragment.create(
                    content="To delete.",
                    narrative_id=narrative_id,
                    parent_id=scene.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            assert fragment.id is not None
            await repo.remove(fragment.id)
            tree = await repo.load_tree(narrative_id)
            assert tree is not None
            assert len(tree.children[0].children) == 0
        finally:
            await _teardown(repo, narrative_id)

    async def test_remove_parent_cascades_to_children(self) -> None:
        """remove() on a Scene removes its Fragment children via ON DELETE CASCADE."""
        repo, narrative_id = await _setup()
        try:
            work = await repo.add(Work.create(title="Work", narrative_id=narrative_id))
            scene = await repo.add(
                Scene.create(
                    title="Scene",
                    narrative_id=narrative_id,
                    parent_id=work.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            await repo.add(
                Fragment.create(
                    content="Orphan.",
                    narrative_id=narrative_id,
                    parent_id=scene.id,  # type: ignore[arg-type]
                    position=1,
                )
            )
            assert scene.id is not None
            await repo.remove(scene.id)
            tree = await repo.load_tree(narrative_id)
            assert tree is not None
            assert len(tree.children) == 0
        finally:
            await _teardown(repo, narrative_id)
