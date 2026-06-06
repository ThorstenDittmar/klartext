# User Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a minimal `User` domain object so that "list narratives" becomes a question to the User who owns them, not a free-floating query.

**Architecture:** A single `User` (Thorsten) is seeded in a new `users` table. Narratives gain a `user_id` FK. `UserService.get_default()` returns this user. The `GET /narratives` endpoint and narrative creation/import endpoints use the default user. This is the foundation for future authentication — no auth logic in this plan.

**Tech Stack:** FastAPI · Supabase PostgREST · Python 3.12 · pytest-asyncio

---

## File Map

**New files:**
- `supabase/migrations/20260605000001_add_users.sql` — DB schema + seed
- `api/models/user.py` — User domain object
- `api/exceptions/user.py` — UserValidationError, UserNotFoundError
- `api/repositories/user_repository.py` — abstract UserRepository port
- `api/repositories/supabase_user_repository.py` — Supabase adapter
- `api/services/user_service.py` — UserService with get_default()
- `api/tests/fakes/fake_user_repository.py` — in-memory fake, pre-seeded with Thorsten
- `api/tests/test_user_domain.py` — domain unit tests
- `api/tests/test_user_service.py` — service unit tests
- `api/tests/test_user_repository.py` — integration test

**Modified files:**
- `api/models/narrative.py` — add `user_id: str | None` + `assign_user()` method
- `api/repositories/narrative_repository.py` — add abstract `list_for_user(user_id)`
- `api/repositories/supabase_narrative_repository.py` — implement `list_for_user()`, fix `causal_model_id` bug in save, update `list_all()` to delegate
- `api/tests/fakes/fake_narrative_repository.py` — add `list_for_user()`
- `api/services/narrative_service.py` — add `list_for_user()`, update `create()` + `import_from_file()` to accept `user_id`
- `api/dependencies.py` — add `get_user_repository` + `get_user_service`
- `api/routers/narratives.py` — update `list_narratives`, `create_narrative`, `import_narrative`
- `api/tests/test_narratives_router.py` — update `FakeNarrativeService` + add `UserService` override

**Fixed bug (bundled in this plan):**
`SupabaseNarrativeRepository.list_all()` currently selects only `id, title` — `causal_model_id` is always `None` in list responses. Fixed in `list_for_user()` which replaces it.

---

## Task 1: DB Migration — users table + narrative.user_id

**Files:**
- Create: `supabase/migrations/20260605000001_add_users.sql`

- [ ] **Step 1: Write the migration file**

```sql
-- supabase/migrations/20260605000001_add_users.sql

-- Create users table.
-- Users own Narratives. At this stage only a name is stored;
-- authentication and profiles are out of scope.
CREATE TABLE users (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed the single default user with a fixed, well-known UUID.
-- This UUID is referenced in code as DEFAULT_USER_ID.
INSERT INTO users (id, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'Thorsten');

-- Add user ownership to narratives (step 1: nullable for migration safety).
ALTER TABLE narrative ADD COLUMN user_id UUID REFERENCES users(id);

-- Assign all existing narratives to the default user.
UPDATE narrative SET user_id = '00000000-0000-0000-0000-000000000001';

-- Enforce that every narrative has an owner.
ALTER TABLE narrative ALTER COLUMN user_id SET NOT NULL;
```

- [ ] **Step 2: Apply the migration**

```bash
cd /Users/thormar/klartext && supabase migration up --local
```

Expected: `Applying migration 20260605000001_add_users.sql...` — no errors.

- [ ] **Step 3: Verify**

```bash
cd /Users/thormar/klartext && supabase db diff --local 2>/dev/null | head -40
```

Expected: diff is clean (no unapplied changes).

- [ ] **Step 4: Commit**

```bash
git add supabase/migrations/20260605000001_add_users.sql
git commit -m "feat: add users table and seed default user Thorsten"
```

---

## Task 2: User Domain Object + Exceptions

**Files:**
- Create: `api/exceptions/user.py`
- Create: `api/models/user.py`
- Create: `api/tests/test_user_domain.py`

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_user_domain.py
"""Unit tests for the User domain object."""

from __future__ import annotations

import pytest

from api.exceptions.user import UserValidationError
from api.models.user import User


def test_user_create_sets_name() -> None:
    """Expects a User with the given name to be returned."""
    user = User.create(name="Thorsten")
    assert user.name == "Thorsten"


def test_user_create_id_is_none_before_save() -> None:
    """Expects a new User to have no ID before being persisted."""
    user = User.create(name="Thorsten")
    assert user.id is None


def test_user_create_rejects_empty_name() -> None:
    """Expects UserValidationError for an empty name."""
    with pytest.raises(UserValidationError):
        User.create(name="")


def test_user_create_rejects_whitespace_name() -> None:
    """Expects UserValidationError for a whitespace-only name."""
    with pytest.raises(UserValidationError):
        User.create(name="   ")


def test_user_from_record_reconstructs() -> None:
    """Expects User.from_record to reconstruct a User from a database row."""
    user = User.from_record({"id": "abc-123", "name": "Thorsten"})
    assert user.id == "abc-123"
    assert user.name == "Thorsten"
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_user_domain.py -v
```

Expected: `ModuleNotFoundError: No module named 'api.models.user'`

- [ ] **Step 3: Write the exceptions**

```python
# api/exceptions/user.py
"""Exception hierarchy for User-related errors."""


class UserError(Exception):
    """Base class for all User-related errors."""


class UserValidationError(UserError):
    """Raised when a User cannot be constructed with the given values."""


class UserNotFoundError(UserError):
    """Raised when a User cannot be found by the given identifier."""
```

- [ ] **Step 4: Write the domain object**

```python
# api/models/user.py
"""Domain object: a registered author who owns Narratives."""

from __future__ import annotations

from typing import Any

from api.exceptions.user import UserValidationError


class User:
    """An author who owns Narratives.

    At this stage only a name is stored. Authentication and full profiles
    are out of scope — a single default user is seeded and auto-logged-in.

    Invariants enforced at construction time:
    - name must not be empty or whitespace-only
    """

    def __init__(self, id: str | None, name: str) -> None:
        self._id = id
        self._name = name

    @classmethod
    def create(cls, name: str) -> "User":
        """Creates a new User. Raises UserValidationError for empty name."""
        if not name.strip():
            raise UserValidationError("name must not be empty")
        return cls(id=None, name=name)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "User":
        """Reconstructs a User from a database record."""
        return cls(id=record["id"], name=record["name"])

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def name(self) -> str:
        return self._name
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_user_domain.py -v
```

Expected: 5 tests passing.

- [ ] **Step 6: Commit**

```bash
git add api/models/user.py api/exceptions/user.py api/tests/test_user_domain.py
git commit -m "feat: User domain object with create and from_record"
```

---

## Task 3: UserRepository (abstract) + FakeUserRepository

**Files:**
- Create: `api/repositories/user_repository.py`
- Create: `api/tests/fakes/fake_user_repository.py`

- [ ] **Step 1: Write the abstract UserRepository**

```python
# api/repositories/user_repository.py
"""Port: defines the contract for loading Users."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.user import User


class UserRepository(ABC):
    """Abstract base class for all UserRepository implementations."""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID.

        Raises UserNotFoundError if no User exists for that ID.
        """

    @abstractmethod
    async def find_default(self) -> User:
        """Returns the auto-logged-in default user (Thorsten).

        Raises UserNotFoundError if the default user has not been seeded.
        """
```

- [ ] **Step 2: Write the FakeUserRepository**

```python
# api/tests/fakes/fake_user_repository.py
"""FakeUserRepository — in-memory UserRepository for unit tests."""

from __future__ import annotations

import logging

from api.exceptions.user import UserNotFoundError
from api.models.user import User
from api.repositories.user_repository import UserRepository

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


class FakeUserRepository(UserRepository):
    """In-memory UserRepository for unit tests.

    Pre-seeded with the default user Thorsten so tests do not need
    to set up the database.
    """

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._store: dict[str, User] = {
            DEFAULT_USER_ID: User(id=DEFAULT_USER_ID, name="Thorsten")
        }

    async def find_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID. Raises UserNotFoundError if absent."""
        self.logger.debug("FakeUserRepository.find_by_id: user_id=%s", user_id)
        if user_id not in self._store:
            raise UserNotFoundError(f"User not found: {user_id}")
        return self._store[user_id]

    async def find_default(self) -> User:
        """Returns the pre-seeded default user Thorsten."""
        self.logger.debug("FakeUserRepository.find_default")
        return await self.find_by_id(DEFAULT_USER_ID)
```

- [ ] **Step 3: Verify the files are syntactically correct**

```bash
cd /Users/thormar/klartext && python -c "from api.repositories.user_repository import UserRepository; from api.tests.fakes.fake_user_repository import FakeUserRepository; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add api/repositories/user_repository.py api/tests/fakes/fake_user_repository.py
git commit -m "feat: UserRepository port + FakeUserRepository"
```

---

## Task 4: SupabaseUserRepository + Integration Test

**Files:**
- Create: `api/repositories/supabase_user_repository.py`
- Create: `api/tests/test_user_repository.py`

- [ ] **Step 1: Write the integration test**

```python
# api/tests/test_user_repository.py
"""Integration test: SupabaseUserRepository against the local Supabase database.

Requires a running local Supabase instance with migration 20260605000001 applied.
Run with: python -m pytest api/tests/test_user_repository.py -v
"""

from __future__ import annotations

import os

import pytest
from supabase import acreate_client

from api.repositories.supabase_user_repository import (
    DEFAULT_USER_ID,
    SupabaseUserRepository,
)


@pytest.fixture
async def supabase_client():
    """Creates a real Supabase client from environment variables."""
    return await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )


@pytest.mark.asyncio
async def test_find_default_returns_thorsten(supabase_client) -> None:
    """Expects the default user to be found and named Thorsten."""
    repo = SupabaseUserRepository(client=supabase_client)
    user = await repo.find_default()
    assert user.id == DEFAULT_USER_ID
    assert user.name == "Thorsten"


@pytest.mark.asyncio
async def test_find_by_id_returns_user(supabase_client) -> None:
    """Expects find_by_id to return the user when the ID exists."""
    repo = SupabaseUserRepository(client=supabase_client)
    user = await repo.find_by_id(DEFAULT_USER_ID)
    assert user.name == "Thorsten"
```

- [ ] **Step 2: Run the test — verify it fails**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_user_repository.py -v
```

Expected: `ModuleNotFoundError: No module named 'api.repositories.supabase_user_repository'`

- [ ] **Step 3: Write the Supabase adapter**

```python
# api/repositories/supabase_user_repository.py
"""Adapter: loads Users via Supabase PostgREST."""

from __future__ import annotations

import logging

from supabase import AsyncClient

from api.exceptions.user import UserNotFoundError
from api.models.user import User
from api.repositories._supabase import records
from api.repositories.user_repository import UserRepository

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"
_TABLE = "users"


class SupabaseUserRepository(UserRepository):
    """Reads Users from Supabase. Currently read-only — no user creation via API."""

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def find_by_id(self, user_id: str) -> User:
        """Returns the User with the given ID."""
        self.logger.debug("SupabaseUserRepository.find_by_id: user_id=%s", user_id)
        result = (
            await self._client.table(_TABLE)
            .select("*")
            .eq("id", user_id)
            .execute()
        )
        if not result.data:
            raise UserNotFoundError(f"User not found: {user_id}")
        return User.from_record(records(result.data)[0])

    async def find_default(self) -> User:
        """Returns the auto-logged-in default user."""
        self.logger.debug("SupabaseUserRepository.find_default")
        return await self.find_by_id(DEFAULT_USER_ID)
```

- [ ] **Step 4: Run the integration tests — verify they pass**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_user_repository.py -v
```

Expected: 2 tests passing.

- [ ] **Step 5: Commit**

```bash
git add api/repositories/supabase_user_repository.py api/tests/test_user_repository.py
git commit -m "feat: SupabaseUserRepository + integration tests"
```

---

## Task 5: UserService + Tests

**Files:**
- Create: `api/services/user_service.py`
- Create: `api/tests/test_user_service.py`

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/test_user_service.py
"""Unit tests for UserService."""

from __future__ import annotations

import pytest

from api.services.user_service import UserService
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID, FakeUserRepository


def make_service() -> UserService:
    return UserService(repository=FakeUserRepository())


@pytest.mark.asyncio
async def test_get_default_returns_thorsten() -> None:
    """Expects get_default to return the pre-seeded Thorsten user."""
    service = make_service()
    user = await service.get_default()
    assert user.id == DEFAULT_USER_ID
    assert user.name == "Thorsten"
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_user_service.py -v
```

Expected: `ModuleNotFoundError: No module named 'api.services.user_service'`

- [ ] **Step 3: Write UserService**

```python
# api/services/user_service.py
"""Service: provides access to user accounts."""

from __future__ import annotations

from api.models.user import User
from api.repositories.user_repository import UserRepository


class UserService:
    """Provides access to user accounts.

    Currently supports only the single default author (Thorsten).
    Full authentication is out of scope at this stage.
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_default(self) -> User:
        """Returns the auto-logged-in default user.

        Raises UserNotFoundError if the default user has not been seeded.
        """
        return await self._repository.find_default()
```

- [ ] **Step 4: Run test — verify it passes**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_user_service.py -v
```

Expected: 1 test passing.

- [ ] **Step 5: Commit**

```bash
git add api/services/user_service.py api/tests/test_user_service.py
git commit -m "feat: UserService.get_default returns the auto-logged-in user"
```

---

## Task 6: Extend Narrative + NarrativeRepository + Fakes

**Files:**
- Modify: `api/models/narrative.py`
- Modify: `api/repositories/narrative_repository.py`
- Modify: `api/repositories/supabase_narrative_repository.py`
- Modify: `api/tests/fakes/fake_narrative_repository.py`

This task adds `user_id` to the Narrative domain object and `list_for_user()` to the repository.
It also fixes the pre-existing bug where `causal_model_id` was never loaded in list queries.

- [ ] **Step 1: Write a failing test for list_for_user in the narrative service tests**

Add to `api/tests/test_narrative_service.py` (do not remove existing tests):

```python
@pytest.mark.asyncio
async def test_list_for_user_returns_only_own_narratives() -> None:
    """Expects list_for_user to return only narratives owned by the given user."""
    repo = FakeNarrativeRepository()
    service = make_service(repository=repo)

    n1 = await service.create(title="Narrative A", user_id="user-111")
    await service.create(title="Narrative B", user_id="user-222")

    result = await service.list_for_user("user-111")
    assert len(result) == 1
    assert result[0].id == n1.id
```

Note: `make_service()` is already defined in the existing test file as shown above.
`NarrativeService.create()` will accept `user_id` after this task.
`NarrativeService.list_for_user()` will be added in Task 7.

Run to confirm it fails:

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_narrative_service.py::test_list_for_user_returns_only_own_narratives -v
```

Expected: `AttributeError` (method does not exist yet).

- [ ] **Step 2: Update Narrative domain object**

In `api/models/narrative.py`, make the following changes:

1. Update `__init__` signature:
```python
def __init__(
    self,
    id: str | None,
    title: str,
    causal_model_id: str | None = None,
    user_id: str | None = None,
) -> None:
    self._id = id
    self._title = title
    self._causal_model_id = causal_model_id
    self._user_id = user_id
    self._scenes: list[Scene] = []
    self._actors: list[Actor] = []
```

2. Update `from_record` to include `user_id`:
```python
@classmethod
def from_record(cls, record: dict[str, Any]) -> "Narrative":
    """Reconstructs a Narrative from a database record."""
    return cls(
        id=record["id"],
        title=record["title"],
        causal_model_id=record.get("causal_model_id"),
        user_id=record.get("user_id"),
    )
```

3. Add `assign_user` method (after the `link_to_causal_model` method):
```python
def assign_user(self, user_id: str) -> None:
    """Assigns this Narrative to a user.

    Raises NarrativeValidationError for empty or whitespace-only user_id.
    """
    if not user_id.strip():
        raise NarrativeValidationError("user_id must not be empty")
    self._user_id = user_id
```

4. Add `user_id` property (after the `causal_model_id` property):
```python
@property
def user_id(self) -> str | None:
    return self._user_id
```

- [ ] **Step 3: Add `list_for_user` to the abstract NarrativeRepository**

In `api/repositories/narrative_repository.py`, add this abstract method after `list_all`:

```python
@abstractmethod
async def list_for_user(self, user_id: str) -> list[Narrative]:
    """Returns all Narratives belonging to the given user.

    Returns summary data only (id, title, causal_model_id, user_id) —
    no scenes or actors are loaded.
    Returns an empty list when the user has no Narratives.
    Raises NarrativePersistenceError on database failure.
    """
```

- [ ] **Step 4: Implement `list_for_user` in SupabaseNarrativeRepository**

In `api/repositories/supabase_narrative_repository.py`, add this method after `list_all`:

```python
async def list_for_user(self, user_id: str) -> list[Narrative]:
    """Returns all Narrative rows for the given user, with causal_model_id included."""
    self.logger.debug("SupabaseNarrativeRepository.list_for_user: user_id=%s", user_id)
    try:
        result = (
            await self._client.table(_NARRATIVE_TABLE)
            .select("id, title, causal_model_id, user_id")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
    except Exception as e:
        raise NarrativePersistenceError(
            f"Failed to list narratives for user {user_id}: {e}"
        ) from e

    return [
        Narrative.from_record(
            {
                "id": row["id"],
                "title": row["title"],
                "causal_model_id": row.get("causal_model_id"),
                "user_id": row.get("user_id"),
            }
        )
        for row in records(result.data)
    ]
```

Also update `save()` in `SupabaseNarrativeRepository` to include `user_id` in the INSERT.
Find the INSERT in `save()` and update it:

```python
narrative_result = (
    await self._client.table(_NARRATIVE_TABLE)
    .insert({"title": narrative.title, "user_id": narrative.user_id})
    .execute()
)
```

- [ ] **Step 5: Implement `list_for_user` in FakeNarrativeRepository**

In `api/tests/fakes/fake_narrative_repository.py`, add after `list_all`:

```python
async def list_for_user(self, user_id: str) -> list[Narrative]:
    """Returns all saved narratives for the given user as title-only summaries."""
    self.logger.debug("FakeNarrativeRepository.list_for_user: user_id=%s", user_id)
    return [
        Narrative(
            id=n.id,
            title=n.title,
            causal_model_id=n.causal_model_id,
            user_id=n.user_id,
        )
        for n in self._store.values()
        if n.user_id == user_id
    ]
```

Also update `save()` in `FakeNarrativeRepository` to preserve `user_id`:

```python
async def save(self, narrative: Narrative) -> Narrative:
    """Stores the narrative with a generated ID and returns it with IDs assigned."""
    self.logger.info("FakeNarrativeRepository.save: title=%s", narrative.title)
    narrative_id = str(uuid.uuid4())
    saved = Narrative(
        id=narrative_id,
        title=narrative.title,
        causal_model_id=narrative.causal_model_id,
        user_id=narrative.user_id,
    )
    for scene in narrative.scenes:
        saved.add_scene(
            Scene(
                id=str(uuid.uuid4()),
                title=scene.title,
                text=scene.text,
                position=scene.position,
            )
        )
    self._store[narrative_id] = saved
    return saved
```

- [ ] **Step 6: Run the full test suite to verify no regressions**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/ -v --ignore=api/tests/test_user_repository.py -x
```

Expected: all existing tests pass. The new `test_list_for_user_returns_only_own_narratives` test still fails (NarrativeService doesn't have `list_for_user` yet — that's Task 7).

- [ ] **Step 7: Commit**

```bash
git add api/models/narrative.py api/repositories/narrative_repository.py \
        api/repositories/supabase_narrative_repository.py \
        api/tests/fakes/fake_narrative_repository.py \
        api/tests/test_narrative_service.py
git commit -m "feat: Narrative.assign_user + NarrativeRepository.list_for_user"
```

---

## Task 7: Update NarrativeService

**Files:**
- Modify: `api/services/narrative_service.py`

- [ ] **Step 1: Update `create()` to accept user_id**

Replace the existing `create()` method:

```python
async def create(self, title: str, user_id: str | None = None) -> Narrative:
    """Creates and persists a new empty Narrative with the given title.

    If user_id is provided, the Narrative is assigned to that user.
    Returns the saved Narrative with an assigned ID and no scenes.
    Raises NarrativeValidationError if the title is empty.
    Raises NarrativePersistenceError on database failure.
    """
    narrative = Narrative.create(title)
    if user_id is not None:
        narrative.assign_user(user_id)
    return await self._repository.save(narrative)
```

- [ ] **Step 2: Update `import_from_file()` to accept user_id**

Replace the existing `import_from_file()` method:

```python
async def import_from_file(self, path: Path, user_id: str | None = None) -> Narrative:
    """Reads, parses and persists a Narrative from the given file path.

    If user_id is provided, the Narrative is assigned to that user.
    Returns the saved Narrative with IDs assigned to it and all its Scenes.
    Raises NarrativeFileNotFoundError if the file does not exist.
    Raises NarrativeParseError if the file is empty or contains no scenes.
    Raises NarrativePersistenceError on database failure.
    """
    narrative = self._import_service.import_from_file(path)
    if user_id is not None:
        narrative.assign_user(user_id)
    return await self._repository.save(narrative)
```

- [ ] **Step 3: Add `list_for_user()` method**

Add after `list_all()`:

```python
async def list_for_user(self, user_id: str) -> list[Narrative]:
    """Returns all Narratives belonging to the given user.

    Returns summary data only (id, title, causal_model_id) — no scenes or actors.
    """
    return await self._repository.list_for_user(user_id)
```

- [ ] **Step 4: Run the narrative service tests**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_narrative_service.py -v
```

Expected: all tests pass including `test_list_for_user_returns_only_own_narratives`.

- [ ] **Step 5: Commit**

```bash
git add api/services/narrative_service.py
git commit -m "feat: NarrativeService.list_for_user + user_id on create and import"
```

---

## Task 8: Wire Dependencies + Update Router + Update Router Tests

**Files:**
- Modify: `api/dependencies.py`
- Modify: `api/routers/narratives.py`
- Modify: `api/tests/test_narratives_router.py`

- [ ] **Step 1: Write failing router tests for the list endpoint**

In `api/tests/test_narratives_router.py`, find the existing `FakeNarrativeService` class and make these changes:

1. Add `list_for_user` method to `FakeNarrativeService` (keep `list_all` for backward compat):

```python
async def list_for_user(self, user_id: str) -> list[Narrative]:
    return self._saved
```

2. Update `create` signature to accept `user_id`:

```python
async def create(self, title: str, user_id: str | None = None) -> Narrative:
    if self._raise_on_create:
        raise self._raise_on_create
    narrative = Narrative(id=SAVED_NARRATIVE_ID, title=title)
    return narrative
```

3. Update `import_from_file` signature to accept `user_id`:

```python
async def import_from_file(self, path: Path, user_id: str | None = None) -> Narrative:
    if self._raise_on_import:
        raise self._raise_on_import
    return make_saved_narrative()
```

4. Add a `FakeUserService` class near the top of the test file (after the `FakeNarrativeService`):

```python
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID, FakeUserRepository
from api.services.user_service import UserService

class FakeUserService:
    """Returns the default Thorsten user for all calls."""

    async def get_default(self):
        return await FakeUserRepository().find_default()
```

5. Update `override_with` to also override the user service:

```python
from api.dependencies import get_user_service

def override_with(service: FakeNarrativeService) -> None:
    app.dependency_overrides[get_narrative_service] = lambda: service
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()


def clear_overrides() -> None:
    app.dependency_overrides.clear()
```

6. Find the existing test for `GET /narratives` (probably named `test_list_narratives_*`) and verify it still passes — the response shape does not change.

- [ ] **Step 2: Wire UserService into dependencies.py**

Add to `api/dependencies.py` (after the narrative repository section):

```python
from api.repositories.supabase_user_repository import SupabaseUserRepository
from api.repositories.user_repository import UserRepository
from api.services.user_service import UserService

async def get_user_repository(
    client: AsyncClient = Depends(get_supabase_client),
) -> UserRepository:
    """Wires SupabaseUserRepository with the injected Supabase client."""
    return SupabaseUserRepository(client=client)


async def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Wires UserRepository into UserService."""
    return UserService(repository=repository)
```

Also update the DI chain comment at the top of `dependencies.py`:

```python
"""Dependency wiring for FastAPI.
...
DI chain:
  get_supabase_client ─┬─► get_narrative_repository ─► get_narrative_service
                       ├─► get_claim_repository ────────► get_claim_service
                       ├─► get_health_checker
                       ├─► get_causal_model_repository ─► get_causal_model_service
                       └─► get_user_repository ──────────► get_user_service
  get_narrative_import_service ────────────────────────► get_narrative_service
  get_consistency_checker ─────────────────────────────► get_causal_model_service
  (standalone) ────────────────────────────────────────► get_claim_extractor_service
"""
```

- [ ] **Step 3: Update narratives router**

In `api/routers/narratives.py`, add the import at the top:

```python
from api.dependencies import (
    ...
    get_user_service,
)
from api.services.user_service import UserService
```

Update `list_narratives`:

```python
@router.get("", response_model=list[NarrativeSummaryResponse])
async def list_narratives(
    user_service: UserService = Depends(get_user_service),
    service: NarrativeService = Depends(get_narrative_service),
) -> list[NarrativeSummaryResponse]:
    """Returns all Narratives belonging to the current (default) user."""
    user = await user_service.get_default()
    narratives = await service.list_for_user(user.id)
    return [
        NarrativeSummaryResponse(id=n.id, title=n.title, causal_model_id=n.causal_model_id)  # type: ignore[arg-type]
        for n in narratives
    ]
```

Update `create_narrative`:

```python
@router.post("", status_code=status.HTTP_201_CREATED, response_model=NarrativeResponse)
async def create_narrative(
    request: CreateNarrativeRequest,
    user_service: UserService = Depends(get_user_service),
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeResponse:
    """Creates a new empty Narrative with the given title for the current user."""
    user = await user_service.get_default()
    narrative = await service.create(title=request.title, user_id=user.id)
    return _to_narrative_response(narrative)
```

Update `import_narrative`:

```python
@router.post(
    "/import",
    response_model=NarrativeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_narrative(
    request: ImportNarrativeRequest,
    user_service: UserService = Depends(get_user_service),
    service: NarrativeService = Depends(get_narrative_service),
) -> NarrativeResponse:
    """Imports a Narrative from the given file path for the current user."""
    user = await user_service.get_default()
    narrative = await service.import_from_file(Path(request.path), user_id=user.id)
    return _to_narrative_response(narrative)
```

- [ ] **Step 4: Run the router tests**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_narratives_router.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Run the full test suite**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/ -v --ignore=api/tests/test_user_repository.py -x
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add api/dependencies.py api/routers/narratives.py api/tests/test_narratives_router.py
git commit -m "feat: narratives list/create/import are now user-scoped via UserService"
```

---

## Task 9: Regression Run

- [ ] **Step 1: Run all unit and integration tests**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/ -v
```

Expected: all tests pass including the `test_user_repository.py` integration tests.

- [ ] **Step 2: Run klartext health**

```bash
cd /Users/thormar/klartext && klartext health
```

Expected: all checks green.

- [ ] **Step 3: Verify causal_model_id bug is fixed**

Start the server and run:

```bash
curl -s http://localhost:8000/narratives | python -m json.tool
```

Expected: narratives in the list now show their actual `causal_model_id` value (not always `null`).

- [ ] **Step 4: Final commit (if any stray files)**

```bash
git status
# Only commit if there are stray changes. Otherwise skip.
```

---

## Summary of Changes

| Layer | What changed |
|---|---|
| DB | New `users` table; Thorsten seeded; `narrative.user_id` FK |
| Domain | `User` class; `Narrative.user_id` + `Narrative.assign_user()` |
| Repository | `UserRepository` port; `SupabaseUserRepository`; `NarrativeRepository.list_for_user()` |
| Service | `UserService.get_default()`; `NarrativeService.list_for_user()` + updated create/import |
| Router | `GET /narratives`, `POST /narratives`, `POST /narratives/import` are now user-scoped |
| Bug fix | `causal_model_id` now correctly populated in narrative list responses |
