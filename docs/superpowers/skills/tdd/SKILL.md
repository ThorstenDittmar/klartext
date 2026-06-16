---
name: tdd
description: Use when implementing any feature or bugfix. Loads the superpowers TDD skill and applies project-specific testing standards.
---

# Test-Driven Development

## Step 1: Load superpowers TDD skill

Before proceeding, invoke the `superpowers:test-driven-development` skill. All rules defined there apply without exception.

## Step 2: Apply project-specific standards

The following standards extend the superpowers TDD skill for this project. They do not replace it.

### Test levels

Always test from inside out — in this order:

1. **Domain objects** — pure unit tests, no mocks, no external systems
2. **Services** — unit tests with fake repositories (in-memory implementations, no Supabase)
3. **Repositories** — integration tests against real test database
4. **Router** — API tests via FastAPI `TestClient`

### Fake repositories instead of mocks

Use real in-memory implementations instead of mocks. Fake repositories are classes, not mock objects.

```python
class FakeUserRepository:
    def __init__(self):
        self._users: dict[str, User] = {}

    def save(self, user: User) -> User:
        """Saves a user to the in-memory store."""
        self._users[user.id] = user
        return user

    def find_by_email(self, email: str) -> User | None:
        """Returns the user with the given email, or None if not found."""
        return next((u for u in self._users.values() if u.email == email), None)
```

### Test naming

Test method names read as specifications — describe what happens under which condition:

```python
def test_create_user_rejects_duplicate_email(): ...
def test_change_email_raises_error_for_invalid_format(): ...
```

### Test comments

Every test method gets a docstring describing the expectation:

```python
def test_create_user_rejects_duplicate_email():
    """Expects an EmailAlreadyExistsError when a user with the same email already exists."""
    ...
```

### Integration tests for Supabase repositories

Every new `SupabaseXRepository` method must have an integration test in the corresponding `test_x_repository.py` file. Unit tests with `FakeXRepository` are **not sufficient** — they don't verify that SQL queries and Supabase client calls work correctly.

**Rule:** Write the integration test in the **same commit** as the Supabase implementation. Do not defer it. Manual smoke-testing is not a substitute.

Pattern (copy from existing tests in the codebase):

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_supabase_x_repository_method_name() -> None:
    """Calls the real database. Expects <description>.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to be set.
    """
    import os
    from supabase import acreate_client
    from api.repositories.supabase_x_repository import SupabaseXRepository

    client = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    repo = SupabaseXRepository(client=client)

    saved = await repo.save(XMother.some())
    try:
        found = await repo.find_by_id(saved.id)
        assert found.field == expected
    finally:
        # Delete in reverse FK order — always, even if assertions fail
        await client.table("child_table").delete().eq("parent_id", saved.id).execute()
        await client.table("parent_table").delete().eq("id", saved.id).execute()
```

Run integration tests with:
```bash
source api/.venv/bin/activate && python -m pytest api/tests/ -m "integration" -v
```

### Infrastructure tests

Infrastructure tests are a separate category — they verify that external systems are reachable:
- Is the database reachable?
- Is Supabase Storage available?
- Are external services responding?

Run separately from unit and integration tests — not part of the normal test run.

### Health check endpoint

Every service gets a `/health` endpoint that returns infrastructure status. Used for monitoring and deployments. Public, no auth required.

### Bug fixes

Never fix a bug without first writing a failing test that reproduces it. Follow the full TDD cycle from there.

## Step 3: QA Review

Before marking work complete, invoke the `qa-review` skill.

The QA agent reviews the diff with fresh eyes — no context from this session.

**For bug fixes specifically:** after the fix is green, also invoke `qa-retro` if the
bug should have been caught during the original implementation.

This step is not optional. "All tests green" is necessary but not sufficient.
The qa-review step verifies that the right tests exist, not just that the existing
tests pass.

## For React/TypeScript components

For React/TypeScript component work, additionally apply the `frontend-testing` skill.
It defines QA-defined completeness criteria that extend the testing standards above.
