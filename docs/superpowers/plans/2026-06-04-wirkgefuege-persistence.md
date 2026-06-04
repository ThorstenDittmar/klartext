# Wirkgefüge Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist Slots and CausalRelations to the database so that the causal model graph can be built and retrieved via the API.

**Architecture:** Slots and CausalRelations are stored in new `slots` and `causal_relations` tables, both belonging to a `causal_models` row. The existing `CausalModelRepository` port is extended with slot and relation methods — no separate repository files. A new `ClaimService` handles claim lifecycle operations (currently: linking a claim to a Wirkgefüge component). All domain objects get explicit `update()` methods per architecture rules.

**Tech Stack:** FastAPI, Pydantic v2, Supabase/PostgREST (Python async client), pytest-asyncio, uv (venv + deps), pre-commit (ruff/mypy/tach)

---

## Architecture Rules (read before touching code)

- **Language:** all code in English; communicate with the user in German
- **TDD:** tests first — run them red before implementing
- **OOP:** business logic in classes; domain changes via explicit methods (`slot.update(...)`)
- **Factory methods:** `create()` for new objects, `from_record()` for DB reconstruction
- **Properties:** `@property` for getters; explicit methods for mutations
- **Repository logging:** first action in every method, before any DB call; `debug` for reads, `info` for writes
- **Type hints:** mandatory everywhere including `-> None`
- **X | None** not `Optional[X]`
- **CRUD completeness:** every persistent domain object gets add + update + remove from the start
- **Health subendpoint:** add `GET /causal-models/health` — it is currently missing
- **Exceptions:** domain → DomainError, service → ServiceError, repository → RepositoryError

## Codebase Context

Run tests with: `source api/.venv/bin/activate && python -m pytest api/tests/ -m "not integration" -v`

The venv is at `api/.venv/`. All test files live under `api/tests/`. Import paths use the `api.*` prefix (e.g. `from api.models.causal_model import Slot`). The `tests.*` prefix is used for test helpers (e.g. `from tests.fakes.fake_causal_model_repository import FakeCausalModelRepository`).

Key files to read before starting:
- `api/models/causal_model.py` — Slot, CausalRelation, EpistemicStatus, SlotType, Polarity
- `api/repositories/causal_model_repository.py` — existing port (abstract base)
- `api/repositories/supabase_causal_model_repository.py` — existing Supabase adapter
- `api/tests/fakes/fake_causal_model_repository.py` — existing in-memory fake
- `api/schemas/causal_models.py` — existing schemas
- `api/routers/causal_models.py` — existing router
- `api/services/causal_model_service.py` — existing service
- `api/repositories/claim_repository.py` — existing ClaimRepository port
- `api/tests/test_causal_model_repository.py` — test patterns to follow

Apply the DB migration via:
```bash
for f in $(ls supabase/migrations/*.sql | sort); do
  docker exec -i supabase_db_klartext psql -U postgres -d postgres < "$f" 2>&1 | tail -3
done
```

---

## File Structure

```
supabase/migrations/
  20260604000001_slots_and_relations.sql   ← NEW: slots + causal_relations tables

api/models/
  causal_model.py                          ← MODIFY: add Slot.update(), CausalRelation.update()

api/exceptions/
  causal_model.py                          ← MODIFY: add SlotNotFoundError, CausalRelationNotFoundError
  claim.py                                 ← MODIFY: add ClaimNotFoundError

api/repositories/
  causal_model_repository.py              ← MODIFY: add slot + relation abstract methods
  supabase_causal_model_repository.py     ← MODIFY: implement slot + relation methods
  claim_repository.py                     ← MODIFY: add find_by_id, update
  supabase_claim_repository.py            ← MODIFY: implement find_by_id, update

api/services/
  causal_model_service.py                 ← MODIFY: add slot + relation service methods
  claim_service.py                        ← NEW: ClaimService.link_to_wirkgefuege()

api/schemas/
  causal_models.py                        ← MODIFY: CreateSlotRequest, UpdateSlotRequest,
                                                     SlotResponse, CreateRelationRequest,
                                                     UpdateRelationRequest, RelationResponse;
                                                     extend CausalModelResponse
  claims.py                               ← MODIFY: add LinkToWirkgefuegeRequest

api/routers/
  causal_models.py                        ← MODIFY: add /health, slot endpoints, relation endpoints
  claims.py                               ← MODIFY: add POST /claims/{id}/link-to-wirkgefuege

api/dependencies.py                       ← MODIFY: wire ClaimService

api/tests/fakes/
  fake_causal_model_repository.py         ← MODIFY: add slot + relation in-memory methods
  fake_claim_repository.py               ← MODIFY: add find_by_id, update

api/tests/
  test_causal_model_repository.py         ← MODIFY: add slot + relation repository tests
  test_causal_model_service.py           ← MODIFY: add slot + relation service tests
  test_causal_model_router.py            ← MODIFY: add slot + relation router tests
  test_claim_service.py                  ← NEW: ClaimService tests
  test_claims_router.py                  ← MODIFY: add link endpoint test
```

---

## Task 1: DB Migration

**Files:**
- Create: `supabase/migrations/20260604000001_slots_and_relations.sql`

- [ ] **Step 1: Write the migration**

```sql
-- Migration 20260604000001 — Slots and CausalRelations tables
--
-- Slots are the named placeholders in a Wirkgefüge (e.g. "Geldmenge", "Inflation").
-- CausalRelations are directed causal links between two Slots.
-- Both belong to exactly one CausalModel via causal_model_id.

ALTER TABLE causal_models ADD COLUMN IF NOT EXISTS identifier TEXT DEFAULT NULL;

CREATE TABLE slots (
    id               UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    causal_model_id  UUID    NOT NULL REFERENCES causal_models(id) ON DELETE CASCADE,
    identifier       TEXT    NOT NULL,
    slot_type        TEXT    NOT NULL
                             CHECK (slot_type IN (
                                 'physical_quantity', 'social_quantity',
                                 'entity_state', 'trend', 'process'
                             )),
    epistemic_status TEXT    NOT NULL DEFAULT 'incomplete'
                             CHECK (epistemic_status IN ('incomplete', 'axiomatic')),
    is_entity        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (causal_model_id, identifier)
);

CREATE TABLE causal_relations (
    id               UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    causal_model_id  UUID    NOT NULL REFERENCES causal_models(id) ON DELETE CASCADE,
    identifier       TEXT    NOT NULL,
    source_slot_id   UUID    NOT NULL REFERENCES slots(id),
    target_slot_id   UUID    NOT NULL REFERENCES slots(id),
    mechanism        TEXT    DEFAULT NULL,
    polarity         TEXT    DEFAULT NULL
                             CHECK (polarity IN ('positive', 'negative', 'ambivalent')),
    epistemic_status TEXT    NOT NULL DEFAULT 'incomplete'
                             CHECK (epistemic_status IN ('incomplete', 'axiomatic')),
    created_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (causal_model_id, identifier)
);

CREATE INDEX slots_causal_model_id_idx ON slots (causal_model_id);
CREATE INDEX causal_relations_causal_model_id_idx ON causal_relations (causal_model_id);
```

- [ ] **Step 2: Apply the migration**

```bash
docker exec -i supabase_db_klartext psql -U postgres -d postgres \
  < supabase/migrations/20260604000001_slots_and_relations.sql
```

Expected: output ending with `CREATE INDEX` — no ERROR lines.

- [ ] **Step 3: Register migration in tracking table**

```bash
docker exec -i supabase_db_klartext psql -U postgres -d postgres -c \
  "INSERT INTO supabase_migrations.schema_migrations (version, name) VALUES ('20260604000001', 'slots_and_relations') ON CONFLICT DO NOTHING;"
```

- [ ] **Step 4: Verify tables exist**

```bash
docker exec supabase_db_klartext psql -U postgres -d postgres -c \
  "SELECT table_name FROM information_schema.tables WHERE table_name IN ('slots','causal_relations') ORDER BY table_name;"
```

Expected:
```
   table_name
-----------------
 causal_relations
 slots
```

- [ ] **Step 5: Commit**

```bash
git add supabase/migrations/20260604000001_slots_and_relations.sql
git commit -m "feat: add slots and causal_relations DB tables"
```

---

## Task 2: Domain update methods + new exceptions

**Files:**
- Modify: `api/models/causal_model.py` (Slot.update, CausalRelation.update)
- Modify: `api/exceptions/causal_model.py`
- Modify: `api/exceptions/claim.py`
- Test: `api/tests/test_slot_domain.py` (already exists — extend it)
- Test: `api/tests/test_causal_relation_domain.py` (already exists — extend it)

- [ ] **Step 1: Write failing tests for Slot.update()**

In `api/tests/test_slot_domain.py`, find a good place to add (after the existing tests):

```python
def test_slot_update_changes_epistemic_status() -> None:
    """Expects update() to change epistemic_status to AXIOMATIC."""
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)

    slot.update(epistemic_status=EpistemicStatus.AXIOMATIC)

    assert slot.epistemic_status == EpistemicStatus.AXIOMATIC


def test_slot_update_keeps_identifier_unchanged() -> None:
    """Expects update() to not change identifier."""
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)

    slot.update(epistemic_status=EpistemicStatus.AXIOMATIC)

    assert slot.identifier == "geldmenge"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source api/.venv/bin/activate && python -m pytest api/tests/test_slot_domain.py::test_slot_update_changes_epistemic_status api/tests/test_slot_domain.py::test_slot_update_keeps_identifier_unchanged -v
```

Expected: FAIL with `AttributeError: 'Slot' object has no attribute 'update'`

- [ ] **Step 3: Add Slot.update() to the domain object**

In `api/models/causal_model.py`, add after the `scope` property of `Slot`:

```python
    def update(self, epistemic_status: EpistemicStatus) -> None:
        """Updates the epistemic_status of this Slot."""
        self._epistemic_status = epistemic_status
```

- [ ] **Step 4: Write failing test for CausalRelation.update()**

In `api/tests/test_causal_relation_domain.py`, add after existing tests:

```python
def test_causal_relation_update_changes_mechanism_and_polarity() -> None:
    """Expects update() to change mechanism and polarity."""
    source = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    target = Slot.create(identifier="inflation", slot_type=SlotType.TREND)
    rel = CausalRelation.create(identifier="geldmenge→inflation", source=source, target=target)

    rel.update(mechanism="Quantitätstheorie", polarity=Polarity.POSITIVE,
               epistemic_status=EpistemicStatus.AXIOMATIC)

    assert rel.mechanism == "Quantitätstheorie"
    assert rel.polarity == Polarity.POSITIVE
    assert rel.epistemic_status == EpistemicStatus.AXIOMATIC


def test_causal_relation_update_can_clear_mechanism() -> None:
    """Expects update() to accept None as mechanism."""
    source = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    target = Slot.create(identifier="inflation", slot_type=SlotType.TREND)
    rel = CausalRelation.create(identifier="geldmenge→inflation", source=source, target=target,
                                mechanism="old")

    rel.update(mechanism=None, polarity=None, epistemic_status=EpistemicStatus.INCOMPLETE)

    assert rel.mechanism is None
```

- [ ] **Step 5: Run CausalRelation tests to verify failure**

```bash
python -m pytest api/tests/test_causal_relation_domain.py::test_causal_relation_update_changes_mechanism_and_polarity api/tests/test_causal_relation_domain.py::test_causal_relation_update_can_clear_mechanism -v
```

Expected: FAIL with `AttributeError: 'CausalRelation' object has no attribute 'update'`

- [ ] **Step 6: Add CausalRelation.update() to the domain object**

In `api/models/causal_model.py`, add after the `is_axiomatic` property of `CausalRelation`:

```python
    def update(
        self,
        mechanism: str | None,
        polarity: Polarity | None,
        epistemic_status: EpistemicStatus,
    ) -> None:
        """Updates mechanism, polarity and epistemic_status of this CausalRelation."""
        self._mechanism = mechanism
        self._polarity = polarity
        self._epistemic_status = epistemic_status
```

- [ ] **Step 7: Add new exceptions**

In `api/exceptions/causal_model.py`, append:

```python
class SlotNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no Slot exists for the given ID."""


class CausalRelationNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no CausalRelation exists for the given ID."""
```

In `api/exceptions/claim.py`, append:

```python
class ClaimNotFoundError(RepositoryError):
    """Raised by ClaimRepository when no Claim exists for the given ID."""
```

- [ ] **Step 8: Run all tests to verify nothing is broken**

```bash
python -m pytest api/tests/ -m "not integration" -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add api/models/causal_model.py api/exceptions/causal_model.py api/exceptions/claim.py \
        api/tests/test_slot_domain.py api/tests/test_causal_relation_domain.py
git commit -m "feat: add Slot.update(), CausalRelation.update() and new not-found exceptions"
```

---

## Task 3: CausalModelRepository — slot methods

**Files:**
- Modify: `api/repositories/causal_model_repository.py`
- Modify: `api/tests/fakes/fake_causal_model_repository.py`
- Modify: `api/tests/test_causal_model_repository.py`

- [ ] **Step 1: Write failing repository tests**

Add to `api/tests/test_causal_model_repository.py` after the existing tests:

```python
# ---------------------------------------------------------------------------
# Slot repository contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_slot_repository_add_slot_assigns_id() -> None:
    """Expects add_slot to return the Slot with a non-None ID."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)

    saved = await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]

    assert saved.id is not None


@pytest.mark.asyncio
async def test_slot_repository_add_slot_makes_it_retrievable() -> None:
    """Expects find_slots_by_model_id to return the added Slot."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]

    found = await repo.find_slots_by_model_id(cm.id)  # type: ignore[arg-type]

    assert len(found) == 1
    assert found[0].identifier == "geldmenge"


@pytest.mark.asyncio
async def test_slot_repository_update_slot_persists_epistemic_status() -> None:
    """Expects update_slot to persist the changed epistemic_status."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    saved = await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]
    saved.update(epistemic_status=EpistemicStatus.AXIOMATIC)

    await repo.update_slot(saved)

    found = await repo.find_slots_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found[0].epistemic_status == EpistemicStatus.AXIOMATIC


@pytest.mark.asyncio
async def test_slot_repository_remove_slot_deletes_it() -> None:
    """Expects remove_slot to make the Slot no longer retrievable."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)
    saved = await repo.add_slot(cm.id, slot)  # type: ignore[arg-type]

    await repo.remove_slot(cm.id, saved.id)  # type: ignore[arg-type]

    found = await repo.find_slots_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found == []


@pytest.mark.asyncio
async def test_slot_repository_add_slot_raises_for_unknown_model() -> None:
    """Expects CausalModelNotFoundError when adding a Slot to a non-existent CausalModel."""
    repo = FakeCausalModelRepository()
    slot = Slot.create(identifier="geldmenge", slot_type=SlotType.PHYSICAL_QUANTITY)

    with pytest.raises(CausalModelNotFoundError):
        await repo.add_slot("00000000-0000-0000-0000-000000000000", slot)
```

Add these imports at the top of `test_causal_model_repository.py`:

```python
from api.models.causal_model import EpistemicStatus, Slot, SlotType
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest api/tests/test_causal_model_repository.py::test_slot_repository_add_slot_assigns_id -v
```

Expected: FAIL with `AttributeError: 'FakeCausalModelRepository' object has no attribute 'add_slot'`

- [ ] **Step 3: Add abstract slot methods to the port**

In `api/repositories/causal_model_repository.py`, add after the existing abstract methods:

```python
from api.models.causal_model import Axiom, CausalModel, CausalRelation, Slot


    @abstractmethod
    async def add_slot(self, causal_model_id: str, slot: Slot) -> Slot:
        """Adds a Slot to the CausalModel and returns it with an ID assigned.

        Raises CausalModelNotFoundError if the CausalModel does not exist.
        """

    @abstractmethod
    async def find_slots_by_model_id(self, causal_model_id: str) -> list[Slot]:
        """Returns all Slots belonging to the given CausalModel."""

    @abstractmethod
    async def update_slot(self, slot: Slot) -> Slot:
        """Persists the current state of an existing Slot. Returns the updated Slot."""

    @abstractmethod
    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Removes a Slot from the CausalModel. Silent no-op for unknown IDs."""
```

- [ ] **Step 4: Implement slot methods in FakeCausalModelRepository**

In `api/tests/fakes/fake_causal_model_repository.py`:

Add import at top: `import logging`
Add import: `from api.models.causal_model import Axiom, CausalModel, CausalRelation, Slot`

Add a `_slots` store and implement the methods:

```python
class FakeCausalModelRepository(CausalModelRepository):
    """In-memory CausalModelRepository for unit tests."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._store: dict[str, CausalModel] = {}
        self._slots: dict[str, list[Slot]] = {}   # causal_model_id → list[Slot]
        self._relations: dict[str, list[CausalRelation]] = {}  # causal_model_id → list[CausalRelation]
```

Add after the existing methods:

```python
    async def add_slot(self, causal_model_id: str, slot: Slot) -> Slot:
        """Adds a Slot to the given CausalModel and returns it with an assigned ID."""
        self.logger.info("FakeCausalModelRepository.add_slot: causal_model_id=%s, identifier=%s",
                         causal_model_id, slot.identifier)
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        saved = Slot(
            id=str(uuid.uuid4()),
            identifier=slot.identifier,
            slot_type=slot.slot_type,
            epistemic_status=slot.epistemic_status,
        )
        self._slots.setdefault(causal_model_id, []).append(saved)
        return saved

    async def find_slots_by_model_id(self, causal_model_id: str) -> list[Slot]:
        """Returns all Slots for the given CausalModel ID."""
        self.logger.debug("FakeCausalModelRepository.find_slots_by_model_id: causal_model_id=%s",
                          causal_model_id)
        return list(self._slots.get(causal_model_id, []))

    async def update_slot(self, slot: Slot) -> Slot:
        """Persists the current state of a Slot (in-memory: already mutated in place)."""
        self.logger.info("FakeCausalModelRepository.update_slot: slot_id=%s", slot.id)
        return slot

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Removes a Slot from the in-memory store."""
        self.logger.info("FakeCausalModelRepository.remove_slot: causal_model_id=%s, slot_id=%s",
                         causal_model_id, slot_id)
        if causal_model_id in self._slots:
            self._slots[causal_model_id] = [
                s for s in self._slots[causal_model_id] if s.id != slot_id
            ]
```

- [ ] **Step 5: Run slot repository tests**

```bash
python -m pytest api/tests/test_causal_model_repository.py -k "slot" -v
```

Expected: all slot tests PASS.

- [ ] **Step 6: Run full test suite**

```bash
python -m pytest api/tests/ -m "not integration" -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add api/repositories/causal_model_repository.py \
        api/tests/fakes/fake_causal_model_repository.py \
        api/tests/test_causal_model_repository.py
git commit -m "feat: add slot repository methods to CausalModelRepository port and fake"
```

---

## Task 4: CausalModelRepository — relation methods

**Files:**
- Modify: `api/repositories/causal_model_repository.py`
- Modify: `api/tests/fakes/fake_causal_model_repository.py`
- Modify: `api/tests/test_causal_model_repository.py`

- [ ] **Step 1: Write failing repository tests for relations**

Add to `api/tests/test_causal_model_repository.py` after the slot tests:

```python
# ---------------------------------------------------------------------------
# CausalRelation repository contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_relation_repository_add_relation_assigns_id() -> None:
    """Expects add_relation to return the CausalRelation with a non-None ID."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("geldmenge", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    relation = CausalRelation.create(
        identifier="geldmenge→inflation", source=source, target=target
    )

    saved = await repo.add_relation(cm.id, relation)  # type: ignore[arg-type]

    assert saved.id is not None


@pytest.mark.asyncio
async def test_relation_repository_add_relation_makes_it_retrievable() -> None:
    """Expects find_relations_by_model_id to return the added CausalRelation."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("geldmenge", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    relation = CausalRelation.create("geldmenge→inflation", source=source, target=target)
    await repo.add_relation(cm.id, relation)  # type: ignore[arg-type]

    found = await repo.find_relations_by_model_id(cm.id)  # type: ignore[arg-type]

    assert len(found) == 1
    assert found[0].identifier == "geldmenge→inflation"


@pytest.mark.asyncio
async def test_relation_repository_update_relation_persists_mechanism() -> None:
    """Expects update_relation to persist mechanism and polarity changes."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("geldmenge", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    saved = await repo.add_relation(cm.id, CausalRelation.create("geldmenge→inflation", source=source, target=target))  # type: ignore[arg-type]
    saved.update(mechanism="Quantitätstheorie", polarity=Polarity.POSITIVE,
                 epistemic_status=EpistemicStatus.AXIOMATIC)

    await repo.update_relation(saved)

    found = await repo.find_relations_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found[0].mechanism == "Quantitätstheorie"


@pytest.mark.asyncio
async def test_relation_repository_remove_relation_deletes_it() -> None:
    """Expects remove_relation to make the CausalRelation no longer retrievable."""
    repo = FakeCausalModelRepository()
    cm = await repo.save(CausalModelMother.empty())
    source = await repo.add_slot(cm.id, Slot.create("geldmenge", SlotType.PHYSICAL_QUANTITY))  # type: ignore[arg-type]
    target = await repo.add_slot(cm.id, Slot.create("inflation", SlotType.TREND))  # type: ignore[arg-type]
    saved = await repo.add_relation(cm.id, CausalRelation.create("geldmenge→inflation", source=source, target=target))  # type: ignore[arg-type]

    await repo.remove_relation(cm.id, saved.id)  # type: ignore[arg-type]

    found = await repo.find_relations_by_model_id(cm.id)  # type: ignore[arg-type]
    assert found == []
```

Add to imports at top of test file: `from api.models.causal_model import CausalRelation, Polarity`

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest api/tests/test_causal_model_repository.py::test_relation_repository_add_relation_assigns_id -v
```

Expected: FAIL with `AttributeError: 'FakeCausalModelRepository' object has no attribute 'add_relation'`

- [ ] **Step 3: Add abstract relation methods to port**

In `api/repositories/causal_model_repository.py`, add after the slot abstract methods:

```python
    @abstractmethod
    async def add_relation(self, causal_model_id: str, relation: CausalRelation) -> CausalRelation:
        """Adds a CausalRelation to the CausalModel and returns it with an ID assigned.

        Raises CausalModelNotFoundError if the CausalModel does not exist.
        """

    @abstractmethod
    async def find_relations_by_model_id(
        self, causal_model_id: str
    ) -> list[CausalRelation]:
        """Returns all CausalRelations belonging to the given CausalModel."""

    @abstractmethod
    async def update_relation(self, relation: CausalRelation) -> CausalRelation:
        """Persists the current state of an existing CausalRelation."""

    @abstractmethod
    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Removes a CausalRelation from the CausalModel. Silent no-op for unknown IDs."""
```

- [ ] **Step 4: Implement relation methods in FakeCausalModelRepository**

Add to `api/tests/fakes/fake_causal_model_repository.py` after the slot methods:

```python
    async def add_relation(
        self, causal_model_id: str, relation: CausalRelation
    ) -> CausalRelation:
        """Adds a CausalRelation and returns it with an assigned ID."""
        self.logger.info(
            "FakeCausalModelRepository.add_relation: causal_model_id=%s, identifier=%s",
            causal_model_id, relation.identifier,
        )
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        saved = CausalRelation(
            id=str(uuid.uuid4()),
            identifier=relation.identifier,
            source=relation.source,
            target=relation.target,
            mechanism=relation.mechanism,
            polarity=relation.polarity,
            epistemic_status=relation.epistemic_status,
        )
        self._relations.setdefault(causal_model_id, []).append(saved)
        return saved

    async def find_relations_by_model_id(self, causal_model_id: str) -> list[CausalRelation]:
        """Returns all CausalRelations for the given CausalModel ID."""
        self.logger.debug(
            "FakeCausalModelRepository.find_relations_by_model_id: causal_model_id=%s",
            causal_model_id,
        )
        return list(self._relations.get(causal_model_id, []))

    async def update_relation(self, relation: CausalRelation) -> CausalRelation:
        """Persists the current state of a CausalRelation (in-memory: already mutated)."""
        self.logger.info(
            "FakeCausalModelRepository.update_relation: relation_id=%s", relation.id
        )
        return relation

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Removes a CausalRelation from the in-memory store."""
        self.logger.info(
            "FakeCausalModelRepository.remove_relation: causal_model_id=%s, relation_id=%s",
            causal_model_id, relation_id,
        )
        if causal_model_id in self._relations:
            self._relations[causal_model_id] = [
                r for r in self._relations[causal_model_id] if r.id != relation_id
            ]
```

- [ ] **Step 5: Run relation repository tests**

```bash
python -m pytest api/tests/test_causal_model_repository.py -k "relation" -v
```

Expected: all relation tests PASS.

- [ ] **Step 6: Run full test suite**

```bash
python -m pytest api/tests/ -m "not integration" -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add api/repositories/causal_model_repository.py \
        api/tests/fakes/fake_causal_model_repository.py \
        api/tests/test_causal_model_repository.py
git commit -m "feat: add relation repository methods to CausalModelRepository port and fake"
```

---

## Task 5: SupabaseCausalModelRepository — slot + relation implementation

**Files:**
- Modify: `api/repositories/supabase_causal_model_repository.py`

- [ ] **Step 1: Implement slot methods in SupabaseCausalModelRepository**

Add `import logging` at top if missing. Add `logger = logging.getLogger(__name__)` as class attribute.

Add these methods to `SupabaseCausalModelRepository`:

```python
    logger = logging.getLogger(__name__)

    async def add_slot(self, causal_model_id: str, slot: Slot) -> Slot:
        """Inserts a Slot into the 'slots' table and returns it with an ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.add_slot: causal_model_id=%s, identifier=%s",
            causal_model_id, slot.identifier,
        )
        try:
            result = (
                await self._client.table("slots")
                .insert({
                    "causal_model_id": causal_model_id,
                    "identifier": slot.identifier,
                    "slot_type": slot.slot_type.value,
                    "epistemic_status": slot.epistemic_status.value,
                    "is_entity": isinstance(slot, Entity),
                })
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save Slot: {exc}") from exc
        row = records(result.data)[0]
        return Slot.from_record(row)

    async def find_slots_by_model_id(self, causal_model_id: str) -> list[Slot]:
        """Returns all Slots for the given CausalModel ID."""
        self.logger.debug(
            "SupabaseCausalModelRepository.find_slots_by_model_id: causal_model_id=%s",
            causal_model_id,
        )
        try:
            result = (
                await self._client.table("slots")
                .select("*")
                .eq("causal_model_id", causal_model_id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load Slots: {exc}") from exc
        return [Slot.from_record(row) for row in records(result.data)]

    async def update_slot(self, slot: Slot) -> Slot:
        """Updates the epistemic_status of an existing Slot."""
        self.logger.info(
            "SupabaseCausalModelRepository.update_slot: slot_id=%s", slot.id
        )
        try:
            result = (
                await self._client.table("slots")
                .update({"epistemic_status": slot.epistemic_status.value})
                .eq("id", slot.id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to update Slot: {exc}") from exc
        return Slot.from_record(records(result.data)[0])

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Deletes a Slot by ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.remove_slot: causal_model_id=%s, slot_id=%s",
            causal_model_id, slot_id,
        )
        try:
            await self._client.table("slots").delete().eq("id", slot_id).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to remove Slot: {exc}") from exc

    async def add_relation(
        self, causal_model_id: str, relation: CausalRelation
    ) -> CausalRelation:
        """Inserts a CausalRelation and returns it with an ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.add_relation: causal_model_id=%s, identifier=%s",
            causal_model_id, relation.identifier,
        )
        try:
            result = (
                await self._client.table("causal_relations")
                .insert({
                    "causal_model_id": causal_model_id,
                    "identifier": relation.identifier,
                    "source_slot_id": relation.source.id,
                    "target_slot_id": relation.target.id,
                    "mechanism": relation.mechanism,
                    "polarity": relation.polarity.value if relation.polarity else None,
                    "epistemic_status": relation.epistemic_status.value,
                })
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to save CausalRelation: {exc}") from exc
        row = records(result.data)[0]
        # Reconstruct with source/target Slot objects passed through
        return CausalRelation(
            id=row["id"],
            identifier=row["identifier"],
            source=relation.source,
            target=relation.target,
            mechanism=row.get("mechanism"),
            polarity=Polarity(row["polarity"]) if row.get("polarity") else None,
            epistemic_status=EpistemicStatus(row.get("epistemic_status", "incomplete")),
        )

    async def find_relations_by_model_id(
        self, causal_model_id: str
    ) -> list[CausalRelation]:
        """Returns CausalRelations for the given CausalModel, with Slots resolved inline.

        Loads all Slots first, then reconstructs each relation from the joined data.
        """
        self.logger.debug(
            "SupabaseCausalModelRepository.find_relations_by_model_id: causal_model_id=%s",
            causal_model_id,
        )
        slots = await self.find_slots_by_model_id(causal_model_id)
        slot_index: dict[str, Slot] = {s.id: s for s in slots if s.id}  # type: ignore[index]
        try:
            result = (
                await self._client.table("causal_relations")
                .select("*")
                .eq("causal_model_id", causal_model_id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to load CausalRelations: {exc}") from exc
        relations = []
        for row in records(result.data):
            source = slot_index.get(row["source_slot_id"])
            target = slot_index.get(row["target_slot_id"])
            if source is None or target is None:
                continue  # orphaned relation — skip
            relations.append(CausalRelation(
                id=row["id"],
                identifier=row["identifier"],
                source=source,
                target=target,
                mechanism=row.get("mechanism"),
                polarity=Polarity(row["polarity"]) if row.get("polarity") else None,
                epistemic_status=EpistemicStatus(row.get("epistemic_status", "incomplete")),
            ))
        return relations

    async def update_relation(self, relation: CausalRelation) -> CausalRelation:
        """Updates mechanism, polarity and epistemic_status of an existing CausalRelation."""
        self.logger.info(
            "SupabaseCausalModelRepository.update_relation: relation_id=%s", relation.id
        )
        try:
            result = (
                await self._client.table("causal_relations")
                .update({
                    "mechanism": relation.mechanism,
                    "polarity": relation.polarity.value if relation.polarity else None,
                    "epistemic_status": relation.epistemic_status.value,
                })
                .eq("id", relation.id)
                .execute()
            )
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to update CausalRelation: {exc}") from exc
        return relation

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Deletes a CausalRelation by ID."""
        self.logger.info(
            "SupabaseCausalModelRepository.remove_relation: causal_model_id=%s, relation_id=%s",
            causal_model_id, relation_id,
        )
        try:
            await self._client.table("causal_relations").delete().eq("id", relation_id).execute()
        except Exception as exc:
            raise CausalModelPersistenceError(f"Failed to remove CausalRelation: {exc}") from exc
```

Add to imports in `supabase_causal_model_repository.py`:

```python
from api.models.causal_model import Axiom, CausalModel, CausalRelation, Entity, EpistemicStatus, Polarity, Slot
```

Also extend `find_by_id` to load slots and relations:

```python
    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Loads the CausalModel with its Axioms, Slots and CausalRelations."""
        # ... existing code for loading cm and axioms stays ...
        # After loading axioms, add:
        for slot in await self.find_slots_by_model_id(causal_model_id):
            cm.add(slot)
        for relation in await self.find_relations_by_model_id(causal_model_id):
            try:
                cm.add(relation)
            except Exception:
                pass  # namespace conflict if already loaded — skip
        return cm
```

Note: The `find_by_id` call to `cm.add(slot)` uses CausalModel's `add()` method which registers the slot in the CausalMixin component list. The returned CausalModel will then have populated `get_slots()` and `get_relations()`.

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest api/tests/ -m "not integration" -q
```

Expected: all tests pass (the Supabase implementation is not tested by unit tests).

- [ ] **Step 3: Commit**

```bash
git add api/repositories/supabase_causal_model_repository.py
git commit -m "feat: implement slot and relation persistence in SupabaseCausalModelRepository"
```

---

## Task 6: Slot + Relation service methods + schemas + router endpoints

**Files:**
- Modify: `api/services/causal_model_service.py`
- Modify: `api/schemas/causal_models.py`
- Modify: `api/routers/causal_models.py`
- Modify: `api/tests/test_causal_model_service.py`
- Modify: `api/tests/test_causal_model_router.py`

- [ ] **Step 1: Write failing service tests**

Add to `api/tests/test_causal_model_service.py`:

```python
from api.models.causal_model import CausalRelation, EpistemicStatus, Polarity, Slot, SlotType
from api.exceptions.causal_model import CausalModelNotFoundError, SlotNotFoundError


# ---------------------------------------------------------------------------
# add_slot
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_add_slot_returns_slot_with_id() -> None:
    """Expects add_slot to return a Slot with a non-None ID."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")

    slot = await service.add_slot(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        identifier="geldmenge",
        slot_type=SlotType.PHYSICAL_QUANTITY,
    )

    assert slot.id is not None
    assert slot.identifier == "geldmenge"


@pytest.mark.asyncio
async def test_service_add_slot_raises_for_unknown_model() -> None:
    """Expects CausalModelNotFoundError when the CausalModel does not exist."""
    service = make_service()

    with pytest.raises(CausalModelNotFoundError):
        await service.add_slot(
            causal_model_id="00000000-0000-0000-0000-000000000000",
            identifier="geldmenge",
            slot_type=SlotType.PHYSICAL_QUANTITY,
        )


# ---------------------------------------------------------------------------
# add_relation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_add_relation_returns_relation_with_id() -> None:
    """Expects add_relation to return a CausalRelation with a non-None ID."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")
    source = await service.add_slot(cm.id, "geldmenge", SlotType.PHYSICAL_QUANTITY)  # type: ignore[arg-type]
    target = await service.add_slot(cm.id, "inflation", SlotType.TREND)  # type: ignore[arg-type]

    relation = await service.add_relation(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        identifier="geldmenge→inflation",
        source_slot_id=source.id,  # type: ignore[arg-type]
        target_slot_id=target.id,  # type: ignore[arg-type]
    )

    assert relation.id is not None
    assert relation.identifier == "geldmenge→inflation"


@pytest.mark.asyncio
async def test_service_add_relation_raises_for_unknown_source_slot() -> None:
    """Expects SlotNotFoundError when source_slot_id does not exist."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")
    target = await service.add_slot(cm.id, "inflation", SlotType.TREND)  # type: ignore[arg-type]

    with pytest.raises(SlotNotFoundError):
        await service.add_relation(
            causal_model_id=cm.id,  # type: ignore[arg-type]
            identifier="unknown→inflation",
            source_slot_id="00000000-0000-0000-0000-000000000000",
            target_slot_id=target.id,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# update_relation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_update_relation_changes_mechanism() -> None:
    """Expects update_relation to persist the new mechanism."""
    service = make_service()
    cm = await service.create(title="Wirkmodell")
    source = await service.add_slot(cm.id, "geldmenge", SlotType.PHYSICAL_QUANTITY)  # type: ignore[arg-type]
    target = await service.add_slot(cm.id, "inflation", SlotType.TREND)  # type: ignore[arg-type]
    rel = await service.add_relation(cm.id, "geldmenge→inflation", source.id, target.id)  # type: ignore[arg-type]

    updated = await service.update_relation(
        causal_model_id=cm.id,  # type: ignore[arg-type]
        relation_id=rel.id,  # type: ignore[arg-type]
        mechanism="Quantitätstheorie",
        polarity=Polarity.POSITIVE,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert updated.mechanism == "Quantitätstheorie"
    assert updated.polarity == Polarity.POSITIVE
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest api/tests/test_causal_model_service.py::test_service_add_slot_returns_slot_with_id -v
```

Expected: FAIL with `AttributeError: 'CausalModelService' object has no attribute 'add_slot'`

- [ ] **Step 3: Add slot + relation methods to CausalModelService**

In `api/services/causal_model_service.py`, add imports and methods:

```python
from api.exceptions.causal_model import (
    CausalModelNotFoundError,
    CausalRelationNotFoundError,
    SlotNotFoundError,
)
from api.models.causal_model import (
    Axiom, CausalModel, CausalRelation, EpistemicStatus, Polarity, Slot, SlotType,
)


    async def add_slot(
        self,
        causal_model_id: str,
        identifier: str,
        slot_type: SlotType,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> Slot:
        """Adds a Slot to the CausalModel. Raises CausalModelNotFoundError if absent."""
        await self._repository.find_by_id(causal_model_id)
        slot = Slot.create(identifier=identifier, slot_type=slot_type,
                           epistemic_status=epistemic_status)
        return await self._repository.add_slot(causal_model_id, slot)

    async def update_slot(
        self,
        causal_model_id: str,
        slot_id: str,
        epistemic_status: EpistemicStatus,
    ) -> Slot:
        """Updates the epistemic_status of a Slot.

        Raises CausalModelNotFoundError or SlotNotFoundError if either is absent.
        """
        await self._repository.find_by_id(causal_model_id)
        slots = await self._repository.find_slots_by_model_id(causal_model_id)
        slot = next((s for s in slots if s.id == slot_id), None)
        if slot is None:
            raise SlotNotFoundError(f"Slot not found: {slot_id}")
        slot.update(epistemic_status=epistemic_status)
        return await self._repository.update_slot(slot)

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        """Removes a Slot from the CausalModel."""
        await self._repository.find_by_id(causal_model_id)
        await self._repository.remove_slot(causal_model_id, slot_id)

    async def add_relation(
        self,
        causal_model_id: str,
        identifier: str,
        source_slot_id: str,
        target_slot_id: str,
        mechanism: str | None = None,
        polarity: Polarity | None = None,
    ) -> CausalRelation:
        """Adds a CausalRelation between two Slots.

        Raises CausalModelNotFoundError or SlotNotFoundError if any ID is absent.
        """
        await self._repository.find_by_id(causal_model_id)
        slots = await self._repository.find_slots_by_model_id(causal_model_id)
        slot_index: dict[str, Slot] = {s.id: s for s in slots if s.id}  # type: ignore[index]
        source = slot_index.get(source_slot_id)
        target = slot_index.get(target_slot_id)
        if source is None:
            raise SlotNotFoundError(f"Source slot not found: {source_slot_id}")
        if target is None:
            raise SlotNotFoundError(f"Target slot not found: {target_slot_id}")
        relation = CausalRelation.create(
            identifier=identifier, source=source, target=target,
            mechanism=mechanism, polarity=polarity,
        )
        return await self._repository.add_relation(causal_model_id, relation)

    async def update_relation(
        self,
        causal_model_id: str,
        relation_id: str,
        mechanism: str | None,
        polarity: Polarity | None,
        epistemic_status: EpistemicStatus,
    ) -> CausalRelation:
        """Updates an existing CausalRelation.

        Raises CausalModelNotFoundError or CausalRelationNotFoundError if absent.
        """
        await self._repository.find_by_id(causal_model_id)
        relations = await self._repository.find_relations_by_model_id(causal_model_id)
        relation = next((r for r in relations if r.id == relation_id), None)
        if relation is None:
            raise CausalRelationNotFoundError(f"CausalRelation not found: {relation_id}")
        relation.update(mechanism=mechanism, polarity=polarity,
                        epistemic_status=epistemic_status)
        return await self._repository.update_relation(relation)

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        """Removes a CausalRelation from the CausalModel."""
        await self._repository.find_by_id(causal_model_id)
        await self._repository.remove_relation(causal_model_id, relation_id)
```

- [ ] **Step 4: Run service tests**

```bash
python -m pytest api/tests/test_causal_model_service.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Add schemas**

In `api/schemas/causal_models.py`, append:

```python
class CreateSlotRequest(BaseModel):
    """Request body for adding a Slot to a CausalModel."""

    identifier: str
    slot_type: str
    epistemic_status: str = "incomplete"

    @field_validator("identifier")
    @classmethod
    def identifier_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("identifier must not be empty")
        return v


class UpdateSlotRequest(BaseModel):
    """Request body for updating a Slot's epistemic_status."""

    epistemic_status: str


class SlotResponse(BaseModel):
    """Response shape for a single Slot."""

    id: str
    identifier: str
    slot_type: str
    epistemic_status: str
    is_entity: bool = False


class CreateRelationRequest(BaseModel):
    """Request body for adding a CausalRelation to a CausalModel."""

    identifier: str
    source_slot_id: str
    target_slot_id: str
    mechanism: str | None = None
    polarity: str | None = None

    @field_validator("identifier")
    @classmethod
    def identifier_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("identifier must not be empty")
        return v


class UpdateRelationRequest(BaseModel):
    """Request body for updating a CausalRelation."""

    mechanism: str | None = None
    polarity: str | None = None
    epistemic_status: str = "incomplete"


class RelationResponse(BaseModel):
    """Response shape for a single CausalRelation."""

    id: str
    identifier: str
    source_slot_id: str
    target_slot_id: str
    mechanism: str | None
    polarity: str | None
    epistemic_status: str
```

Also update `CausalModelResponse` to include slots and relations:

```python
class CausalModelResponse(BaseModel):
    """Response shape for a CausalModel with its full list of Axioms, Slots and Relations."""

    id: str
    title: str
    status: str
    axioms: list[AxiomResponse]
    slots: list[SlotResponse] = []
    relations: list[RelationResponse] = []
```

- [ ] **Step 6: Add router tests**

Add to `api/tests/test_causal_model_router.py` — first extend `FakeCausalModelService`:

```python
# Add to FakeCausalModelService class:

    async def add_slot(
        self, causal_model_id: str, identifier: str, slot_type: SlotType,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> Slot:
        if causal_model_id == "unknown":
            raise CausalModelNotFoundError("not found")
        return Slot(id="slot-001", identifier=identifier, slot_type=SlotType(slot_type.value),
                    epistemic_status=epistemic_status)

    async def update_slot(
        self, causal_model_id: str, slot_id: str, epistemic_status: EpistemicStatus
    ) -> Slot:
        return Slot(id=slot_id, identifier="geldmenge",
                    slot_type=SlotType.PHYSICAL_QUANTITY, epistemic_status=epistemic_status)

    async def remove_slot(self, causal_model_id: str, slot_id: str) -> None:
        pass

    async def add_relation(
        self, causal_model_id: str, identifier: str, source_slot_id: str,
        target_slot_id: str, mechanism: str | None = None, polarity: Polarity | None = None,
    ) -> CausalRelation:
        source = Slot(id=source_slot_id, identifier="src",
                      slot_type=SlotType.PHYSICAL_QUANTITY)
        target = Slot(id=target_slot_id, identifier="tgt",
                      slot_type=SlotType.TREND)
        return CausalRelation(id="rel-001", identifier=identifier,
                              source=source, target=target, mechanism=mechanism, polarity=polarity)

    async def update_relation(
        self, causal_model_id: str, relation_id: str, mechanism: str | None,
        polarity: Polarity | None, epistemic_status: EpistemicStatus,
    ) -> CausalRelation:
        source = Slot(id="slot-src", identifier="src", slot_type=SlotType.PHYSICAL_QUANTITY)
        target = Slot(id="slot-tgt", identifier="tgt", slot_type=SlotType.TREND)
        return CausalRelation(id=relation_id, identifier="geldmenge→inflation",
                              source=source, target=target,
                              mechanism=mechanism, polarity=polarity,
                              epistemic_status=epistemic_status)

    async def remove_relation(self, causal_model_id: str, relation_id: str) -> None:
        pass
```

Then add router tests:

```python
# Add these imports to test_causal_model_router.py:
from api.models.causal_model import CausalRelation, EpistemicStatus, Polarity, Slot, SlotType
from api.exceptions.causal_model import SlotNotFoundError


# ---------------------------------------------------------------------------
# GET /causal-models/health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_models_health_returns_200() -> None:
    """Expects GET /causal-models/health to return HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/causal-models/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# POST /causal-models/{id}/slots
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_slot_returns_201() -> None:
    """Expects POST /causal-models/{id}/slots to return HTTP 201."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/slots",
            json={"identifier": "geldmenge", "slot_type": "physical_quantity"},
        )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_slot_response_contains_id_and_identifier() -> None:
    """Expects the slot response to include id and identifier."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/slots",
            json={"identifier": "geldmenge", "slot_type": "physical_quantity"},
        )
    data = response.json()
    assert data["id"] == "slot-001"
    assert data["identifier"] == "geldmenge"


# ---------------------------------------------------------------------------
# POST /causal-models/{id}/relations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_relation_returns_201() -> None:
    """Expects POST /causal-models/{id}/relations to return HTTP 201."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/causal-models/cm-001/relations",
            json={
                "identifier": "geldmenge→inflation",
                "source_slot_id": "slot-src",
                "target_slot_id": "slot-tgt",
            },
        )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# PUT /causal-models/{id}/relations/{rid}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_relation_returns_200() -> None:
    """Expects PUT /causal-models/{id}/relations/{rid} to return HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/causal-models/cm-001/relations/rel-001",
            json={"mechanism": "Quantitätstheorie", "polarity": "positive"},
        )
    assert response.status_code == 200
    assert response.json()["mechanism"] == "Quantitätstheorie"
```

- [ ] **Step 7: Run router tests to verify failure**

```bash
python -m pytest api/tests/test_causal_model_router.py::test_causal_models_health_returns_200 -v
```

Expected: FAIL (endpoint does not exist yet)

- [ ] **Step 8: Add endpoints to the router**

In `api/routers/causal_models.py`, add imports and endpoints:

```python
from api.schemas.causal_models import (
    AddAxiomRequest, AxiomResponse,
    CausalModelResponse, CausalModelSummaryResponse,
    CheckConsistencyRequest, ConsistencyConflictResponse, ConsistencyResultResponse,
    CreateCausalModelRequest,
    CreateRelationRequest, UpdateRelationRequest, RelationResponse,
    CreateSlotRequest, UpdateSlotRequest, SlotResponse,
)
from api.models.causal_model import EpistemicStatus, Polarity, SlotType
```

Add health endpoint at the TOP of the router (before other endpoints):

```python
@router.get("/health")
async def health() -> dict[str, str]:
    """Returns service health status. Public — no authentication required."""
    return {"status": "ok"}
```

Add slot endpoints:

```python
@router.post(
    "/{causal_model_id}/slots",
    status_code=status.HTTP_201_CREATED,
    response_model=SlotResponse,
)
async def add_slot(
    causal_model_id: str,
    request: CreateSlotRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> SlotResponse:
    """Adds a Slot (named placeholder) to an existing CausalModel."""
    slot = await service.add_slot(
        causal_model_id=causal_model_id,
        identifier=request.identifier,
        slot_type=SlotType(request.slot_type),
        epistemic_status=EpistemicStatus(request.epistemic_status),
    )
    return SlotResponse(
        id=slot.id,  # type: ignore[arg-type]
        identifier=slot.identifier,
        slot_type=slot.slot_type.value,
        epistemic_status=slot.epistemic_status.value,
    )


@router.put("/{causal_model_id}/slots/{slot_id}", response_model=SlotResponse)
async def update_slot(
    causal_model_id: str,
    slot_id: str,
    request: UpdateSlotRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> SlotResponse:
    """Updates the epistemic_status of a Slot."""
    slot = await service.update_slot(
        causal_model_id=causal_model_id,
        slot_id=slot_id,
        epistemic_status=EpistemicStatus(request.epistemic_status),
    )
    return SlotResponse(
        id=slot.id,  # type: ignore[arg-type]
        identifier=slot.identifier,
        slot_type=slot.slot_type.value,
        epistemic_status=slot.epistemic_status.value,
    )


@router.delete("/{causal_model_id}/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_slot(
    causal_model_id: str,
    slot_id: str,
    service: CausalModelService = Depends(get_causal_model_service),
) -> None:
    """Removes a Slot from the CausalModel."""
    await service.remove_slot(causal_model_id=causal_model_id, slot_id=slot_id)
```

Add relation endpoints:

```python
@router.post(
    "/{causal_model_id}/relations",
    status_code=status.HTTP_201_CREATED,
    response_model=RelationResponse,
)
async def add_relation(
    causal_model_id: str,
    request: CreateRelationRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> RelationResponse:
    """Adds a CausalRelation (directed causal link) to an existing CausalModel."""
    relation = await service.add_relation(
        causal_model_id=causal_model_id,
        identifier=request.identifier,
        source_slot_id=request.source_slot_id,
        target_slot_id=request.target_slot_id,
        mechanism=request.mechanism,
        polarity=Polarity(request.polarity) if request.polarity else None,
    )
    return RelationResponse(
        id=relation.id,  # type: ignore[arg-type]
        identifier=relation.identifier,
        source_slot_id=relation.source.id,  # type: ignore[arg-type]
        target_slot_id=relation.target.id,  # type: ignore[arg-type]
        mechanism=relation.mechanism,
        polarity=relation.polarity.value if relation.polarity else None,
        epistemic_status=relation.epistemic_status.value,
    )


@router.put("/{causal_model_id}/relations/{relation_id}", response_model=RelationResponse)
async def update_relation(
    causal_model_id: str,
    relation_id: str,
    request: UpdateRelationRequest,
    service: CausalModelService = Depends(get_causal_model_service),
) -> RelationResponse:
    """Updates mechanism, polarity and epistemic_status of a CausalRelation."""
    relation = await service.update_relation(
        causal_model_id=causal_model_id,
        relation_id=relation_id,
        mechanism=request.mechanism,
        polarity=Polarity(request.polarity) if request.polarity else None,
        epistemic_status=EpistemicStatus(request.epistemic_status),
    )
    return RelationResponse(
        id=relation.id,  # type: ignore[arg-type]
        identifier=relation.identifier,
        source_slot_id=relation.source.id,  # type: ignore[arg-type]
        target_slot_id=relation.target.id,  # type: ignore[arg-type]
        mechanism=relation.mechanism,
        polarity=relation.polarity.value if relation.polarity else None,
        epistemic_status=relation.epistemic_status.value,
    )


@router.delete(
    "/{causal_model_id}/relations/{relation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_relation(
    causal_model_id: str,
    relation_id: str,
    service: CausalModelService = Depends(get_causal_model_service),
) -> None:
    """Removes a CausalRelation from the CausalModel."""
    await service.remove_relation(
        causal_model_id=causal_model_id, relation_id=relation_id
    )
```

Also update the two existing response-building helpers in `get_causal_model` and `create_causal_model` to include slots and relations:

```python
# Helper function to avoid repetition — add near top of routers/causal_models.py:
def _to_response(cm: CausalModel) -> CausalModelResponse:
    """Converts a CausalModel to its full API response shape."""
    from api.models.causal_model import CausalRelation as CR, Slot as S
    return CausalModelResponse(
        id=cm.id,  # type: ignore[arg-type]
        title=cm.title,
        status=cm.status.value,
        axioms=[
            AxiomResponse(id=a.id, label=a.label, description=a.description)  # type: ignore[arg-type]
            for a in cm.axioms
        ],
        slots=[
            SlotResponse(
                id=s.id,  # type: ignore[arg-type]
                identifier=s.identifier,
                slot_type=s.slot_type.value,
                epistemic_status=s.epistemic_status.value,
            )
            for s in cm.get_slots()
        ],
        relations=[
            RelationResponse(
                id=r.id,  # type: ignore[arg-type]
                identifier=r.identifier,
                source_slot_id=r.source.id,  # type: ignore[arg-type]
                target_slot_id=r.target.id,  # type: ignore[arg-type]
                mechanism=r.mechanism,
                polarity=r.polarity.value if r.polarity else None,
                epistemic_status=r.epistemic_status.value,
            )
            for r in cm.get_relations()
            if isinstance(r, CR)
        ],
    )
```

Replace the inline response-building in `create_causal_model` and `get_causal_model` with `return _to_response(cm)`.

- [ ] **Step 9: Run all tests**

```bash
python -m pytest api/tests/ -m "not integration" -q
```

Expected: all tests pass.

- [ ] **Step 10: Commit**

```bash
git add api/services/causal_model_service.py api/schemas/causal_models.py \
        api/routers/causal_models.py \
        api/tests/test_causal_model_service.py api/tests/test_causal_model_router.py
git commit -m "feat: add slot and relation service methods, schemas and router endpoints"
```

---

## Task 7: ClaimRepository extension + ClaimService + link endpoint

**Files:**
- Modify: `api/repositories/claim_repository.py`
- Modify: `api/repositories/supabase_claim_repository.py`
- Modify: `api/tests/fakes/fake_claim_repository.py`
- Create: `api/services/claim_service.py`
- Modify: `api/schemas/claims.py`
- Modify: `api/routers/claims.py`
- Modify: `api/dependencies.py`
- Create: `api/tests/test_claim_service.py`
- Modify: `api/tests/test_claims_router.py`

- [ ] **Step 1: Write failing tests for ClaimRepository extensions**

Add to `api/tests/test_claim_repository.py` after existing tests:

```python
from api.exceptions.claim import ClaimNotFoundError


@pytest.mark.asyncio
async def test_claim_repository_find_by_id_returns_saved_claim() -> None:
    """Expects find_by_id to return the Claim that was saved."""
    repo = FakeClaimRepository()
    [saved] = await repo.save_all([ClaimMother.causal()], scene_id=SCENE_ID)

    found = await repo.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.id == saved.id
    assert found.label == saved.label


@pytest.mark.asyncio
async def test_claim_repository_find_by_id_raises_for_unknown_id() -> None:
    """Expects ClaimNotFoundError when no Claim exists for the given ID."""
    repo = FakeClaimRepository()

    with pytest.raises(ClaimNotFoundError):
        await repo.find_by_id("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_claim_repository_update_persists_status_and_wirkgefuege_ref() -> None:
    """Expects update to persist status and wirkgefuege_ref changes."""
    repo = FakeClaimRepository()
    [saved] = await repo.save_all([ClaimMother.causal()], scene_id=SCENE_ID)
    saved.link_to_wirkgefuege("slot-abc")

    updated = await repo.update(saved)

    refetched = await repo.find_by_id(updated.id)  # type: ignore[arg-type]
    assert refetched.status.value == "linked"
    assert refetched.wirkgefuege_ref == "slot-abc"
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest api/tests/test_claim_repository.py::test_claim_repository_find_by_id_returns_saved_claim -v
```

Expected: FAIL with `AttributeError: 'FakeClaimRepository' object has no attribute 'find_by_id'`

- [ ] **Step 3: Extend ClaimRepository port**

In `api/repositories/claim_repository.py`, add after existing abstract methods:

```python
from api.exceptions.claim import ClaimNotFoundError


    @abstractmethod
    async def find_by_id(self, claim_id: str) -> Claim:
        """Returns the Claim with the given ID.

        Raises ClaimNotFoundError if no Claim exists for that ID.
        """

    @abstractmethod
    async def update(self, claim: Claim) -> Claim:
        """Persists the current state of an existing Claim. Returns the updated Claim."""
```

- [ ] **Step 4: Implement in FakeClaimRepository**

In `api/tests/fakes/fake_claim_repository.py`:

Change `_store` to also index by ID. Add `_index: dict[str, Claim] = {}` for O(1) lookup.

```python
class FakeClaimRepository(ClaimRepository):
    """In-memory ClaimRepository for unit tests."""

    def __init__(self) -> None:
        self._store: dict[str, list[Claim]] = {}   # scene_id → list[Claim]
        self._index: dict[str, Claim] = {}          # claim_id → Claim

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Assigns a new UUID to each claim and stores them under the given scene_id."""
        saved = [
            Claim(
                id=str(uuid.uuid4()),
                label=c.label,
                text=c.text,
                typ=c.typ,
                confidence=c.confidence,
                status=c.status,
                wirkgefuege_ref=c.wirkgefuege_ref,
            )
            for c in claims
        ]
        self._store[scene_id] = saved
        for claim in saved:
            self._index[claim.id] = claim  # type: ignore[index]
        return saved

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns the claims for the given scene, or an empty list if none exist."""
        return self._store.get(scene_id, [])

    async def find_by_id(self, claim_id: str) -> Claim:
        """Returns the Claim with the given ID. Raises ClaimNotFoundError if absent."""
        if claim_id not in self._index:
            raise ClaimNotFoundError(f"Claim not found: {claim_id}")
        return self._index[claim_id]

    async def update(self, claim: Claim) -> Claim:
        """Persists the current state of a Claim (in-memory: already mutated in place)."""
        if claim.id in self._index:
            self._index[claim.id] = claim  # type: ignore[index]
        return claim
```

Add import at top: `from api.exceptions.claim import ClaimNotFoundError`

- [ ] **Step 5: Implement in SupabaseClaimRepository**

In `api/repositories/supabase_claim_repository.py`, add:

```python
from api.exceptions.claim import ClaimNotFoundError, ClaimPersistenceError


    async def find_by_id(self, claim_id: str) -> Claim:
        """Returns the Claim with the given ID. Raises ClaimNotFoundError if absent."""
        self.logger.debug("SupabaseClaimRepository.find_by_id: claim_id=%s", claim_id)
        try:
            result = (
                await self._client.table(_CLAIM_TABLE)
                .select("*")
                .eq("id", claim_id)
                .execute()
            )
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to load claim {claim_id}: {e}") from e
        if not result.data:
            raise ClaimNotFoundError(f"Claim not found: {claim_id}")
        return Claim.from_record(records(result.data)[0])

    async def update(self, claim: Claim) -> Claim:
        """Updates status and wirkgefuege_ref of an existing Claim."""
        self.logger.info("SupabaseClaimRepository.update: claim_id=%s", claim.id)
        try:
            result = (
                await self._client.table(_CLAIM_TABLE)
                .update({
                    "status": claim.status.value,
                    "wirkgefuege_ref": claim.wirkgefuege_ref,
                })
                .eq("id", claim.id)
                .execute()
            )
        except Exception as e:
            raise ClaimPersistenceError(f"Failed to update claim {claim.id}: {e}") from e
        return Claim.from_record(records(result.data)[0])
```

- [ ] **Step 6: Run ClaimRepository tests**

```bash
python -m pytest api/tests/test_claim_repository.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Write failing ClaimService tests**

Create `api/tests/test_claim_service.py`:

```python
"""Tests for ClaimService."""

from __future__ import annotations

import pytest

from api.exceptions.claim import ClaimNotFoundError
from api.models.claim import ClaimStatus
from api.services.claim_service import ClaimService
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.mothers.claim_mother import ClaimMother

SCENE_ID = "scene-001"


def make_service() -> ClaimService:
    """Builds a ClaimService with an in-memory repository."""
    return ClaimService(repository=FakeClaimRepository())


@pytest.mark.asyncio
async def test_link_to_wirkgefuege_sets_status_to_linked() -> None:
    """Expects link_to_wirkgefuege to set the claim status to LINKED."""
    service = make_service()
    repo = FakeClaimRepository()
    [saved] = await repo.save_all([ClaimMother.causal()], scene_id=SCENE_ID)
    service = ClaimService(repository=repo)

    updated = await service.link_to_wirkgefuege(
        claim_id=saved.id,  # type: ignore[arg-type]
        wirkgefuege_ref="slot-abc",
    )

    assert updated.status == ClaimStatus.LINKED
    assert updated.wirkgefuege_ref == "slot-abc"


@pytest.mark.asyncio
async def test_link_to_wirkgefuege_raises_for_unknown_claim() -> None:
    """Expects ClaimNotFoundError when no Claim exists for the given ID."""
    service = make_service()

    with pytest.raises(ClaimNotFoundError):
        await service.link_to_wirkgefuege(
            claim_id="00000000-0000-0000-0000-000000000000",
            wirkgefuege_ref="slot-abc",
        )
```

- [ ] **Step 8: Run to verify failure**

```bash
python -m pytest api/tests/test_claim_service.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'api.services.claim_service'`

- [ ] **Step 9: Create ClaimService**

Create `api/services/claim_service.py`:

```python
"""ClaimService — business logic for Claim lifecycle operations."""

from __future__ import annotations

from api.models.claim import Claim
from api.repositories.claim_repository import ClaimRepository


class ClaimService:
    """Orchestrates Claim persistence and lifecycle changes."""

    def __init__(self, repository: ClaimRepository) -> None:
        self._repository = repository

    async def link_to_wirkgefuege(self, claim_id: str, wirkgefuege_ref: str) -> Claim:
        """Links a Claim to a Wirkgefüge component by reference ID.

        Sets the Claim's status to LINKED and stores the wirkgefuege_ref.
        Raises ClaimNotFoundError if no Claim exists for that ID.
        """
        claim = await self._repository.find_by_id(claim_id)
        claim.link_to_wirkgefuege(wirkgefuege_ref)
        return await self._repository.update(claim)
```

- [ ] **Step 10: Run ClaimService tests**

```bash
python -m pytest api/tests/test_claim_service.py -v
```

Expected: all tests PASS.

- [ ] **Step 11: Add schema and router endpoint**

In `api/schemas/claims.py`, append:

```python
class LinkToWirkgefuegeRequest(BaseModel):
    """Request body for linking a Claim to a Wirkgefüge component."""

    wirkgefuege_ref: str

    @field_validator("wirkgefuege_ref")
    @classmethod
    def ref_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("wirkgefuege_ref must not be empty")
        return v
```

Add import at top of `api/schemas/claims.py`: `from pydantic import BaseModel, field_validator`

In `api/routers/claims.py`, add the endpoint:

```python
from api.dependencies import get_claim_extractor_service, get_claim_service
from api.schemas.claims import (
    ClaimResponse, ExtractClaimsRequest, ExtractClaimsResponse,
    LinkToWirkgefuegeRequest,
)
from api.services.claim_service import ClaimService


@router.post("/claims/{claim_id}/link-to-wirkgefuege", response_model=ClaimResponse)
async def link_claim_to_wirkgefuege(
    claim_id: str,
    request: LinkToWirkgefuegeRequest,
    service: ClaimService = Depends(get_claim_service),
) -> ClaimResponse:
    """Links a Claim to a Wirkgefüge component (Slot or CausalRelation).

    Sets the Claim's status to LINKED and stores the wirkgefuege_ref.
    """
    claim = await service.link_to_wirkgefuege(
        claim_id=claim_id,
        wirkgefuege_ref=request.wirkgefuege_ref,
    )
    return ClaimResponse(
        label=claim.label,
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
        status=claim.status.value,
        wirkgefuege_ref=claim.wirkgefuege_ref,
    )
```

Note: The `claims` router is currently registered without a prefix. The endpoint `/claims/{id}/link-to-wirkgefuege` must be registered on the router without a `/claims` prefix since it's added in `main.py` — check how the router is mounted in `api/main.py` and adjust the route path accordingly. If the router is mounted at `/` add the full `/claims/{claim_id}/link-to-wirkgefuege` path as shown.

- [ ] **Step 12: Wire ClaimService in dependencies.py**

In `api/dependencies.py`, add:

```python
from api.services.claim_service import ClaimService


async def get_claim_service(
    repository: ClaimRepository = Depends(get_claim_repository),
) -> ClaimService:
    """Wires ClaimRepository into ClaimService."""
    return ClaimService(repository=repository)
```

- [ ] **Step 13: Add router test**

In `api/tests/test_claims_router.py`, add:

```python
from api.dependencies import get_claim_service
from api.services.claim_service import ClaimService
from api.models.claim import ClaimStatus


class FakeClaimService:
    """Returns a fixed linked claim for all link requests."""

    async def link_to_wirkgefuege(self, claim_id: str, wirkgefuege_ref: str) -> Claim:
        claim = ClaimMother.causal()
        claim.link_to_wirkgefuege(wirkgefuege_ref)
        return claim


@pytest.fixture
def override_claim_service():
    app.dependency_overrides[get_claim_service] = lambda: FakeClaimService()
    yield
    app.dependency_overrides.pop(get_claim_service, None)


@pytest.mark.asyncio
async def test_link_claim_to_wirkgefuege_returns_200(override_claim_service) -> None:
    """Expects POST /claims/{id}/link-to-wirkgefuege to return HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/claims/claim-001/link-to-wirkgefuege",
            json={"wirkgefuege_ref": "slot-abc"},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "linked"
    assert response.json()["wirkgefuege_ref"] == "slot-abc"
```

- [ ] **Step 14: Run all tests**

```bash
python -m pytest api/tests/ -m "not integration" -q
```

Expected: all tests pass.

- [ ] **Step 15: Commit**

```bash
git add api/repositories/claim_repository.py \
        api/repositories/supabase_claim_repository.py \
        api/tests/fakes/fake_claim_repository.py \
        api/services/claim_service.py \
        api/schemas/claims.py \
        api/routers/claims.py \
        api/dependencies.py \
        api/tests/test_claim_repository.py \
        api/tests/test_claim_service.py \
        api/tests/test_claims_router.py
git commit -m "feat: ClaimRepository find_by_id+update, ClaimService, link-to-wirkgefuege endpoint"
```

---

## Task 8: Full regression run

**Files:** none

- [ ] **Step 1: Run full unit test suite**

```bash
source api/.venv/bin/activate && python -m pytest api/tests/ -m "not integration" -v
```

Expected: all tests PASS, zero failures, zero errors.

- [ ] **Step 2: Run pre-commit hooks**

```bash
git add -A && pre-commit run --files $(git diff --cached --name-only | tr '\n' ' ')
```

Expected: ruff lint, ruff format, mypy, tach all PASS.

- [ ] **Step 3: Final commit if needed**

```bash
git commit -m "fix: address any regressions found in full test run"
```

(only if there were hook fixes to commit)

---

## Scope Notes for the Implementer

**What is NOT in Plan C (deferred):**
- `GET /causal-models/{id}/slots` — list endpoint (add GET after POST works)
- `GET /causal-models/{id}/relations` — list endpoint
- Strength, uncertainty, conditions, scope on CausalRelation (complex fields)
- `CausalRelation.update()` domain method test file `test_causal_relation_domain.py` already exists — just add tests to it
- Frontend changes — handled in a later plan
- Integration tests against real Supabase — marked `@pytest.mark.integration`, run separately

**Files also affected by Plan C that require checking in regression (Lessons Learned from Plan B):**
- `api/routers/claims.py` — built ClaimResponse inline; now updated in Task 7
- `api/tests/fakes/fake_claim_repository.py` — constructs Claim directly; updated in Task 7
- `api/tests/test_claims_router.py` — creates Claim objects; extended in Task 7
