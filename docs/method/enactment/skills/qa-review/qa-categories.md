# QA Check Categories

The QA sub-agent works through these five categories for every diff.

---

## Category 1: Test Completeness

For every new class or method in `models/`, `services/`, `repositories/`, `routers/`:

- Does a corresponding test file exist (`tests/test_<name>.py`)?
- Does every public method have at least one test?
- Are all four layers present?
  - Domain test (no mocks, no external systems)
  - Service test (with FakeRepository, no Supabase)
  - Repository test (`@pytest.mark.integration`, real database)
  - Router test (via `TestClient` or `AsyncClient`)

**Checklist per new class:**
- [ ] `test_<classname>_domain.py` or entry in `test_<module>.py` — Domain
- [ ] `test_<name>_service.py` — Service with FakeRepository
- [ ] `test_<name>_repository.py` with `@pytest.mark.integration` — Repository
- [ ] `test_<name>_router.py` with health test — Router

---

## Category 2: Edge and Error Cases

For every service and domain method, check:

- **Not Found:** if a method can fail to find a resource, is `XNotFoundError` raised and tested?
- **Invalid input:** are invalid inputs (empty string, None, malformed ID) tested at the router (422) and domain (DomainError)?
- **Empty collections:** does the code handle an empty list as input? Is it tested?
- **Duplicate detection:** if uniqueness is enforced, is the duplicate error path tested?
- **Error propagation:** is the error path tested alongside the happy path, not just listed?

**Red flags — these cases are almost always missing:**
- No test for the `XNotFoundError` case
- Router tests only test 200, never 404 or 422
- Service tests only test success, never the failure branches

---

## Category 3: Infrastructure Tests

- Every new router must have a `GET /<resource>/health` endpoint returning `{"status": "ok"}`.
- Every new router test file must have a test for this endpoint.
- Every new `SupabaseXRepository` method that uses the database client must have an
  `@pytest.mark.integration` test in `tests/test_<name>_repository.py`.
- Query methods with JOINs, PostgREST embedded counts (`table(count)`), or
  multi-table lookups **must** have integration tests — fake repositories cannot
  verify these queries work.

**Pattern for router health test (copy exactly):**
```python
@pytest.mark.asyncio
async def test_<resource>_health_returns_200() -> None:
    """Expects GET /<resource>/health to return HTTP 200 with status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/<resource>/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

---

## Category 4: Fake Contract Completeness

- Every `Fake*` class must implement the full interface (all abstract methods).
- Methods must not return silent placeholder values as their only statement:
  - `return 0` — hides that count is never tested
  - `return []` — hides that the caller never verifies list contents
  - `return None` — hides that None handling is untested
  - `return False` — hides boolean logic gaps
- For computed fields (counts derived from related objects), provide a test helper:
  ```python
  def set_claim_count(self, narrative_id: str, count: int) -> None:
      """Sets the claim count for a narrative. Used in tests."""
      self._claim_counts[narrative_id] = count
  ```
- Methods the fake cannot meaningfully implement must raise `NotImplementedError`
  explicitly — never silently return a default.

**Error-behaviour parity (not just return values):** A fake must raise the *same
exceptions on the same conditions* as the real repository — silent-divergence is not
limited to placeholder return values. Open the real `SupabaseXRepository` method and
check every `raise` it contains:

- Real repo raises `XNotFoundError` when the row is missing (e.g. `update()`/`remove()`
  on an unknown ID, empty PostgREST result) → the fake **must** raise it too on the
  missing-key path. A fake that mutates/returns leniently where the real repo raises
  lets tests pass against a path production rejects.
- Mismatch check: for each mutating method (`update`, `remove`, `save`-on-conflict),
  does the fake have a `raise` mirroring the real repo's `if not result.data: raise ...`?
- Asymmetry within one repo is a red flag: if `remove()` is strict but `update()` is
  lenient (or vice versa) in the **fake**, while the real repo treats both the same,
  the fake is wrong.

**Note:** `return []` inside an `if not items:` branch is fine — it's conditional,
not a silent default. Only flag standalone methods whose entire body is a silent return.

---

## Category 5: Domain Composition Tests

**Triggered when any of these appear in the diff:**
- `models/causal_model*.py`
- `models/slot*.py`
- `models/causal_relation*.py`
- `models/scope*.py`
- Any method on `CausalModel`, `Slot`, `CausalRelation`, or `CausalModelScope`

**What to check:**
- Are there tests that assemble multiple domain objects and verify their interaction?
  - Example: create a CausalModel, add Slots and Relations, then verify scope resolution
- Is scope behavior tested under different object combinations?
  - Empty model, single node, chain, fork, merge
- Are composition edge cases covered?
  - Empty model → resolve() returns `[]` not `None`
  - Component in multiple containers simultaneously (CausalMixin)
  - Circular reference guard (if applicable)
  - Scope boundary conditions (node at edge of scope, node outside scope)

**Important:** Composition tests live at the domain level — no Supabase, no FakeRepository.
They test `CausalModel`, `Slot`, and `CausalModelScope` directly.
