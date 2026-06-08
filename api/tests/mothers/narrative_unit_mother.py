"""NarrativeUnitMother — builds NarrativeUnit test objects for all test scenarios.

All factory methods use hard-coded UUIDs so they can be referenced predictably
across test files without re-querying.
"""

from __future__ import annotations

from api.models.narrative_unit import Fragment, Scene, Work

# Seeded by migration 20260605000001_add_users.sql.
TEST_NARRATIVE_ID = "00000000-0000-0000-0000-000000000001"

# Hard-coded IDs for deterministic cross-test references.
WORK_ID = "10000000-0000-0000-0000-000000000001"
SCENE_ID = "10000000-0000-0000-0000-000000000002"
FRAGMENT_ID = "10000000-0000-0000-0000-000000000003"


class NarrativeUnitMother:
    """Factory for NarrativeUnit test objects.

    Use minimal_work() when only a root node is needed.
    Use work_with_scene_and_fragment() for Manuscript View and service tests.
    """

    @staticmethod
    def minimal_work() -> Work:
        """A Work node with no children and no ID (unsaved)."""
        return Work.create(title="Test Work", narrative_id=TEST_NARRATIVE_ID)

    @staticmethod
    def saved_work() -> Work:
        """A Work node that already has a database ID assigned."""
        return Work(
            id=WORK_ID,
            title="Test Work",
            content=None,
            position=1,
            narrative_id=TEST_NARRATIVE_ID,
            parent_id=None,
        )

    @staticmethod
    def work_with_scene_and_fragment() -> Work:
        """Work → Scene → Fragment tree.

        The minimal structure needed for Manuscript View tests.
        All nodes carry hard-coded IDs for predictable assertions.
        """
        work = Work(
            id=WORK_ID,
            title="Test Work",
            content=None,
            position=1,
            narrative_id=TEST_NARRATIVE_ID,
            parent_id=None,
        )
        scene = Scene(
            id=SCENE_ID,
            title="Test Scene",
            content=None,
            position=1,
            narrative_id=TEST_NARRATIVE_ID,
            parent_id=WORK_ID,
        )
        fragment = Fragment(
            id=FRAGMENT_ID,
            title=None,
            content="Es war einmal.",
            position=1,
            narrative_id=TEST_NARRATIVE_ID,
            parent_id=SCENE_ID,
        )
        scene.add_child(fragment)
        work.add_child(scene)
        return work

    @staticmethod
    def unsaved_fragment() -> Fragment:
        """A Fragment with no ID — ready to be passed to repository.add()."""
        return Fragment.create(
            content="Ein neuer Absatz.",
            narrative_id=TEST_NARRATIVE_ID,
            parent_id=SCENE_ID,
            position=2,
        )
