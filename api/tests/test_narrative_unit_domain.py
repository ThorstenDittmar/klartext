"""Tests for the NarrativeUnit domain hierarchy.

Invariants:
- Work.create() requires a non-empty title.
- Fragment.create() requires non-empty content.
- NarrativeUnit.from_record() dispatches to the correct subclass.
- add_child() attaches children; update_content() mutates content.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative_unit import InvalidOperationError, NarrativeUnitValidationError
from api.models.narrative_unit import (
    Chapter,
    Fragment,
    NarrativeUnit,
    Part,
    Scene,
    Work,
)

NARRATIVE_ID = "nar-001"
WORK_ID = "unit-001"
SCENE_ID = "unit-002"


class TestWork:
    def test_create_work_with_valid_title(self) -> None:
        """Work.create() builds a root node with no children, no parent and no ID."""
        work = Work.create(title="Der Aufstand", narrative_id=NARRATIVE_ID)
        assert work.title == "Der Aufstand"
        assert work.narrative_id == NARRATIVE_ID
        assert work.id is None
        assert work.parent_id is None
        assert work.children == []
        assert work.typ == "work"

    def test_create_work_with_empty_title_raises(self) -> None:
        """Work.create() rejects empty or whitespace-only titles."""
        with pytest.raises(NarrativeUnitValidationError, match="title must not be empty"):
            Work.create(title="   ", narrative_id=NARRATIVE_ID)


class TestPart:
    def test_create_part(self) -> None:
        """Part.create() sets typ='part' and links to parent_id."""
        part = Part.create(
            title="Erster Teil", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        assert part.typ == "part"
        assert part.parent_id == WORK_ID
        assert part.position == 1

    def test_create_part_empty_title_raises(self) -> None:
        """Part.create() rejects empty titles."""
        with pytest.raises(NarrativeUnitValidationError):
            Part.create(title="", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1)


class TestChapter:
    def test_create_chapter(self) -> None:
        """Chapter.create() sets typ='chapter'."""
        chapter = Chapter.create(
            title="Kapitel 1", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        assert chapter.typ == "chapter"
        assert chapter.id is None


class TestScene:
    def test_create_scene(self) -> None:
        """Scene.create() sets typ='scene' and requires a title."""
        scene = Scene.create(
            title="Die Verhandlung", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        assert scene.typ == "scene"
        assert scene.title == "Die Verhandlung"

    def test_create_scene_empty_title_raises(self) -> None:
        """Scene.create() rejects empty titles."""
        with pytest.raises(NarrativeUnitValidationError):
            Scene.create(title="   ", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1)


class TestFragment:
    def test_create_fragment_with_valid_content(self) -> None:
        """Fragment.create() builds an editing unit with content, no title."""
        fragment = Fragment.create(
            content="Es war einmal.",
            narrative_id=NARRATIVE_ID,
            parent_id=SCENE_ID,
            position=1,
        )
        assert fragment.content == "Es war einmal."
        assert fragment.parent_id == SCENE_ID
        assert fragment.position == 1
        assert fragment.title is None
        assert fragment.typ == "fragment"

    def test_create_fragment_with_empty_content_raises(self) -> None:
        """Fragment.create() rejects empty or whitespace-only content."""
        with pytest.raises(NarrativeUnitValidationError, match="content must not be empty"):
            Fragment.create(
                content="   ",
                narrative_id=NARRATIVE_ID,
                parent_id=SCENE_ID,
                position=1,
            )

    def test_update_content_replaces_text(self) -> None:
        """update_content() mutates the fragment's content in place."""
        fragment = Fragment.create(
            content="Original.", narrative_id=NARRATIVE_ID, parent_id=SCENE_ID, position=1
        )
        fragment.update_content("Updated.")
        assert fragment.content == "Updated."


class TestFromRecord:
    def test_from_record_dispatches_to_work(self) -> None:
        """NarrativeUnit.from_record() returns a Work instance for typ='work'."""
        record = {
            "id": WORK_ID,
            "typ": "work",
            "title": "Test Work",
            "content": None,
            "position": 1,
            "narrative_id": NARRATIVE_ID,
            "parent_id": None,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Work)
        assert unit.id == WORK_ID
        assert unit.title == "Test Work"

    def test_from_record_dispatches_to_part(self) -> None:
        """NarrativeUnit.from_record() returns a Part for typ='part'."""
        record = {
            "id": "p-001",
            "typ": "part",
            "title": "Teil 1",
            "content": None,
            "position": 1,
            "narrative_id": NARRATIVE_ID,
            "parent_id": WORK_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Part)

    def test_from_record_dispatches_to_chapter(self) -> None:
        """NarrativeUnit.from_record() returns a Chapter for typ='chapter'."""
        record = {
            "id": "c-001",
            "typ": "chapter",
            "title": "Kap 1",
            "content": None,
            "position": 1,
            "narrative_id": NARRATIVE_ID,
            "parent_id": WORK_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Chapter)

    def test_from_record_dispatches_to_scene(self) -> None:
        """NarrativeUnit.from_record() returns a Scene for typ='scene'."""
        record = {
            "id": SCENE_ID,
            "typ": "scene",
            "title": "Szene 1",
            "content": None,
            "position": 1,
            "narrative_id": NARRATIVE_ID,
            "parent_id": WORK_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Scene)

    def test_from_record_dispatches_to_fragment(self) -> None:
        """NarrativeUnit.from_record() returns a Fragment for typ='fragment'."""
        record = {
            "id": "f-001",
            "typ": "fragment",
            "title": None,
            "content": "Some text.",
            "position": 1,
            "narrative_id": NARRATIVE_ID,
            "parent_id": SCENE_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Fragment)
        assert unit.content == "Some text."

    def test_from_record_unknown_typ_raises(self) -> None:
        """NarrativeUnit.from_record() raises NarrativeUnitValidationError for unknown types."""
        record = {
            "id": "x-001",
            "typ": "unknown",
            "title": None,
            "content": None,
            "position": 1,
            "narrative_id": NARRATIVE_ID,
            "parent_id": None,
        }
        with pytest.raises(NarrativeUnitValidationError, match="Unknown narrative unit type"):
            NarrativeUnit.from_record(record)


class TestAddChild:
    def test_add_child_appends_to_children_list(self) -> None:
        """add_child() appends the child unit to the parent's children list."""
        work = Work.create(title="Test Work", narrative_id=NARRATIVE_ID)
        scene = Scene.create(
            title="Test Scene", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        work.add_child(scene)
        assert len(work.children) == 1
        assert work.children[0] is scene

    def test_add_multiple_children_preserves_order(self) -> None:
        """add_child() preserves insertion order."""
        work = Work.create(title="Test Work", narrative_id=NARRATIVE_ID)
        scene1 = Scene.create(
            title="Szene 1", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        scene2 = Scene.create(
            title="Szene 2", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=2
        )
        work.add_child(scene1)
        work.add_child(scene2)
        assert work.children[0].title == "Szene 1"
        assert work.children[1].title == "Szene 2"


class TestUpdateTitle:
    def test_update_title_renames_node(self) -> None:
        """update_title() replaces the node's title."""
        scene = Scene.create(
            title="Old Title", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        scene.update_title("New Title")
        assert scene.title == "New Title"

    def test_update_title_empty_raises(self) -> None:
        """update_title() rejects empty titles."""
        scene = Scene.create(
            title="Title", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
        )
        with pytest.raises(NarrativeUnitValidationError, match="title must not be empty"):
            scene.update_title("   ")

    def test_fragment_update_title_raises_invalid_operation(self) -> None:
        """Fragment.update_title() raises InvalidOperationError — Fragment has no title."""
        fragment = Fragment.create(
            content="Text.", narrative_id=NARRATIVE_ID, parent_id=SCENE_ID, position=1
        )
        with pytest.raises(InvalidOperationError, match="Fragment has no title"):
            fragment.update_title("A Title")
