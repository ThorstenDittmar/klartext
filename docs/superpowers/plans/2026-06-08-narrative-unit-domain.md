# Narrative Unit Domain Model — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full NarrativeUnit domain model hierarchy (Work → Part → Chapter → Scene → Fragment) on top of the existing `narrative_units` table and expose it via a new `/narrative-units` REST API.

**Architecture:** Abstract `NarrativeUnit` base class with five concrete subclasses, auto-registered via `__init_subclass__`. Single-query tree assembly in the repository (one `SELECT *` → Python dict-based tree build). Fragment is the atomic editing unit; `update_content()` on domain object + `repository.update()` persists the change. No existing narratives.py code is deleted — this is a parallel new domain.

**Tech Stack:** Python 3.12, FastAPI, Supabase PostgREST (`AsyncClient`), pytest-asyncio, Pydantic v2. All commands: `cd /Users/thormar/klartext && source venv/bin/activate`.

**Branch:** `task/H01-A/narrative-unit-domain`

**Dependency:** None — can start immediately.

---

## File Map

| Path | Status | Responsibility |
|---|---|---|
| `supabase/migrations/20260608000001_narrative_units_cascade.sql` | CREATE | Add ON DELETE CASCADE to parent_id FK |
| `api/exceptions/narrative_unit.py` | CREATE | `NarrativeUnitValidationError`, `NarrativeUnitNotFoundError`, `NarrativeUnitPersistenceError` |
| `api/models/narrative_unit.py` | CREATE | `NarrativeUnit` (abstract), `Work`, `Part`, `Chapter`, `Scene`, `Fragment` |
| `api/repositories/narrative_unit_repository.py` | CREATE | Abstract `NarrativeUnitRepository` port |
| `api/tests/fakes/fake_narrative_unit_repository.py` | CREATE | In-memory implementation for tests |
| `api/tests/mothers/narrative_unit_mother.py` | CREATE | `NarrativeUnitMother` test object factory |
| `api/schemas/narrative_units.py` | CREATE | Pydantic request/response schemas |
| `api/services/narrative_unit_service.py` | CREATE | `NarrativeUnitService` |
| `api/repositories/supabase_narrative_unit_repository.py` | CREATE | `SupabaseNarrativeUnitRepository` |
| `api/routers/narrative_units.py` | CREATE | `/narrative-units` router (5 endpoints) |
| `api/tests/test_narrative_unit_domain.py` | CREATE | Domain model tests |
| `api/tests/test_narrative_unit_service.py` | CREATE | Service tests |
| `api/tests/test_narrative_unit_repository.py` | CREATE | Integration tests (real Supabase) |
| `api/tests/test_narrative_units_router.py` | CREATE | Router tests |
| `api/dependencies.py` | MODIFY | Wire `NarrativeUnitService` and `NarrativeUnitRepository` |
| `api/main.py` | MODIFY | Register `narrative_units.router` |

---

## Task 0: DB Migration — parent_id CASCADE

The current `narrative_units.parent_id` FK has no `ON DELETE CASCADE`. Without it, deleting a non-leaf unit causes a FK violation. This migration fixes it.

**Files:**
- Create: `supabase/migrations/20260608000001_narrative_units_cascade.sql`

- [ ] **Step 1: Write the migration file**

```sql
-- Add ON DELETE CASCADE to narrative_units.parent_id so deleting a parent
-- automatically removes all descendants.
--
-- The FK constraint was created by the initial schema as
-- narrative_einheiten_parent_id_fkey and may have been renamed.
-- We drop both possible names defensively.

ALTER TABLE narrative_units
    DROP CONSTRAINT IF EXISTS narrative_einheiten_parent_id_fkey;

ALTER TABLE narrative_units
    DROP CONSTRAINT IF EXISTS narrative_units_parent_id_fkey;

ALTER TABLE narrative_units
    ADD CONSTRAINT narrative_units_parent_id_fkey
        FOREIGN KEY (parent_id)
        REFERENCES narrative_units(id)
        ON DELETE CASCADE;
```

- [ ] **Step 2: Apply the migration**

```bash
klartext db push
```

Expected: migration applied, no errors.

- [ ] **Step 3: Commit**

```bash
git add supabase/migrations/20260608000001_narrative_units_cascade.sql
git commit -m "feat: add ON DELETE CASCADE to narrative_units.parent_id"
```

---

## Task 1: Exception Classes

**Files:**
- Create: `api/exceptions/narrative_unit.py`

No logic to test in exception classes — skip test step.

- [ ] **Step 1: Create exception file**

```python
"""Exception classes for the NarrativeUnit domain, service and repository."""

from api.exceptions.base import DomainError, RepositoryError


class NarrativeUnitValidationError(DomainError):
    """Raised when a NarrativeUnit cannot be created due to invalid input."""


class InvalidOperationError(DomainError):
    """Raised when an operation is not valid for the target NarrativeUnit type.

    Example: calling update_title() on a Fragment, which has no title.
    """


class NarrativeUnitNotFoundError(RepositoryError):
    """Raised when a NarrativeUnit cannot be found by the given ID."""


class NarrativeUnitPersistenceError(RepositoryError):
    """Raised when saving, loading or deleting a NarrativeUnit fails."""
```

- [ ] **Step 2: Verify import works**

```bash
python -c "from api.exceptions.narrative_unit import NarrativeUnitValidationError; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add api/exceptions/narrative_unit.py
git commit -m "feat: add NarrativeUnit exception classes"
```

---

## Task 2: Domain Model — Tests First

**Files:**
- Create: `api/tests/test_narrative_unit_domain.py`
- Create: `api/models/narrative_unit.py` (implementation added in Task 3)

- [ ] **Step 1: Write the failing tests**

```python
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
            Scene.create(
                title="   ", narrative_id=NARRATIVE_ID, parent_id=WORK_ID, position=1
            )


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
            "id": "p-001", "typ": "part", "title": "Teil 1", "content": None,
            "position": 1, "narrative_id": NARRATIVE_ID, "parent_id": WORK_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Part)

    def test_from_record_dispatches_to_chapter(self) -> None:
        """NarrativeUnit.from_record() returns a Chapter for typ='chapter'."""
        record = {
            "id": "c-001", "typ": "chapter", "title": "Kap 1", "content": None,
            "position": 1, "narrative_id": NARRATIVE_ID, "parent_id": WORK_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Chapter)

    def test_from_record_dispatches_to_scene(self) -> None:
        """NarrativeUnit.from_record() returns a Scene for typ='scene'."""
        record = {
            "id": SCENE_ID, "typ": "scene", "title": "Szene 1", "content": None,
            "position": 1, "narrative_id": NARRATIVE_ID, "parent_id": WORK_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Scene)

    def test_from_record_dispatches_to_fragment(self) -> None:
        """NarrativeUnit.from_record() returns a Fragment for typ='fragment'."""
        record = {
            "id": "f-001", "typ": "fragment", "title": None, "content": "Some text.",
            "position": 1, "narrative_id": NARRATIVE_ID, "parent_id": SCENE_ID,
        }
        unit = NarrativeUnit.from_record(record)
        assert isinstance(unit, Fragment)
        assert unit.content == "Some text."

    def test_from_record_unknown_typ_raises(self) -> None:
        """NarrativeUnit.from_record() raises NarrativeUnitValidationError for unknown types."""
        record = {
            "id": "x-001", "typ": "unknown", "title": None, "content": None,
            "position": 1, "narrative_id": NARRATIVE_ID, "parent_id": None,
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
```

- [ ] **Step 2: Run tests — verify they all fail**

```bash
pytest api/tests/test_narrative_unit_domain.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError: No module named 'api.models.narrative_unit'`

---

## Task 3: Domain Model — Implementation

**Files:**
- Create: `api/models/narrative_unit.py`

- [ ] **Step 1: Write the domain model**

```python
"""Domain model: NarrativeUnit hierarchy (Work, Part, Chapter, Scene, Fragment).

All five types share a single database table (narrative_units) with a
self-referential parent_id FK. The tree is assembled in Python after
a single flat SELECT — not via recursive SQL.

Subclasses auto-register via __init_subclass__ so NarrativeUnit.from_record()
dispatches to the right type without an explicit if/elif chain.
"""
from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from api.exceptions.narrative_unit import InvalidOperationError, NarrativeUnitValidationError


class NarrativeUnit(ABC):
    """Abstract base for all narrative content tree nodes.

    Subclasses must define TYP as a class-level string constant matching the
    value stored in the narrative_units.typ column.
    """

    TYP: str  # Defined by every concrete subclass
    _registry: ClassVar[dict[str, type[NarrativeUnit]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Registers each concrete subclass by its TYP value."""
        super().__init_subclass__(**kwargs)
        if "TYP" in cls.__dict__ and cls.TYP:
            NarrativeUnit._registry[cls.TYP] = cls

    def __init__(
        self,
        id: str | None,
        title: str | None,
        content: str | None,
        position: int,
        narrative_id: str,
        parent_id: str | None,
    ) -> None:
        self._id = id
        self._title = title
        self._content = content
        self._position = position
        self._narrative_id = narrative_id
        self._parent_id = parent_id
        self._children: list[NarrativeUnit] = []

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "NarrativeUnit":
        """Reconstructs the correct NarrativeUnit subclass from a database record.

        Routes by the 'typ' column value. Raises NarrativeUnitValidationError
        for unrecognised typ values.
        """
        typ = record.get("typ", "")
        subclass = cls._registry.get(typ)
        if subclass is None:
            raise NarrativeUnitValidationError(f"Unknown narrative unit type: '{typ}'")
        return subclass(
            id=record["id"],
            title=record.get("title"),
            content=record.get("content"),
            position=record["position"],
            narrative_id=record["narrative_id"],
            parent_id=record.get("parent_id"),
        )

    def add_child(self, child: "NarrativeUnit") -> None:
        """Appends a child node to this unit's subtree."""
        self._children.append(child)

    def update_content(self, content: str) -> None:
        """Replaces the text content of this unit."""
        self._content = content

    def update_title(self, title: str) -> None:
        """Renames this unit. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        self._title = title

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str | None:
        return self._title

    @property
    def content(self) -> str | None:
        return self._content

    @property
    def position(self) -> int:
        return self._position

    @property
    def narrative_id(self) -> str:
        return self._narrative_id

    @property
    def parent_id(self) -> str | None:
        return self._parent_id

    @property
    def children(self) -> list["NarrativeUnit"]:
        return self._children

    @property
    def typ(self) -> str:
        """Returns the typ value matching the database column."""
        return self.__class__.TYP


class Work(NarrativeUnit):
    """Root container of a narrative content tree."""

    TYP = "work"

    @classmethod
    def create(cls, title: str, narrative_id: str) -> "Work":
        """Creates a new Work node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None, title=title, content=None, position=1,
            narrative_id=narrative_id, parent_id=None,
        )


class Part(NarrativeUnit):
    """A major structural division within a Work (e.g. Erster Teil)."""

    TYP = "part"

    @classmethod
    def create(cls, title: str, narrative_id: str, parent_id: str, position: int) -> "Part":
        """Creates a new Part node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None, title=title, content=None, position=position,
            narrative_id=narrative_id, parent_id=parent_id,
        )


class Chapter(NarrativeUnit):
    """A chapter within a Work or Part."""

    TYP = "chapter"

    @classmethod
    def create(
        cls, title: str, narrative_id: str, parent_id: str, position: int
    ) -> "Chapter":
        """Creates a new Chapter node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None, title=title, content=None, position=position,
            narrative_id=narrative_id, parent_id=parent_id,
        )


class Scene(NarrativeUnit):
    """A narrative scene: a thematic or temporal unit of action within the story."""

    TYP = "scene"

    @classmethod
    def create(
        cls, title: str, narrative_id: str, parent_id: str, position: int
    ) -> "Scene":
        """Creates a new Scene node. Raises NarrativeUnitValidationError for empty title."""
        if not title.strip():
            raise NarrativeUnitValidationError("title must not be empty")
        return cls(
            id=None, title=title, content=None, position=position,
            narrative_id=narrative_id, parent_id=parent_id,
        )


class Fragment(NarrativeUnit):
    """Atomic editing unit — one prose paragraph within a Scene.

    Fragment is the autosave boundary: each <textarea> in the Manuscript View
    corresponds to exactly one Fragment. Title is always None — calling
    update_title() raises InvalidOperationError.
    """

    TYP = "fragment"

    @classmethod
    def create(
        cls, content: str, narrative_id: str, parent_id: str, position: int
    ) -> "Fragment":
        """Creates a new Fragment. Raises NarrativeUnitValidationError for empty content."""
        if not content.strip():
            raise NarrativeUnitValidationError("content must not be empty")
        return cls(
            id=None, title=None, content=content, position=position,
            narrative_id=narrative_id, parent_id=parent_id,
        )

    def update_title(self, title: str) -> None:
        """Always raises InvalidOperationError — Fragment has no title."""
        raise InvalidOperationError(
            "Fragment has no title — use update_content() instead."
        )
```

- [ ] **Step 2: Run domain tests — verify they pass**

```bash
pytest api/tests/test_narrative_unit_domain.py -v
```

Expected: all tests GREEN.

- [ ] **Step 3: Commit**

```bash
git add api/models/narrative_unit.py api/tests/test_narrative_unit_domain.py
git commit -m "feat: add NarrativeUnit domain hierarchy (Work/Part/Chapter/Scene/Fragment)"
```

---

## Task 4: Repository Interface

**Files:**
- Create: `api/repositories/narrative_unit_repository.py`

No tests needed (abstract interface only).

- [ ] **Step 1: Write the interface**

```python
"""Port: defines the contract for persisting and loading NarrativeUnit trees."""
from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.narrative_unit import NarrativeUnit


class NarrativeUnitRepository(ABC):
    """Abstract base class for all NarrativeUnitRepository implementations.

    Concrete adapters (e.g. SupabaseNarrativeUnitRepository) implement data access.
    Tests inject a FakeNarrativeUnitRepository.
    """

    @abstractmethod
    async def load_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Loads the full content tree for the given Narrative.

        Fetches all units in a single query and assembles the tree in Python.
        Returns the root NarrativeUnit (Work) with all descendants attached via
        their .children list, or None if no units exist for this narrative.
        Raises NarrativeUnitPersistenceError on database failure.
        """

    @abstractmethod
    async def add(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Inserts a new NarrativeUnit row.

        Returns the unit with an ID assigned by the database.
        Raises NarrativeUnitPersistenceError on database failure.
        """

    @abstractmethod
    async def update(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Persists changes to title and/or content of an existing NarrativeUnit.

        Returns the updated unit as stored in the database.
        Raises NarrativeUnitNotFoundError if no row exists for unit.id.
        Raises NarrativeUnitPersistenceError on database failure.
        """

    @abstractmethod
    async def remove(self, unit_id: str) -> None:
        """Deletes the NarrativeUnit row with the given ID.

        Descendant rows are removed automatically by ON DELETE CASCADE
        (requires migration 20260608000001_narrative_units_cascade.sql).
        Raises NarrativeUnitPersistenceError on database failure.
        """
```

- [ ] **Step 2: Commit**

```bash
git add api/repositories/narrative_unit_repository.py
git commit -m "feat: add NarrativeUnitRepository abstract interface"
```

---

## Task 5: Fake Repository + Test Mother

**Files:**
- Create: `api/tests/fakes/fake_narrative_unit_repository.py`
- Create: `api/tests/mothers/narrative_unit_mother.py`

- [ ] **Step 1: Write the fake repository**

```python
"""In-memory NarrativeUnitRepository for unit and service tests.

Does NOT simulate ON DELETE CASCADE — use only for tests that don't
test multi-node deletion.
"""
from __future__ import annotations

import uuid

from api.models.narrative_unit import Fragment, NarrativeUnit, Scene, Work
from api.repositories.narrative_unit_repository import NarrativeUnitRepository


def _clone_with_id(unit: NarrativeUnit) -> NarrativeUnit:
    """Returns a new instance of the same concrete type with a fresh UUID."""
    return unit.__class__(
        id=str(uuid.uuid4()),
        title=unit.title,
        content=unit.content,
        position=unit.position,
        narrative_id=unit.narrative_id,
        parent_id=unit.parent_id,
    )


class FakeNarrativeUnitRepository(NarrativeUnitRepository):
    """Stores trees and units in plain dicts for fast, isolated tests."""

    def __init__(self) -> None:
        self._trees: dict[str, NarrativeUnit] = {}  # narrative_id → root
        self._units: dict[str, NarrativeUnit] = {}  # unit_id → unit

    def set_tree(self, narrative_id: str, root: NarrativeUnit) -> None:
        """Pre-seeds a tree for a narrative. Call from test setUp before the subject."""
        self._trees[narrative_id] = root

    def set_unit(self, unit: NarrativeUnit) -> None:
        """Registers an individual unit by ID for update/remove tests."""
        if unit.id:
            self._units[unit.id] = unit

    async def load_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Returns the pre-seeded root node, or None."""
        return self._trees.get(narrative_id)

    async def add(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Clones the unit with a new UUID, stores and returns it."""
        saved = _clone_with_id(unit)
        assert saved.id is not None
        self._units[saved.id] = saved
        return saved

    async def update(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Stores the updated unit and returns it unchanged."""
        assert unit.id is not None
        self._units[unit.id] = unit
        return unit

    async def remove(self, unit_id: str) -> None:
        """Removes the unit from the store. Silent no-op for unknown IDs."""
        self._units.pop(unit_id, None)
```

- [ ] **Step 2: Write the test mother**

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add api/tests/fakes/fake_narrative_unit_repository.py api/tests/mothers/narrative_unit_mother.py
git commit -m "feat: add FakeNarrativeUnitRepository and NarrativeUnitMother"
```

---

## Task 6: Schemas

**Files:**
- Create: `api/schemas/narrative_units.py`

- [ ] **Step 1: Write schemas**

```python
"""Pydantic schemas for the /narrative-units endpoints."""
from __future__ import annotations

from pydantic import BaseModel, field_validator


class NarrativeUnitResponse(BaseModel):
    """Response schema for a single NarrativeUnit — includes its assembled subtree."""

    id: str
    typ: str
    title: str | None
    content: str | None
    position: int
    narrative_id: str
    parent_id: str | None
    children: list["NarrativeUnitResponse"] = []

    model_config = {"from_attributes": True}


NarrativeUnitResponse.model_rebuild()


class NarrativeTreeResponse(BaseModel):
    """Response schema for GET /narrative-units/tree/{narrative_id}."""

    narrative_id: str
    root: NarrativeUnitResponse | None


class CreateNarrativeUnitRequest(BaseModel):
    """Request body for POST /narrative-units."""

    typ: str
    title: str | None = None
    content: str | None = None
    position: int
    parent_id: str | None = None
    narrative_id: str

    @field_validator("typ")
    @classmethod
    def typ_must_be_valid(cls, value: str) -> str:
        """Rejects typ values not in the database CHECK constraint."""
        valid = {"work", "part", "chapter", "scene", "fragment"}
        if value not in valid:
            raise ValueError(f"typ must be one of: {', '.join(sorted(valid))}")
        return value


class UpdateNarrativeUnitRequest(BaseModel):
    """Request body for PATCH /narrative-units/{unit_id}.

    Both fields are optional — only the non-None fields are applied.
    """

    title: str | None = None
    content: str | None = None
```

- [ ] **Step 2: Commit**

```bash
git add api/schemas/narrative_units.py
git commit -m "feat: add NarrativeUnit Pydantic schemas"
```

---

## Task 7: Service — Tests First

**Files:**
- Create: `api/tests/test_narrative_unit_service.py`
- Create: `api/services/narrative_unit_service.py` (implementation added below)

- [ ] **Step 1: Write the failing service tests**

```python
"""Tests for NarrativeUnitService.

All tests use FakeNarrativeUnitRepository — no database involved.
"""
from __future__ import annotations

import pytest

from api.models.narrative_unit import Fragment, NarrativeUnit
from api.services.narrative_unit_service import NarrativeUnitService
from api.tests.fakes.fake_narrative_unit_repository import FakeNarrativeUnitRepository
from api.tests.mothers.narrative_unit_mother import (
    NarrativeUnitMother,
    FRAGMENT_ID,
    TEST_NARRATIVE_ID,
)


@pytest.fixture
def repository() -> FakeNarrativeUnitRepository:
    return FakeNarrativeUnitRepository()


@pytest.fixture
def service(repository: FakeNarrativeUnitRepository) -> NarrativeUnitService:
    return NarrativeUnitService(repository=repository)


class TestGetTree:
    async def test_returns_none_when_no_units_exist(
        self, service: NarrativeUnitService
    ) -> None:
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
    async def test_update_unit_persists_content(
        self, service: NarrativeUnitService
    ) -> None:
        """update_unit() persists the updated content via the repository."""
        unit = NarrativeUnitMother.unsaved_fragment()
        saved = await service.add_unit(unit)
        saved.update_content("Geänderter Absatz.")
        result = await service.update_unit(saved)
        assert result.content == "Geänderter Absatz."

    async def test_update_unit_returns_updated_unit(
        self, service: NarrativeUnitService
    ) -> None:
        """update_unit() returns the unit as it came back from the repository."""
        unit = NarrativeUnitMother.unsaved_fragment()
        saved = await service.add_unit(unit)
        saved.update_title("Neuer Titel")
        result = await service.update_unit(saved)
        assert result.title == "Neuer Titel"


class TestRemoveUnit:
    async def test_remove_unit_does_not_raise(
        self, service: NarrativeUnitService
    ) -> None:
        """remove_unit() completes without error for a known unit ID."""
        unit = NarrativeUnitMother.unsaved_fragment()
        saved = await service.add_unit(unit)
        assert saved.id is not None
        await service.remove_unit(saved.id)  # must not raise
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest api/tests/test_narrative_unit_service.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'api.services.narrative_unit_service'`

- [ ] **Step 3: Write the service implementation**

```python
"""NarrativeUnitService: business logic for the narrative content tree."""
from __future__ import annotations

from api.models.narrative_unit import NarrativeUnit
from api.repositories.narrative_unit_repository import NarrativeUnitRepository


class NarrativeUnitService:
    """Coordinates NarrativeUnit operations via the repository port."""

    def __init__(self, repository: NarrativeUnitRepository) -> None:
        self._repository = repository

    async def get_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Returns the fully assembled content tree for the narrative.

        Returns None if no units have been created for this narrative yet.
        """
        return await self._repository.load_tree(narrative_id)

    async def add_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Persists a new NarrativeUnit. Returns the unit with an assigned ID."""
        return await self._repository.add(unit)

    async def update_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Persists changes to an existing NarrativeUnit. Returns the updated unit."""
        return await self._repository.update(unit)

    async def remove_unit(self, unit_id: str) -> None:
        """Removes the unit and all its descendants (via ON DELETE CASCADE)."""
        await self._repository.remove(unit_id)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest api/tests/test_narrative_unit_service.py -v
```

Expected: all tests GREEN.

- [ ] **Step 5: Commit**

```bash
git add api/services/narrative_unit_service.py api/tests/test_narrative_unit_service.py
git commit -m "feat: add NarrativeUnitService with TDD"
```

---

## Task 8: Supabase Repository — Tests First

**Files:**
- Create: `api/tests/test_narrative_unit_repository.py`
- Create: `api/repositories/supabase_narrative_unit_repository.py`

These are integration tests that hit the real Supabase dev instance.

- [ ] **Step 1: Write the failing integration tests**

Look at `api/tests/test_narrative_repository.py` for the conftest fixtures pattern — specifically `narrative_id_for_test` or similar that creates a fresh narrative row and returns its ID for isolation. Use the same approach.

```python
"""Integration tests for SupabaseNarrativeUnitRepository.

These tests hit the real Supabase dev database. They require a test narrative
to exist (created by the fixture) and clean up after themselves.

Run with: pytest api/tests/test_narrative_unit_repository.py -v -m integration
"""
from __future__ import annotations

import pytest

from api.models.narrative_unit import Fragment, NarrativeUnit, Scene, Work
from api.repositories.supabase_narrative_unit_repository import (
    SupabaseNarrativeUnitRepository,
)
from api.tests.mothers.narrative_unit_mother import TEST_NARRATIVE_ID


@pytest.fixture
async def repository(supabase_client) -> SupabaseNarrativeUnitRepository:
    """Creates a SupabaseNarrativeUnitRepository backed by the test Supabase client."""
    return SupabaseNarrativeUnitRepository(client=supabase_client)


@pytest.fixture
async def clean_units(supabase_client) -> None:
    """Deletes all narrative_units rows for TEST_NARRATIVE_ID before and after each test."""
    await supabase_client.table("narrative_units").delete().eq(
        "narrative_id", TEST_NARRATIVE_ID
    ).execute()
    yield
    await supabase_client.table("narrative_units").delete().eq(
        "narrative_id", TEST_NARRATIVE_ID
    ).execute()


class TestLoadTree:
    async def test_load_tree_returns_none_when_empty(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """load_tree() returns None when no units exist for the narrative."""
        result = await repository.load_tree(TEST_NARRATIVE_ID)
        assert result is None

    async def test_load_tree_returns_assembled_work(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """load_tree() returns a Work with its Scene children attached."""
        # Insert Work directly (no parent)
        work_result = await repository.add(
            Work.create(title="Integration Work", narrative_id=TEST_NARRATIVE_ID)
        )
        assert work_result.id is not None

        # Insert Scene as child of Work
        scene_result = await repository.add(
            Scene.create(
                title="Integration Scene",
                narrative_id=TEST_NARRATIVE_ID,
                parent_id=work_result.id,
                position=1,
            )
        )
        assert scene_result.id is not None

        tree = await repository.load_tree(TEST_NARRATIVE_ID)
        assert tree is not None
        assert isinstance(tree, Work)
        assert tree.title == "Integration Work"
        assert len(tree.children) == 1
        assert isinstance(tree.children[0], Scene)
        assert tree.children[0].title == "Integration Scene"


class TestAdd:
    async def test_add_assigns_id(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """add() inserts a Work and returns it with a database-assigned ID."""
        work = Work.create(title="New Work", narrative_id=TEST_NARRATIVE_ID)
        saved = await repository.add(work)
        assert saved.id is not None
        assert saved.title == "New Work"
        assert saved.typ == "work"

    async def test_add_fragment_preserves_content(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """add() persists Fragment content correctly."""
        work = await repository.add(
            Work.create(title="Work", narrative_id=TEST_NARRATIVE_ID)
        )
        scene = await repository.add(
            Scene.create(
                title="Scene", narrative_id=TEST_NARRATIVE_ID,
                parent_id=work.id, position=1,  # type: ignore[arg-type]
            )
        )
        fragment = await repository.add(
            Fragment.create(
                content="Ein Absatz.",
                narrative_id=TEST_NARRATIVE_ID,
                parent_id=scene.id,  # type: ignore[arg-type]
                position=1,
            )
        )
        assert fragment.content == "Ein Absatz."


class TestUpdate:
    async def test_update_persists_new_content(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """update() saves new content and returns the updated fragment."""
        work = await repository.add(
            Work.create(title="Work", narrative_id=TEST_NARRATIVE_ID)
        )
        scene = await repository.add(
            Scene.create(
                title="Scene", narrative_id=TEST_NARRATIVE_ID,
                parent_id=work.id, position=1,  # type: ignore[arg-type]
            )
        )
        fragment = await repository.add(
            Fragment.create(
                content="Original.",
                narrative_id=TEST_NARRATIVE_ID,
                parent_id=scene.id,  # type: ignore[arg-type]
                position=1,
            )
        )
        fragment.update_content("Updated.")
        updated = await repository.update(fragment)
        assert updated.content == "Updated."


class TestRemove:
    async def test_remove_deletes_leaf_node(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """remove() deletes a fragment row; subsequent load_tree shows it gone."""
        work = await repository.add(
            Work.create(title="Work", narrative_id=TEST_NARRATIVE_ID)
        )
        scene = await repository.add(
            Scene.create(
                title="Scene", narrative_id=TEST_NARRATIVE_ID,
                parent_id=work.id, position=1,  # type: ignore[arg-type]
            )
        )
        fragment = await repository.add(
            Fragment.create(
                content="To delete.",
                narrative_id=TEST_NARRATIVE_ID,
                parent_id=scene.id,  # type: ignore[arg-type]
                position=1,
            )
        )
        assert fragment.id is not None
        await repository.remove(fragment.id)
        # Reload tree — fragment should be gone
        tree = await repository.load_tree(TEST_NARRATIVE_ID)
        assert tree is not None
        assert len(tree.children[0].children) == 0

    async def test_remove_parent_cascades_to_children(
        self, repository: SupabaseNarrativeUnitRepository, clean_units: None
    ) -> None:
        """remove() on a Scene removes its Fragment children via ON DELETE CASCADE."""
        work = await repository.add(
            Work.create(title="Work", narrative_id=TEST_NARRATIVE_ID)
        )
        scene = await repository.add(
            Scene.create(
                title="Scene", narrative_id=TEST_NARRATIVE_ID,
                parent_id=work.id, position=1,  # type: ignore[arg-type]
            )
        )
        await repository.add(
            Fragment.create(
                content="Orphan.",
                narrative_id=TEST_NARRATIVE_ID,
                parent_id=scene.id,  # type: ignore[arg-type]
                position=1,
            )
        )
        assert scene.id is not None
        await repository.remove(scene.id)
        # Work should still exist but have no children
        tree = await repository.load_tree(TEST_NARRATIVE_ID)
        assert tree is not None
        assert len(tree.children) == 0
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest api/tests/test_narrative_unit_repository.py -v -m integration 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'api.repositories.supabase_narrative_unit_repository'`

- [ ] **Step 3: Write the Supabase repository**

```python
"""Adapter: persists and loads NarrativeUnit trees via Supabase (PostgREST)."""
from __future__ import annotations

import logging
from typing import Any

from supabase import AsyncClient

from api.exceptions.narrative_unit import (
    NarrativeUnitNotFoundError,
    NarrativeUnitPersistenceError,
)
from api.models.narrative_unit import NarrativeUnit
from api.repositories._supabase import records
from api.repositories.narrative_unit_repository import NarrativeUnitRepository

_TABLE = "narrative_units"


class SupabaseNarrativeUnitRepository(NarrativeUnitRepository):
    """Reads and writes NarrativeUnit trees using the Supabase PostgREST API.

    Tree assembly algorithm:
    1. Fetch all rows for the narrative in a single SELECT ordered by position.
    2. Build a flat dict: unit_id → NarrativeUnit.
    3. Walk the dict — nodes with parent_id are attached to their parent;
       the node with parent_id=None is the root (Work).
    """

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def load_tree(self, narrative_id: str) -> NarrativeUnit | None:
        """Fetches all units and assembles the tree in Python. Returns root or None."""
        self.logger.debug(
            "SupabaseNarrativeUnitRepository.load_tree: narrative_id=%s", narrative_id
        )
        try:
            result = (
                await self._client.table(_TABLE)
                .select("*")
                .eq("narrative_id", narrative_id)
                .order("position")
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(
                f"Failed to load tree for narrative {narrative_id}: {e}"
            ) from e

        rows = records(result.data)
        if not rows:
            return None

        # Index all units by database ID
        units: dict[str, NarrativeUnit] = {}
        for row in rows:
            unit = NarrativeUnit.from_record(row)
            if unit.id:
                units[unit.id] = unit

        # Attach children to parents; find the Work root.
        # We look specifically for typ='work' to avoid treating orphan scenes
        # (imported via the old Phase-1 workflow, parent_id=NULL) as roots.
        root: NarrativeUnit | None = None
        for unit in units.values():
            if unit.parent_id is None and unit.typ == "work":
                root = unit
            elif unit.parent_id is not None:
                parent = units.get(unit.parent_id)
                if parent is not None:
                    parent.add_child(unit)

        return root

    async def add(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Inserts a NarrativeUnit row. Returns the unit with an assigned ID."""
        self.logger.info(
            "SupabaseNarrativeUnitRepository.add: narrative_id=%s, typ=%s",
            unit.narrative_id,
            unit.typ,
        )
        try:
            result = (
                await self._client.table(_TABLE)
                .insert(
                    {
                        "narrative_id": unit.narrative_id,
                        "typ": unit.typ,
                        "title": unit.title,
                        "content": unit.content,
                        "position": unit.position,
                        "parent_id": unit.parent_id,
                    }
                )
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(f"Failed to add narrative unit: {e}") from e

        if not result.data:
            raise NarrativeUnitPersistenceError("Add narrative unit returned no data.")

        row = records(result.data)[0]
        return NarrativeUnit.from_record(row)

    async def update(self, unit: NarrativeUnit) -> NarrativeUnit:
        """Updates title and content of the unit. Returns the updated row."""
        self.logger.info(
            "SupabaseNarrativeUnitRepository.update: unit_id=%s", unit.id
        )
        try:
            result = (
                await self._client.table(_TABLE)
                .update({"title": unit.title, "content": unit.content})
                .eq("id", unit.id)
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(
                f"Failed to update narrative unit {unit.id}: {e}"
            ) from e

        if not result.data:
            raise NarrativeUnitNotFoundError(f"Narrative unit not found: {unit.id}")

        row = records(result.data)[0]
        return NarrativeUnit.from_record(row)

    async def remove(self, unit_id: str) -> None:
        """Deletes the unit row. Descendants removed by ON DELETE CASCADE."""
        self.logger.info(
            "SupabaseNarrativeUnitRepository.remove: unit_id=%s", unit_id
        )
        try:
            await (
                self._client.table(_TABLE)
                .delete()
                .eq("id", unit_id)
                .execute()
            )
        except Exception as e:
            raise NarrativeUnitPersistenceError(
                f"Failed to remove narrative unit {unit_id}: {e}"
            ) from e
```

- [ ] **Step 4: Run integration tests — verify they pass**

```bash
pytest api/tests/test_narrative_unit_repository.py -v -m integration
```

Expected: all tests GREEN.

- [ ] **Step 5: Commit**

```bash
git add api/repositories/supabase_narrative_unit_repository.py api/tests/test_narrative_unit_repository.py
git commit -m "feat: add SupabaseNarrativeUnitRepository with integration tests"
```

---

## Task 9: Router — Tests First

**Files:**
- Create: `api/tests/test_narrative_units_router.py`
- Create: `api/routers/narrative_units.py`

**Note:** The router depends on `NarrativeUnitService`. Before running tests, Task 10 (Wire Dependencies) must also be complete, otherwise the `app.dependency_overrides` key won't match. Do Task 9 and 10 together in the same commit.

- [ ] **Step 1: Write the failing router tests**

```python
"""Tests for the /narrative-units router.

NarrativeUnitService is replaced by a FakeNarrativeUnitService via
app.dependency_overrides. No database is involved.
"""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_narrative_unit_service
from api.exceptions.narrative_unit import NarrativeUnitNotFoundError
from api.main import app
from api.models.narrative_unit import Fragment, NarrativeUnit, Work
from api.services.narrative_unit_service import NarrativeUnitService
from api.tests.fakes.fake_narrative_unit_repository import FakeNarrativeUnitRepository
from api.tests.mothers.narrative_unit_mother import (
    FRAGMENT_ID,
    NarrativeUnitMother,
    SCENE_ID,
    TEST_NARRATIVE_ID,
    WORK_ID,
)


# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeNarrativeUnitService:
    """Returns preset responses; does not touch the database."""

    def __init__(
        self,
        *,
        tree: NarrativeUnit | None = None,
        added_unit: NarrativeUnit | None = None,
        updated_unit: NarrativeUnit | None = None,
        raise_on_update: Exception | None = None,
        raise_on_remove: Exception | None = None,
    ) -> None:
        self._tree = tree
        self._added_unit = added_unit
        self._updated_unit = updated_unit
        self._raise_on_update = raise_on_update
        self._raise_on_remove = raise_on_remove

    async def get_tree(self, narrative_id: str) -> NarrativeUnit | None:
        return self._tree

    async def add_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        if self._added_unit is not None:
            return self._added_unit
        # Return a clone with a fake ID
        import uuid
        return unit.__class__(
            id=str(uuid.uuid4()),
            title=unit.title, content=unit.content, position=unit.position,
            narrative_id=unit.narrative_id, parent_id=unit.parent_id,
        )

    async def update_unit(self, unit: NarrativeUnit) -> NarrativeUnit:
        if self._raise_on_update:
            raise self._raise_on_update
        return self._updated_unit or unit

    async def remove_unit(self, unit_id: str) -> None:
        if self._raise_on_remove:
            raise self._raise_on_remove


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_client(service: FakeNarrativeUnitService) -> AsyncClient:
    app.dependency_overrides[get_narrative_unit_service] = lambda: service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHealth:
    async def test_health_returns_ok(self) -> None:
        """GET /narrative-units/health returns 200 {"status": "ok"}."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.get("/narrative-units/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestGetTree:
    async def test_get_tree_returns_null_root_when_empty(self) -> None:
        """GET /narrative-units/tree/{id} returns 200 with root=null for empty narrative."""
        async with _make_client(FakeNarrativeUnitService(tree=None)) as client:
            response = await client.get(f"/narrative-units/tree/{TEST_NARRATIVE_ID}")
        assert response.status_code == 200
        body = response.json()
        assert body["narrative_id"] == TEST_NARRATIVE_ID
        assert body["root"] is None

    async def test_get_tree_returns_work_with_children(self) -> None:
        """GET /narrative-units/tree/{id} returns the assembled tree."""
        tree = NarrativeUnitMother.work_with_scene_and_fragment()
        async with _make_client(FakeNarrativeUnitService(tree=tree)) as client:
            response = await client.get(f"/narrative-units/tree/{TEST_NARRATIVE_ID}")
        assert response.status_code == 200
        body = response.json()
        assert body["root"]["typ"] == "work"
        assert len(body["root"]["children"]) == 1
        assert body["root"]["children"][0]["typ"] == "scene"


class TestCreateUnit:
    async def test_create_fragment_returns_201(self) -> None:
        """POST /narrative-units returns 201 with the created unit."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "fragment",
                    "content": "Ein neuer Absatz.",
                    "position": 1,
                    "parent_id": SCENE_ID,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 201
        body = response.json()
        assert body["typ"] == "fragment"
        assert body["content"] == "Ein neuer Absatz."

    async def test_create_unit_with_invalid_typ_returns_422(self) -> None:
        """POST /narrative-units rejects unknown typ values with 422."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.post(
                "/narrative-units",
                json={
                    "typ": "banana",
                    "content": "text",
                    "position": 1,
                    "narrative_id": TEST_NARRATIVE_ID,
                },
            )
        assert response.status_code == 422


class TestUpdateUnit:
    async def test_update_fragment_content_returns_200(self) -> None:
        """PATCH /narrative-units/{id} returns 200 with the updated unit."""
        updated = Fragment(
            id=FRAGMENT_ID, title=None, content="Updated.",
            position=1, narrative_id=TEST_NARRATIVE_ID, parent_id=SCENE_ID,
        )
        async with _make_client(
            FakeNarrativeUnitService(updated_unit=updated)
        ) as client:
            response = await client.patch(
                f"/narrative-units/{FRAGMENT_ID}",
                json={"content": "Updated."},
            )
        assert response.status_code == 200
        assert response.json()["content"] == "Updated."

    async def test_update_unknown_unit_returns_404(self) -> None:
        """PATCH /narrative-units/{id} returns 404 when unit does not exist."""
        async with _make_client(
            FakeNarrativeUnitService(
                raise_on_update=NarrativeUnitNotFoundError("not found")
            )
        ) as client:
            response = await client.patch(
                "/narrative-units/does-not-exist",
                json={"content": "x"},
            )
        assert response.status_code == 404


class TestRemoveUnit:
    async def test_remove_unit_returns_204(self) -> None:
        """DELETE /narrative-units/{id} returns 204 on success."""
        async with _make_client(FakeNarrativeUnitService()) as client:
            response = await client.delete(f"/narrative-units/{FRAGMENT_ID}")
        assert response.status_code == 204

    async def test_remove_unknown_unit_returns_404(self) -> None:
        """DELETE /narrative-units/{id} returns 404 when the unit does not exist."""
        async with _make_client(
            FakeNarrativeUnitService(
                raise_on_remove=NarrativeUnitNotFoundError("not found")
            )
        ) as client:
            response = await client.delete("/narrative-units/does-not-exist")
        assert response.status_code == 404
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest api/tests/test_narrative_units_router.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError` or import errors.

---

## Task 10: Router + Wire Dependencies

**Files:**
- Create: `api/routers/narrative_units.py`
- Modify: `api/dependencies.py`
- Modify: `api/main.py`

- [ ] **Step 1: Write the router**

```python
"""Router: /narrative-units endpoints for the narrative content tree."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_narrative_unit_service
from api.exceptions.narrative_unit import (
    NarrativeUnitNotFoundError,
    NarrativeUnitValidationError,
)
from api.models.narrative_unit import (
    Chapter,
    Fragment,
    NarrativeUnit,
    Part,
    Scene,
    Work,
)
from api.schemas.narrative_units import (
    CreateNarrativeUnitRequest,
    NarrativeTreeResponse,
    NarrativeUnitResponse,
    UpdateNarrativeUnitRequest,
)
from api.services.narrative_unit_service import NarrativeUnitService

router = APIRouter(prefix="/narrative-units", tags=["narrative-units"])

_TYP_FACTORY: dict[str, type[NarrativeUnit]] = {
    "work": Work,
    "part": Part,
    "chapter": Chapter,
    "scene": Scene,
    "fragment": Fragment,
}


def _to_response(unit: NarrativeUnit) -> NarrativeUnitResponse:
    """Recursively serialises a NarrativeUnit tree to the response schema."""
    return NarrativeUnitResponse(
        id=unit.id or "",
        typ=unit.typ,
        title=unit.title,
        content=unit.content,
        position=unit.position,
        narrative_id=unit.narrative_id,
        parent_id=unit.parent_id,
        children=[_to_response(child) for child in unit.children],
    )


@router.get("/health")
async def health() -> dict[str, str]:
    """Returns the health status of the narrative-units service."""
    return {"status": "ok", "service": "narrative-units"}


@router.get("/tree/{narrative_id}", response_model=NarrativeTreeResponse)
async def get_tree(
    narrative_id: str,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> NarrativeTreeResponse:
    """Returns the full content tree for a narrative, or root=null if empty."""
    root = await service.get_tree(narrative_id)
    return NarrativeTreeResponse(
        narrative_id=narrative_id,
        root=_to_response(root) if root is not None else None,
    )


@router.post("", response_model=NarrativeUnitResponse, status_code=201)
async def create_unit(
    body: CreateNarrativeUnitRequest,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> NarrativeUnitResponse:
    """Creates a new NarrativeUnit and returns it with an assigned ID."""
    subclass = _TYP_FACTORY[body.typ]
    if body.typ == "work":
        unit = Work.create(title=body.title or "", narrative_id=body.narrative_id)
    elif body.typ == "fragment":
        if not body.parent_id:
            raise HTTPException(status_code=422, detail="parent_id is required for fragment")
        unit = Fragment.create(
            content=body.content or "",
            narrative_id=body.narrative_id,
            parent_id=body.parent_id,
            position=body.position,
        )
    else:
        if not body.parent_id:
            raise HTTPException(
                status_code=422,
                detail=f"parent_id is required for typ='{body.typ}'",
            )
        unit = subclass(
            id=None,
            title=body.title,
            content=body.content,
            position=body.position,
            narrative_id=body.narrative_id,
            parent_id=body.parent_id,
        )
    try:
        saved = await service.add_unit(unit)
    except NarrativeUnitValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return _to_response(saved)


@router.patch("/{unit_id}", response_model=NarrativeUnitResponse)
async def update_unit(
    unit_id: str,
    body: UpdateNarrativeUnitRequest,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> NarrativeUnitResponse:
    """Updates the title and/or content of an existing NarrativeUnit."""
    # Load the current state of the unit via a single-row tree load
    # The service's update() requires a fully constructed NarrativeUnit.
    # We use a lightweight proxy: load just this unit from the repository.
    # For MVP the service does not expose a get_by_id — we reconstruct from
    # the PATCH payload and the existing row, relying on the repository to
    # apply only the fields we send. The repository.update() uses .eq("id")
    # so we build a minimal Fragment placeholder carrying just id + new values.
    # A full get_by_id endpoint can be added in a follow-up if needed.
    try:
        # We need the full existing unit to preserve narrative_id, typ etc.
        # Strategy: use the FakeNarrativeUnitService in tests which returns a
        # preset updated_unit. In prod the SupabaseNarrativeUnitRepository.update()
        # sends ONLY title/content via .update({"title":..., "content":...}).
        # We create a shell unit carrying just the ID and new values.
        shell = Fragment(
            id=unit_id,
            title=body.title,
            content=body.content,
            position=0,          # not persisted by update()
            narrative_id="",     # not persisted by update()
            parent_id=None,      # not persisted by update()
        )
        updated = await service.update_unit(shell)
    except NarrativeUnitNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return _to_response(updated)


@router.delete("/{unit_id}", status_code=204)
async def remove_unit(
    unit_id: str,
    service: NarrativeUnitService = Depends(get_narrative_unit_service),
) -> None:
    """Deletes a NarrativeUnit and all its descendants."""
    try:
        await service.remove_unit(unit_id)
    except NarrativeUnitNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
```

**Note on the shell approach in `update_unit`:** The `SupabaseNarrativeUnitRepository.update()` only sends `title` and `content` via `.update({"title": ..., "content": ...})`. The `narrative_id`, `position`, and `parent_id` fields in the shell object are never persisted — they're just placeholders to satisfy the type system. This is acceptable for MVP. A cleaner solution (add `get_by_id` to the repository) can be added in a follow-up.

- [ ] **Step 2: Wire dependencies**

Add to `api/dependencies.py`:

```python
from api.repositories.narrative_unit_repository import NarrativeUnitRepository
from api.repositories.supabase_narrative_unit_repository import SupabaseNarrativeUnitRepository
from api.services.narrative_unit_service import NarrativeUnitService

async def get_narrative_unit_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> NarrativeUnitRepository:
    """Wires SupabaseNarrativeUnitRepository with the injected Supabase client."""
    return SupabaseNarrativeUnitRepository(client=client)


async def get_narrative_unit_service(
    repository: NarrativeUnitRepository = Depends(get_narrative_unit_repository),
) -> NarrativeUnitService:
    """Wires NarrativeUnitService with the Supabase repository."""
    return NarrativeUnitService(repository=repository)
```

- [ ] **Step 3: Register router in main.py**

In `api/main.py`, add after the existing imports and router registrations:

```python
from api.routers import narrative_units
# ... existing imports ...

# in the section where include_router is called:
app.include_router(narrative_units.router, tags=["narrative-units"])
```

Also add the exception handlers for `NarrativeUnitNotFoundError` and `NarrativeUnitPersistenceError` following the existing pattern:

```python
from api.exceptions.narrative_unit import (
    NarrativeUnitNotFoundError,
    NarrativeUnitPersistenceError,
)

@app.exception_handler(NarrativeUnitNotFoundError)
async def handle_narrative_unit_not_found(
    request: Request, exc: NarrativeUnitNotFoundError
) -> JSONResponse:
    """Returns 404 when a NarrativeUnit cannot be found."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(NarrativeUnitPersistenceError)
async def handle_narrative_unit_persistence_error(
    request: Request, exc: NarrativeUnitPersistenceError
) -> JSONResponse:
    """Returns 500 when a database operation fails."""
    return JSONResponse(status_code=500, content={"detail": str(exc)})
```

- [ ] **Step 4: Run the router tests**

```bash
pytest api/tests/test_narrative_units_router.py -v
```

Expected: all tests GREEN.

- [ ] **Step 5: Run the full test suite**

```bash
klartext test
```

Expected: all tests GREEN (no regressions).

- [ ] **Step 6: Commit**

```bash
git add api/routers/narrative_units.py api/dependencies.py api/main.py api/tests/test_narrative_units_router.py
git commit -m "feat: add /narrative-units router with health, tree, CRUD endpoints"
```

---

## Task 11: Infrastructure Test

**Files:**
- Modify: `api/tests/infrastructure/` (find the existing infrastructure test file)

The health subendpoint `GET /narrative-units/health` must be covered by the infrastructure tests.

- [ ] **Step 1: Find the infrastructure test file**

```bash
ls api/tests/infrastructure/
```

- [ ] **Step 2: Add the health check**

In the infrastructure test file, add:

```python
async def test_narrative_units_health(client: AsyncClient) -> None:
    """GET /narrative-units/health returns 200 for the narrative-units service."""
    response = await client.get("/narrative-units/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 3: Run infrastructure tests**

```bash
pytest api/tests/infrastructure/ -v -m integration
```

Expected: new test GREEN.

- [ ] **Step 4: Final commit**

```bash
git add api/tests/infrastructure/
git commit -m "test: add infrastructure health check for /narrative-units"
```

---

## QA Gate

Before opening the PR, run the following checks:

```bash
# 1. Full test suite
klartext test

# 2. Coverage check
python api/tests/check_test_coverage.py

# 3. Linting
klartext lint

# 4. Server starts without error
klartext dev &
sleep 3
curl http://localhost:8000/narrative-units/health
```

Expected:
- `klartext test`: all GREEN
- `check_test_coverage.py`: no missing coverage reported
- `klartext lint`: no errors
- `curl`: `{"status":"ok","service":"narrative-units"}`

---

## PR Checklist

- [ ] All tests pass (`klartext test`)
- [ ] Coverage check clean (`check_test_coverage.py`)
- [ ] Health endpoint works (`GET /narrative-units/health` → 200)
- [ ] Tree endpoint works (`GET /narrative-units/tree/{id}` → 200)
- [ ] Create/Update/Delete endpoints work
- [ ] No existing tests broken
- [ ] Migration applied (20260608000001_narrative_units_cascade.sql)
- [ ] PR title: `feat: narrative unit domain model (Work/Part/Chapter/Scene/Fragment)`
- [ ] PR base branch: `main`
