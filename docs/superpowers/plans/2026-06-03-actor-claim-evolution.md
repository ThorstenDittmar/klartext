# Actor + Claim Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename Actor fields (`name→label`, `typ→actor_type`, `description→notes`) and add `entity_ref`; add `ClaimStatus`, `label`, `wirkgefuege_ref` to Claim with `link_to_wirkgefuege()` and `mark_unresolved()` methods — propagated through all layers.

**Architecture:** Domain-first: fix both domain objects first (tests are already written and RED), then propagate changes layer by layer (test infra → service → schemas+router → repositories → provider → DB migration → seeddata → frontend). Each layer has its own failing tests before the implementation changes.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Supabase/PostgREST, React, TypeScript.

---

## File Map

| File | Change |
|---|---|
| `api/models/narrative.py` | Actor: rename fields, add entity_ref |
| `api/models/claim.py` | Add ClaimStatus, label, status, wirkgefuege_ref, 2 methods |
| `api/tests/test_narrative_domain.py` | Remove old-API tests; rewrite 2 Narrative+Actor tests |
| `api/tests/test_claim_domain.py` | Already written (RED) — no changes needed |
| `api/tests/mothers/narrative_mother.py` | Update Actor.create calls |
| `api/tests/mothers/claim_mother.py` | Add label to Claim.create calls |
| `api/tests/fakes/fake_narrative_repository.py` | Update add_actor field names |
| `api/tests/test_narrative_service.py` | Update actor field names in calls/assertions |
| `api/tests/test_narratives_router.py` | Update FakeNarrativeService + JSON field names |
| `api/tests/test_narrative_repository.py` | Update actor field names in assertions |
| `api/tests/test_claim_extractor_service.py` | Add label to Claim.create calls |
| `api/tests/test_scene_claims_router.py` | Add label to Claim.create calls |
| `api/tests/test_claude_claim_extraction_provider.py` | Add label to mock responses |
| `api/tests/test_seeddata.py` | Update `actor.name` → `actor.label`, `actor.typ` → `actor.actor_type` |
| `api/schemas/narratives.py` | Rename Actor request/response fields |
| `api/schemas/claims.py` | Add label, status, wirkgefuege_ref to ClaimResponse |
| `api/services/narrative_service.py` | Rename add_actor/update_actor params |
| `api/repositories/supabase_narrative_repository.py` | Update DB column names for actor |
| `api/repositories/supabase_claim_repository.py` | Add label, status, wirkgefuege_ref |
| `api/providers/claude_claim_extraction_provider.py` | Add label to prompt + _parse_claim |
| `api/routers/narratives.py` | Update _to_actor_response + _to_claim_response |
| `api/seeddata.py` | Update SeedActor field names |
| `supabase/migrations/20260603000001_actor_claim_evolution.sql` | Rename columns, add new ones |
| `frontend/src/lib/api.ts` | Actor interface + function signatures |
| `frontend/src/pages/NarrativeEditor.tsx` | State vars + API calls |

---

## Context for Subagents

**Project root:** `/Users/thormar/klartext`
**API root:** `/Users/thormar/klartext/api`
**Run tests from:** `/Users/thormar/klartext/api`
**Test command:** `cd /Users/thormar/klartext/api && python -m pytest <test_file> -v`
**Run all tests:** `cd /Users/thormar/klartext/api && python -m pytest --ignore=tests/test_narrative_repository.py -v` (skip integration tests unless DB is running)

**CLAUDE.md rules that apply:**
- All code in English (variable names, function names, method names, comments)
- TDD: tests first, then implementation
- OOP: changes to domain objects as explicit methods
- Getters via @property, no direct attribute access from outside
- Every non-trivial method gets a docstring
- Factory methods: `create()` for new objects, `from_record()` for DB records
- Type hints everywhere (parameters, return values, class attributes)
- `X | None` not `Optional[X]`

**Current state:** Actor uses `name`, `typ`, `description`. Claim uses `text`, `typ`, `confidence` only. Both domain test files have tests written that are RED because the implementation uses old field names. All downstream files (service, repo, router, frontend) still use the old API.

**What "already written and RED" means:** The test files `test_narrative_domain.py` (Actor section, lines 145–279) and `test_claim_domain.py` are fully written. They fail because the models don't implement the new API yet. Do NOT rewrite these tests — implement the models to make them pass.

---

## Task 1: Fix Actor domain object

**Files:**
- Modify: `api/models/narrative.py`
- Modify: `api/tests/test_narrative_domain.py` (cleanup old-API tests only)

The domain tests for Actor (lines 145–279 of `test_narrative_domain.py`) are already written and RED. The task is to implement the new Actor API and remove the leftover old-API tests that are now dead code.

- [ ] **Step 1: Run the Actor tests to confirm they are RED**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_domain.py -v -k "actor" 2>&1 | head -50
```

Expected: Multiple FAILED — `label`, `actor_type`, `notes`, `entity_ref` do not exist.

- [ ] **Step 2: Implement the new Actor class in `api/models/narrative.py`**

Replace the entire `Actor` class (keep `ActorType` as-is — it's correct):

```python
class Actor:
    """A participant in a Narrative.

    A person, organisation, group, institution or abstract entity that acts or is
    acted upon within the story. The optional entity_ref links this actor to a
    causal model Entity, forming the bridge between narrative figure and formal model.

    Invariants enforced at construction time:
    - label must not be empty
    """

    def __init__(
        self,
        id: str | None,
        label: str,
        actor_type: ActorType,
        notes: str | None,
        entity_ref: str | None = None,
    ) -> None:
        self._id = id
        self._label = label
        self._actor_type = actor_type
        self._notes = notes
        self._entity_ref = entity_ref

    @classmethod
    def create(
        cls,
        label: str,
        actor_type: ActorType,
        notes: str | None = None,
        entity_ref: str | None = None,
    ) -> "Actor":
        """Creates a new Actor from user input. Raises ActorValidationError for empty label."""
        if not label.strip():
            raise ActorValidationError("label must not be empty")
        return cls(id=None, label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Actor":
        """Reconstructs an Actor from a database record.

        Raises ActorValidationError for an unrecognised actor_type value.
        """
        try:
            actor_type = ActorType(record["actor_type"])
        except ValueError as e:
            raise ActorValidationError(
                f"Unknown actor type in record: {record['actor_type']}"
            ) from e
        return cls(
            id=record["id"],
            label=record["label"],
            actor_type=actor_type,
            notes=record.get("notes"),
            entity_ref=record.get("entity_ref"),
        )

    def update(self, label: str, actor_type: ActorType, notes: str | None) -> None:
        """Updates label, actor_type and notes. Raises ActorValidationError for empty label."""
        if not label.strip():
            raise ActorValidationError("label must not be empty")
        self._label = label
        self._actor_type = actor_type
        self._notes = notes

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def actor_type(self) -> ActorType:
        return self._actor_type

    @property
    def notes(self) -> str | None:
        return self._notes

    @property
    def entity_ref(self) -> str | None:
        return self._entity_ref
```

- [ ] **Step 3: Clean up old-API tests in `api/tests/test_narrative_domain.py`**

The file has THREE sections that use the OLD API and must be removed or rewritten:

**3a — Rewrite `test_narrative_add_actor_appends_actor` (around line 292):**

Replace:
```python
def test_narrative_add_actor_appends_actor() -> None:
    """Expects add_actor() to make the actor accessible via the actors property."""
    narrative = Narrative.create(title="A Novel")
    actor = Actor.create(name="Max", typ=ActorType.INDIVIDUAL)

    narrative.add_actor(actor)

    assert len(narrative.actors) == 1
    assert narrative.actors[0].name == "Max"
```
With:
```python
def test_narrative_add_actor_appends_actor() -> None:
    """Expects add_actor() to make the actor accessible via the actors property."""
    narrative = Narrative.create(title="A Novel")
    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)

    narrative.add_actor(actor)

    assert len(narrative.actors) == 1
    assert narrative.actors[0].label == "Max"
```

**3b — Rewrite `test_narrative_add_actor_preserves_insertion_order` (around line 302):**

Replace:
```python
def test_narrative_add_actor_preserves_insertion_order() -> None:
    """Expects actors to appear in the order they were added."""
    narrative = Narrative.create(title="A Novel")
    narrative.add_actor(Actor.create(name="Max", typ=ActorType.INDIVIDUAL))
    narrative.add_actor(Actor.create(name="CDU", typ=ActorType.ORGANISATION))
    narrative.add_actor(Actor.create(name="Voters", typ=ActorType.GROUP))

    assert narrative.actors[0].name == "Max"
    assert narrative.actors[1].name == "CDU"
    assert narrative.actors[2].name == "Voters"
```
With:
```python
def test_narrative_add_actor_preserves_insertion_order() -> None:
    """Expects actors to appear in the order they were added."""
    narrative = Narrative.create(title="A Novel")
    narrative.add_actor(Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL))
    narrative.add_actor(Actor.create(label="CDU", actor_type=ActorType.ORGANISATION))
    narrative.add_actor(Actor.create(label="Voters", actor_type=ActorType.GROUP))

    assert narrative.actors[0].label == "Max"
    assert narrative.actors[1].label == "CDU"
    assert narrative.actors[2].label == "Voters"
```

**3c — Remove the entire `--- Actor.update ---` section** (the OLD update tests, around lines 368–406):

Delete these four tests entirely (they duplicate the new tests at lines 262–279):
```python
# --- Actor.update ---


def test_actor_update_changes_all_fields() -> None:
    ...

def test_actor_update_can_clear_description() -> None:
    ...

def test_actor_update_raises_for_empty_name() -> None:
    ...

def test_actor_update_raises_for_whitespace_only_name() -> None:
    ...
```

- [ ] **Step 4: Run Actor tests to confirm GREEN**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_domain.py -v 2>&1 | tail -20
```

Expected: All PASSED.

- [ ] **Step 5: Commit**

```bash
cd /Users/thormar/klartext && git add api/models/narrative.py api/tests/test_narrative_domain.py
git commit -m "feat: rename Actor fields to label/actor_type/notes and add entity_ref"
```

---

## Task 2: Fix Claim domain object

**Files:**
- Modify: `api/models/claim.py`

The domain tests (`test_claim_domain.py`) are already written and RED.

- [ ] **Step 1: Run claim domain tests to confirm RED**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_claim_domain.py -v 2>&1 | head -30
```

Expected: Multiple FAILED — `ClaimStatus`, `label`, `status`, `wirkgefuege_ref`, `link_to_wirkgefuege`, `mark_unresolved` do not exist.

- [ ] **Step 2: Replace `api/models/claim.py` with the new implementation**

```python
"""Domain objects for claims extracted from narrative scenes."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from api.exceptions.claim import ClaimValidationError


class ClaimType(StrEnum):
    """The epistemic type of a claim.

    Values are stored in the database and passed to the Claude API prompt.
    """

    EMPIRICAL = "empirical"
    CAUSAL = "causal"
    DEFINITIONAL = "definitional"
    NORMATIVE = "normative"
    PROGNOSTIC = "prognostic"
    COUNTERFACTUAL = "counterfactual"
    METHODOLOGICAL = "methodological"
    UNCERTAINTY = "uncertainty"


class ClaimStatus(StrEnum):
    """The formalisation status of a claim.

    DRAFT:      Default. No Wirkgefüge link yet — blocks publication.
    LINKED:     Mapped to a causal model element — appears as confirmed claim.
    UNRESOLVED: Consciously marked as an open gap — appears as open finding.
    """

    DRAFT = "draft"
    LINKED = "linked"
    UNRESOLVED = "unresolved"


class Claim:
    """A single extractable assertion from a Scene.

    Claims are provisional – the author can confirm, reject, or reformulate them.
    The label is a short human-readable name; text is the full original wording.

    Invariants enforced at construction time:
    - label must not be empty
    - text must not be empty
    - confidence must be between 0.0 and 1.0 (inclusive)
    """

    def __init__(
        self,
        id: str | None,
        label: str,
        text: str,
        typ: ClaimType,
        confidence: float,
        status: ClaimStatus = ClaimStatus.DRAFT,
        wirkgefuege_ref: str | None = None,
    ) -> None:
        self._id = id
        self._label = label
        self._text = text
        self._typ = typ
        self._confidence = confidence
        self._status = status
        self._wirkgefuege_ref = wirkgefuege_ref

    @classmethod
    def create(cls, label: str, text: str, typ: ClaimType, confidence: float) -> "Claim":
        """Creates a new Claim from extracted data.

        Raises ClaimValidationError for empty label, empty text, or out-of-range confidence.
        """
        if not label.strip():
            raise ClaimValidationError("label must not be empty")
        if not text.strip():
            raise ClaimValidationError("text must not be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ClaimValidationError("confidence must be between 0.0 and 1.0")
        return cls(id=None, label=label, text=text, typ=typ, confidence=confidence)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Claim":
        """Reconstructs a Claim from a database record.

        Raises ClaimValidationError for an unrecognised typ value.
        """
        try:
            typ = ClaimType(record["typ"])
        except ValueError as e:
            raise ClaimValidationError(f"Unknown claim type in record: {record['typ']}") from e
        status = ClaimStatus(record.get("status", ClaimStatus.DRAFT))
        return cls(
            id=record["id"],
            label=record["label"],
            text=record["text"],
            typ=typ,
            confidence=record["confidence"],
            status=status,
            wirkgefuege_ref=record.get("wirkgefuege_ref"),
        )

    def link_to_wirkgefuege(self, ref_id: str) -> None:
        """Links this Claim to a causal model element and sets status to LINKED."""
        self._wirkgefuege_ref = ref_id
        self._status = ClaimStatus.LINKED

    def mark_unresolved(self) -> None:
        """Marks this Claim as an open, unresolvable gap. Sets status to UNRESOLVED."""
        self._status = ClaimStatus.UNRESOLVED

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def text(self) -> str:
        return self._text

    @property
    def typ(self) -> ClaimType:
        return self._typ

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def status(self) -> ClaimStatus:
        return self._status

    @property
    def wirkgefuege_ref(self) -> str | None:
        return self._wirkgefuege_ref
```

- [ ] **Step 3: Run claim domain tests to confirm GREEN**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_claim_domain.py -v 2>&1 | tail -20
```

Expected: All PASSED.

- [ ] **Step 4: Commit**

```bash
cd /Users/thormar/klartext && git add api/models/claim.py
git commit -m "feat: add ClaimStatus, label, wirkgefuege_ref and lifecycle methods to Claim"
```

---

## Task 3: Update test infrastructure

After Tasks 1 and 2, all test files that reference the old Actor/Claim API are broken. Fix them now so the rest of the layers can run their tests.

**Files:**
- Modify: `api/tests/mothers/narrative_mother.py`
- Modify: `api/tests/mothers/claim_mother.py`
- Modify: `api/tests/fakes/fake_narrative_repository.py`
- Modify: `api/tests/test_narrative_service.py`
- Modify: `api/tests/test_narratives_router.py`
- Modify: `api/tests/test_narrative_repository.py`
- Modify: `api/tests/test_claim_extractor_service.py`
- Modify: `api/tests/test_scene_claims_router.py`
- Modify: `api/tests/test_seeddata.py`

- [ ] **Step 1: Update `api/tests/mothers/narrative_mother.py`**

Find `with_actors()` method and update the three Actor.create calls:

```python
    @staticmethod
    def with_actors() -> Narrative:
        """Narrative with one scene and three actors of different types.

        Use for actor-related tests.
        """
        narrative = Narrative.create(title="Klartext")
        narrative.add_scene(SceneMother.minimal())
        narrative.add_actor(Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL))
        narrative.add_actor(Actor.create(label="CDU", actor_type=ActorType.ORGANISATION))
        narrative.add_actor(Actor.create(label="Voters", actor_type=ActorType.GROUP))
        return narrative
```

- [ ] **Step 2: Update `api/tests/mothers/claim_mother.py`**

Add `label=` to every `Claim.create()` call. The label should be a short English description of the claim:

```python
"""ClaimMother — builds Claim test objects for all test scenarios."""

from __future__ import annotations

from api.models.claim import Claim, ClaimType


class ClaimMother:
    """Factory for Claim test objects.

    Use causal() or empirical() for single-claim tests.
    Use collection() for tests that need a varied set of claims.
    """

    @staticmethod
    def causal() -> Claim:
        """A single causal claim with high confidence."""
        return Claim.create(
            label="Money supply causes inflation",
            text="Inflation entsteht durch eine Ausweitung der Geldmenge.",
            typ=ClaimType.CAUSAL,
            confidence=0.9,
        )

    @staticmethod
    def empirical() -> Claim:
        """A single empirical claim with moderate confidence."""
        return Claim.create(
            label="2022 inflation rate above 7%",
            text="Die Inflationsrate lag 2022 bei über 7 Prozent.",
            typ=ClaimType.EMPIRICAL,
            confidence=0.8,
        )

    @staticmethod
    def normative() -> Claim:
        """A single normative claim — for tests that distinguish claim types."""
        return Claim.create(
            label="State should cap energy prices",
            text="Der Staat sollte die Energiepreise deckeln.",
            typ=ClaimType.NORMATIVE,
            confidence=0.75,
        )

    @staticmethod
    def with_low_confidence() -> Claim:
        """A claim with low confidence — for confidence boundary tests."""
        return Claim.create(
            label="Inflation may decline by 2025",
            text="Möglicherweise wird die Inflation bis 2025 sinken.",
            typ=ClaimType.PROGNOSTIC,
            confidence=0.3,
        )

    @staticmethod
    def collection() -> list[Claim]:
        """A varied set of claims covering different types — for extraction and storage tests."""
        return [
            ClaimMother.causal(),
            ClaimMother.empirical(),
            ClaimMother.normative(),
        ]
```

- [ ] **Step 3: Update `api/tests/fakes/fake_narrative_repository.py`**

In `add_actor()`, change the `Actor(...)` constructor call:

```python
    async def add_actor(self, narrative_id: str, actor: Actor) -> Actor:
        """Appends an actor to the stored narrative and returns it with an assigned ID."""
        self.logger.info("FakeNarrativeRepository.add_actor: narrative_id=%s", narrative_id)
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        saved_actor = Actor(
            id=str(uuid.uuid4()),
            label=actor.label,
            actor_type=actor.actor_type,
            notes=actor.notes,
            entity_ref=actor.entity_ref,
        )
        self._store[narrative_id].add_actor(saved_actor)
        return saved_actor
```

- [ ] **Step 4: Update `api/tests/test_narrative_service.py`**

The service tests reference old Actor fields. Make these targeted replacements:

**4a — In `add_actor` tests, change positional params to keyword params:**

All `service.add_actor(narrative.id, "Max", ActorType.INDIVIDUAL)` calls stay as-is (positional args) but the assertions change:

Find and replace:
```python
    assert actor.name == "CDU"
    assert actor.typ == ActorType.ORGANISATION
```
→
```python
    assert actor.label == "CDU"
    assert actor.actor_type == ActorType.ORGANISATION
```

Find and replace:
```python
    assert actor.description is None
```
→
```python
    assert actor.notes is None
```

**4b — In `update_actor` tests:**

Find and replace the `update_actor` call:
```python
    updated = await service.update_actor(
        narrative.id, actor.id, "CDU", ActorType.ORGANISATION, "A party."
    )
```
stays the same (positional params are fine — service signature will be updated).

Find and replace the assertions:
```python
    assert updated.name == "CDU"
    assert updated.typ == ActorType.ORGANISATION
    assert updated.description == "A party."
```
→
```python
    assert updated.label == "CDU"
    assert updated.actor_type == ActorType.ORGANISATION
    assert updated.notes == "A party."
```

**4c — Update test docstrings** to say "label" instead of "name", "actor_type" instead of "type":

```python
async def test_narrative_service_add_actor_returns_actor_with_correct_name_and_type() -> None:
    """Expects the returned Actor to carry the label and actor_type that were passed in."""
```

```python
async def test_narrative_service_add_actor_description_defaults_to_none() -> None:
    """Expects notes to be None when not provided."""
```

```python
async def test_narrative_service_add_actor_raises_for_empty_name() -> None:
    """Expects ActorValidationError when the actor label is empty."""
```

```python
async def test_narrative_service_update_actor_returns_actor_with_updated_fields() -> None:
    """Expects update_actor to return an Actor carrying the new label, actor_type and notes."""
```

```python
async def test_narrative_service_update_actor_raises_for_empty_name() -> None:
    """Expects ActorValidationError when the new label is empty."""
```

- [ ] **Step 5: Update `api/tests/test_narratives_router.py`**

**5a — Update `FakeNarrativeService.add_actor` method (around line 97):**

```python
    async def add_actor(
        self,
        narrative_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None = None,
        entity_ref: str | None = None,
    ) -> Actor:
        if self._raise_on_add_actor:
            raise self._raise_on_add_actor
        return Actor(id=SAVED_ACTOR_ID, label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref)
```

**5b — Update `FakeNarrativeService.update_actor` method (around line 104):**

```python
    async def update_actor(
        self,
        narrative_id: str,
        actor_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None,
    ) -> Actor:
        if self._raise_on_update_actor:
            raise self._raise_on_update_actor
        return Actor(id=actor_id, label=label, actor_type=actor_type, notes=notes)
```

**5c — Update all actor JSON payloads in test requests:**

Replace every occurrence of `{"name": ..., "typ": ...}` with `{"label": ..., "actor_type": ...}`. Replace `"description"` with `"notes"`. Concretely:

- `json={"name": "Max", "typ": "individual"}` → `json={"label": "Max", "actor_type": "individual"}`
- `json={"name": "CDU", "typ": "organisation", "description": "A party."}` → `json={"label": "CDU", "actor_type": "organisation", "notes": "A party."}`
- `json={"name": "", "typ": "individual"}` → `json={"label": "", "actor_type": "individual"}`

**5d — Update all response assertions:**

- `data["name"]` → `data["label"]`
- `data["typ"]` → `data["actor_type"]`
- `data["description"]` → `data["notes"]`

**5e — Update test docstrings** to say "label" instead of "name":

```python
async def test_narratives_add_actor_response_contains_id_name_and_type() -> None:
    """Expects the response to include the actor id, label and actor_type."""
```

```python
async def test_narratives_add_actor_returns_422_for_empty_name() -> None:
    """Expects 422 when the label field is an empty string."""
```

- [ ] **Step 6: Update `api/tests/test_narrative_repository.py`**

Find and replace all Actor field references in assertions:

- `actor.name` → `actor.label`
- `actor.typ` → `actor.actor_type`
- `Actor.create(name=..., typ=...)` → `Actor.create(label=..., actor_type=...)`

Concretely:

```python
    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)
    ...
    assert saved_actor.id is not None
```

```python
    actor = Actor.create(label="CDU", actor_type=ActorType.ORGANISATION)
    ...
    assert saved_actor.label == "CDU"
    assert saved_actor.actor_type == ActorType.ORGANISATION
```

```python
    found = await repo.get_actor(saved_narrative.id, saved_actor.id)
    assert found.id == saved_actor.id
    assert found.label == "Max"
```

Also update `Actor.create(name="Max", typ=ActorType.INDIVIDUAL)` → `Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)` in any test helper or fixture that creates Actors.

- [ ] **Step 7: Update `api/tests/test_claim_extractor_service.py`**

In `FakeClaimExtractionProvider.extract()` add `label=` to each `Claim.create()`:

```python
class FakeClaimExtractionProvider(ClaimExtractionProvider):
    """Returns a fixed list of claims regardless of input."""

    async def extract(self, scene: Scene) -> list[Claim]:
        return [
            Claim.create(
                label="Money supply causes inflation",
                text="Inflation entsteht durch Geldmenge.",
                typ=ClaimType.CAUSAL,
                confidence=0.9,
            ),
            Claim.create(
                label="Rate hikes dampen demand",
                text="Zinserhöhungen dämpfen die Nachfrage.",
                typ=ClaimType.CAUSAL,
                confidence=0.85,
            ),
        ]
```

- [ ] **Step 8: Update `api/tests/test_scene_claims_router.py`**

In `FakeClaimExtractorService.__init__()` add `label=` to the `Claim.create()` call:

```python
    def __init__(self, claims: list[Claim] | None = None) -> None:
        self._claims = claims or [
            Claim.create(
                label="Money supply causes inflation",
                text="Inflation entsteht durch Geldmenge.",
                typ=ClaimType.CAUSAL,
                confidence=0.9,
            )
        ]
        self.received_scene: Scene | None = None
```

Also check line ~227 for another `Claim.create()` call and add `label=` there too:

```python
            Claim.create(
                label="Test claim",
                text="...",   # keep existing text
                typ=ClaimType.CAUSAL,
                confidence=0.9,
            )
```

- [ ] **Step 9: Update `api/tests/test_seeddata.py`**

Replace `actor.name` and `actor.typ` with the new field names:

```python
def test_seed_actors_all_have_non_empty_names() -> None:
    """Expects every seed actor to have a non-empty label."""
    for actor in SEED_ACTORS:
        assert actor.label.strip() != ""


def test_seed_actors_all_have_valid_types() -> None:
    """Expects every seed actor type to be a valid ActorType value."""
    valid_values = {t.value for t in ActorType}
    for actor in SEED_ACTORS:
        assert actor.actor_type in valid_values, f"Unknown actor_type: {actor.actor_type!r}"


def test_seed_actors_include_at_least_one_individual() -> None:
    """Expects at least one actor of type INDIVIDUAL in the seed data."""
    types = {a.actor_type for a in SEED_ACTORS}
    assert "individual" in types
```

- [ ] **Step 10: Run all non-integration tests**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_domain.py tests/test_claim_domain.py tests/test_narrative_service.py tests/test_claim_extractor_service.py tests/test_scene_claims_router.py tests/test_seeddata.py -v 2>&1 | tail -30
```

Expected: All PASSED (or errors only in schema/router/provider tests not yet updated).

- [ ] **Step 11: Commit**

```bash
cd /Users/thormar/klartext && git add \
  api/tests/mothers/narrative_mother.py \
  api/tests/mothers/claim_mother.py \
  api/tests/fakes/fake_narrative_repository.py \
  api/tests/test_narrative_service.py \
  api/tests/test_narratives_router.py \
  api/tests/test_narrative_repository.py \
  api/tests/test_claim_extractor_service.py \
  api/tests/test_scene_claims_router.py \
  api/tests/test_seeddata.py
git commit -m "test: update all test infrastructure to new Actor and Claim API"
```

---

## Task 4: Update Narrative Service

**Files:**
- Modify: `api/services/narrative_service.py`

- [ ] **Step 1: Run service tests to see what fails**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_service.py -v 2>&1 | head -30
```

Expected: `add_actor` and `update_actor` tests fail — service still uses `name`, `typ`, `description`.

- [ ] **Step 2: Update `add_actor` in `api/services/narrative_service.py`**

Replace:
```python
    async def add_actor(
        self,
        narrative_id: str,
        name: str,
        typ: ActorType,
        description: str | None = None,
    ) -> Actor:
        """Adds a new Actor to the Narrative with the given ID.

        Returns the saved Actor with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorValidationError if the name is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = Actor.create(name=name, typ=typ, description=description)
        return await self._repository.add_actor(narrative_id, actor)
```
With:
```python
    async def add_actor(
        self,
        narrative_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None = None,
        entity_ref: str | None = None,
    ) -> Actor:
        """Adds a new Actor to the Narrative with the given ID.

        Returns the saved Actor with an assigned ID.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorValidationError if the label is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = Actor.create(label=label, actor_type=actor_type, notes=notes, entity_ref=entity_ref)
        return await self._repository.add_actor(narrative_id, actor)
```

- [ ] **Step 3: Update `update_actor` in `api/services/narrative_service.py`**

Replace:
```python
    async def update_actor(
        self,
        narrative_id: str,
        actor_id: str,
        name: str,
        typ: ActorType,
        description: str | None,
    ) -> Actor:
        """Updates name, type and description of an existing Actor.

        Uses find → change → save: loads the actor, applies changes via the domain method,
        then persists the result.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises ActorValidationError if the new name is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = await self._repository.get_actor(narrative_id, actor_id)
        actor.update(name=name, typ=typ, description=description)
        return await self._repository.update_actor(narrative_id, actor)
```
With:
```python
    async def update_actor(
        self,
        narrative_id: str,
        actor_id: str,
        label: str,
        actor_type: ActorType,
        notes: str | None,
    ) -> Actor:
        """Updates label, actor_type and notes of an existing Actor.

        Uses find → change → save: loads the actor, applies changes via the domain method,
        then persists the result.
        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        Raises ActorNotFoundError if no Actor with that ID exists in the Narrative.
        Raises ActorValidationError if the new label is empty.
        Raises NarrativePersistenceError on database failure.
        """
        await self._repository.find_by_id(narrative_id)
        actor = await self._repository.get_actor(narrative_id, actor_id)
        actor.update(label=label, actor_type=actor_type, notes=notes)
        return await self._repository.update_actor(narrative_id, actor)
```

- [ ] **Step 4: Run service tests to confirm GREEN**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_service.py -v 2>&1 | tail -20
```

Expected: All PASSED.

- [ ] **Step 5: Commit**

```bash
cd /Users/thormar/klartext && git add api/services/narrative_service.py
git commit -m "feat: rename actor params in NarrativeService to label/actor_type/notes/entity_ref"
```

---

## Task 5: Update Schemas + Router

**Files:**
- Modify: `api/schemas/narratives.py`
- Modify: `api/schemas/claims.py`
- Modify: `api/routers/narratives.py`

- [ ] **Step 1: Run router tests to see current failures**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narratives_router.py -v 2>&1 | head -40
```

Expected: Tests around `add_actor` and `update_actor` fail — schema still uses `name`, `typ`, `description`.

- [ ] **Step 2: Update `api/schemas/narratives.py`**

Replace the three Actor-related schemas:

```python
class CreateActorRequest(BaseModel):
    """Request body for POST /narratives/{id}/actors."""

    label: str
    actor_type: ActorType
    notes: str | None = None
    entity_ref: str | None = None

    @field_validator("label")
    @classmethod
    def label_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only labels."""
        if not value.strip():
            raise ValueError("label must not be empty")
        return value


class UpdateActorRequest(BaseModel):
    """Request body for PUT /narratives/{id}/actors/{actor_id}."""

    label: str
    actor_type: ActorType
    notes: str | None = None

    @field_validator("label")
    @classmethod
    def label_not_empty(cls, value: str) -> str:
        """Rejects empty or whitespace-only labels."""
        if not value.strip():
            raise ValueError("label must not be empty")
        return value


class ActorResponse(BaseModel):
    """A single actor as returned in the API response."""

    id: str
    label: str
    actor_type: str
    notes: str | None
    entity_ref: str | None = None
```

- [ ] **Step 3: Update `api/schemas/claims.py`**

Add `label`, `status`, `wirkgefuege_ref` to `ClaimResponse`:

```python
class ClaimResponse(BaseModel):
    """Response shape for a single extracted Claim."""

    label: str
    text: str
    typ: str
    confidence: float
    status: str = "draft"
    wirkgefuege_ref: str | None = None
```

- [ ] **Step 4: Update `api/routers/narratives.py`**

**4a — Update `_to_actor_response()`:**

```python
def _to_actor_response(actor: Actor) -> ActorResponse:
    """Converts an Actor domain object into an ActorResponse schema."""
    return ActorResponse(
        id=actor.id,  # type: ignore[arg-type]
        label=actor.label,
        actor_type=actor.actor_type.value,
        notes=actor.notes,
        entity_ref=actor.entity_ref,
    )
```

**4b — Update `_to_claim_response()`:**

```python
def _to_claim_response(claim: Claim) -> ClaimResponse:
    """Converts a Claim domain object into a ClaimResponse schema."""
    return ClaimResponse(
        label=claim.label,
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
        status=claim.status.value,
        wirkgefuege_ref=claim.wirkgefuege_ref,
    )
```

**4c — Update `add_actor` endpoint:**

```python
@router.post(
    "/{narrative_id}/actors",
    status_code=status.HTTP_201_CREATED,
    response_model=ActorResponse,
)
async def add_actor(
    narrative_id: str,
    request: CreateActorRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> ActorResponse:
    """Adds a new Actor to the Narrative with the given ID."""
    actor = await service.add_actor(
        narrative_id,
        request.label,
        request.actor_type,
        request.notes,
        request.entity_ref,
    )
    return _to_actor_response(actor)
```

**4d — Update `update_actor` endpoint:**

```python
@router.put(
    "/{narrative_id}/actors/{actor_id}",
    response_model=ActorResponse,
)
async def update_actor(
    narrative_id: str,
    actor_id: str,
    request: UpdateActorRequest,
    service: NarrativeService = Depends(get_narrative_service),
) -> ActorResponse:
    """Updates the label, actor_type and notes of an existing Actor."""
    actor = await service.update_actor(
        narrative_id, actor_id, request.label, request.actor_type, request.notes
    )
    return _to_actor_response(actor)
```

- [ ] **Step 5: Run router tests to confirm GREEN**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narratives_router.py tests/test_scene_claims_router.py -v 2>&1 | tail -30
```

Expected: All PASSED.

- [ ] **Step 6: Commit**

```bash
cd /Users/thormar/klartext && git add \
  api/schemas/narratives.py \
  api/schemas/claims.py \
  api/routers/narratives.py
git commit -m "feat: update actor and claim schemas and router to new field names"
```

---

## Task 6: Update Supabase Narrative Repository

**Files:**
- Modify: `api/repositories/supabase_narrative_repository.py`

This is the most extensive single-file change: every actor DB column reference must be updated.

- [ ] **Step 1: Note all changes needed**

The `narrative_actors` DB table (after Task 9 migration) will have:
- `label` (was `name`)
- `actor_type` (was `typ`)
- `notes` (was `description`)
- `entity_ref` (new)

All reads and writes in `supabase_narrative_repository.py` must be updated.

- [ ] **Step 2: Update `add_actor` method**

Replace the INSERT dict:
```python
                .insert(
                    {
                        "narrative_id": narrative_id,
                        "label": actor.label,
                        "actor_type": actor.actor_type.value,
                        "notes": actor.notes,
                        "entity_ref": actor.entity_ref,
                    }
                )
```

Update the log message:
```python
        self.logger.info(
            "SupabaseNarrativeRepository.add_actor: narrative_id=%s, label=%s",
            narrative_id,
            actor.label,
        )
```

Update the `Actor.from_record()` call after the INSERT:
```python
        return Actor.from_record(
            {
                "id": row["id"],
                "label": row["label"],
                "actor_type": row["actor_type"],
                "notes": row.get("notes"),
                "entity_ref": row.get("entity_ref"),
            }
        )
```

- [ ] **Step 3: Update `get_actor` method**

Update the `Actor.from_record()` call:
```python
        return Actor.from_record(
            {
                "id": row["id"],
                "label": row["label"],
                "actor_type": row["actor_type"],
                "notes": row.get("notes"),
                "entity_ref": row.get("entity_ref"),
            }
        )
```

Update the log message:
```python
        self.logger.debug(
            "SupabaseNarrativeRepository.get_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor_id,
        )
```
(no change needed here — no actor field name in the log)

- [ ] **Step 4: Update `update_actor` method**

Replace the UPDATE dict:
```python
                .update(
                    {
                        "label": actor.label,
                        "actor_type": actor.actor_type.value,
                        "notes": actor.notes,
                        "entity_ref": actor.entity_ref,
                    }
                )
```

Update the `Actor.from_record()` call after the UPDATE:
```python
        return Actor.from_record(
            {
                "id": row["id"],
                "label": row["label"],
                "actor_type": row["actor_type"],
                "notes": row.get("notes"),
                "entity_ref": row.get("entity_ref"),
            }
        )
```

Update the log message:
```python
        self.logger.info(
            "SupabaseNarrativeRepository.update_actor: narrative_id=%s, actor_id=%s",
            narrative_id,
            actor.id,
        )
```
(no change needed here)

- [ ] **Step 5: Update `find_by_id` — actor loop**

The actor loop in `find_by_id` currently reads `name`, `typ`, `description` from the DB row.  
Replace the `Actor.from_record()` call:

```python
        for actor_row in records(actor_result.data):
            narrative.add_actor(
                Actor.from_record(
                    {
                        "id": actor_row["id"],
                        "label": actor_row["label"],
                        "actor_type": actor_row["actor_type"],
                        "notes": actor_row.get("notes"),
                        "entity_ref": actor_row.get("entity_ref"),
                    }
                )
            )
```

- [ ] **Step 6: Commit**

```bash
cd /Users/thormar/klartext && git add api/repositories/supabase_narrative_repository.py
git commit -m "feat: update SupabaseNarrativeRepository to use new actor column names"
```

(Integration tests for this file run against the real DB — they will pass after the migration in Task 9.)

---

## Task 7: Update Supabase Claim Repository + Claude Provider + Seeddata

**Files:**
- Modify: `api/repositories/supabase_claim_repository.py`
- Modify: `api/providers/claude_claim_extraction_provider.py`
- Modify: `api/tests/test_claude_claim_extraction_provider.py`
- Modify: `api/seeddata.py`

- [ ] **Step 1: Update `api/repositories/supabase_claim_repository.py`**

**1a — Update `save_all()`** to include `label`, `status`, `wirkgefuege_ref`:

```python
        rows = [
            {
                "scene_id": scene_id,
                "label": claim.label,
                "text": claim.text,
                "typ": claim.typ.value,
                "confidence": claim.confidence,
                "status": claim.status.value,
                "wirkgefuege_ref": claim.wirkgefuege_ref,
            }
            for claim in claims
        ]
```

The `Claim.from_record()` call after the INSERT stays as-is — the DB will return all columns.

**1b — Add logger** (this class currently has no logger — add it per CLAUDE.md standard):

```python
import logging

class SupabaseClaimRepository(ClaimRepository):
    """Reads and writes Claims using the Supabase PostgREST API."""

    logger = logging.getLogger(__name__)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save_all(self, claims: list[Claim], scene_id: str) -> list[Claim]:
        """Inserts all Claims for the given scene. Returns Claims with assigned IDs."""
        self.logger.info(
            "SupabaseClaimRepository.save_all: scene_id=%s, count=%d",
            scene_id,
            len(claims),
        )
        ...

    async def find_by_scene_id(self, scene_id: str) -> list[Claim]:
        """Returns all Claims stored for the given scene ID."""
        self.logger.debug("SupabaseClaimRepository.find_by_scene_id: scene_id=%s", scene_id)
        ...
```

- [ ] **Step 2: Update `api/tests/test_claude_claim_extraction_provider.py`**

Every mock JSON response must now include a `label` field, because `_parse_claim` will read it.

Find all `json.dumps([{"text": ..., "typ": ..., "confidence": ...}])` patterns and add `label`:

```python
    response = json.dumps(
        [
            {
                "label": "Inflation through money supply",
                "text": "Inflation entsteht durch Geldmenge.",
                "typ": "causal",
                "confidence": 0.9,
            }
        ]
    )
```

Do this for every mock response in the test file. Also update the assertion for `ClaimExtractionError`:

```python
    response = json.dumps(
        [{"label": "Test claim", "text": "Ein Claim.", "typ": "empirical", "confidence": 1.5},
         {"label": "Another claim", "text": "Noch ein Claim.", "typ": "empirical", "confidence": -0.2}]
    )
```

```python
    response = json.dumps([{"label": "Test claim", "text": "Ein Claim.", "typ": "empirical", "confidence": 0.8}])
```

```python
    raw = json.dumps([{"label": "Test claim", "text": "Ein Claim.", "typ": "empirical", "confidence": 0.8}])
```

```python
    response = json.dumps([{"label": "Unknown type claim", "text": "Ein Claim.", "typ": "unbekannter_claim", "confidence": 0.8}])
```

- [ ] **Step 3: Update `api/providers/claude_claim_extraction_provider.py`**

**3a — Update the system prompt** to include `label` in the requested JSON fields:

```python
_SYSTEM_PROMPT = f"""Du bist ein Experte für epistemische Analyse narrativer Texte.

Deine Aufgabe: Extrahiere vorläufige Claims aus dem gegebenen Text.
Ein Claim ist eine behauptete Aussage –
empirisch, kausal, normativ, prognostisch oder definitorisch.

Antworte ausschließlich mit einem JSON-Array. Jeder Eintrag hat:
- "label": Kurzer englischer Titel des Claims (max. 80 Zeichen)
- "text": Die extrahierte Aussage (vollständiger Satz, max. 200 Zeichen)
- "typ": Einer von: {_CLAIM_TYPES}
- "confidence": Float zwischen 0.0 und 1.0

Extrahiere nur Claims die explizit oder klar implizit im Text vorhanden sind.
Maximal 10 Claims pro Text. Claims sind vorläufig – nicht verbindlich."""
```

**3b — Update `_parse_claim()`** to extract `label`:

```python
    def _parse_claim(self, record: dict[str, Any]) -> Claim:
        """Converts a raw API record into a Claim, clamping confidence to 0.0–1.0.

        Raises ClaimExtractionError if the API returned an unrecognised claim type.
        Uses text as fallback label if the API omitted the label field.
        """
        try:
            typ = ClaimType(record["typ"])
        except ValueError as e:
            raise ClaimExtractionError(
                f"Claude API returned unknown claim type: {record['typ']}"
            ) from e
        confidence = max(0.0, min(1.0, float(record.get("confidence", 0.5))))
        label = record.get("label") or record["text"][:80]
        return Claim.create(label=label, text=record["text"], typ=typ, confidence=confidence)
```

- [ ] **Step 4: Run Claude provider tests to confirm GREEN**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_claude_claim_extraction_provider.py -v 2>&1 | tail -20
```

Expected: All PASSED (unit tests only — integration test needs real API key).

- [ ] **Step 5: Update `api/seeddata.py`**

**5a — Update `SeedActor` dataclass:**

```python
@dataclass
class SeedActor:
    """A single actor definition for the narrative seed data."""

    label: str
    actor_type: str  # ActorType value ('individual', 'organisation', etc.)
    notes: str | None = field(default=None)
```

**5b — Update `SEED_ACTORS` list:**

```python
SEED_ACTORS: list[SeedActor] = [
    SeedActor(
        label="Mara",
        actor_type="individual",
        notes="Autorin und Mitgründerin von klartext.jetzt.",
    ),
    SeedActor(
        label="Tarek",
        actor_type="individual",
        notes="Entwickler und Mitgründer von klartext.jetzt.",
    ),
    SeedActor(
        label="klartext.jetzt",
        actor_type="organisation",
        notes="Die Plattform für epistemische Publikationen.",
    ),
    SeedActor(
        label="Öffentlichkeit",
        actor_type="abstract_entity",
        notes="Die abstrakte Gemeinschaft der Debattenteilnehmer.",
    ),
]
```

- [ ] **Step 6: Run seeddata tests to confirm GREEN**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_seeddata.py -v 2>&1 | tail -10
```

Expected: All PASSED.

- [ ] **Step 7: Commit**

```bash
cd /Users/thormar/klartext && git add \
  api/repositories/supabase_claim_repository.py \
  api/providers/claude_claim_extraction_provider.py \
  api/tests/test_claude_claim_extraction_provider.py \
  api/seeddata.py
git commit -m "feat: update claim repo, claude provider and seeddata to new Claim/Actor API"
```

---

## Task 8: DB Migration

**Files:**
- Create: `supabase/migrations/20260603000001_actor_claim_evolution.sql`

- [ ] **Step 1: Create the migration file**

```sql
-- Actor + Claim Evolution
--
-- Renames narrative_actors columns to match the domain model (Plan B):
--   name        → label
--   typ         → actor_type  (column + constraint rename)
--   description → notes
--   +entity_ref  (new nullable column)
--
-- Adds columns to claims:
--   +label          (short human-readable name for the claim)
--   +status         (draft | linked | unresolved)
--   +wirkgefuege_ref (nullable reference to a causal model element)

-- ============================================================
-- narrative_actors: rename name → label
-- ============================================================

ALTER TABLE narrative_actors RENAME COLUMN name TO label;

-- ============================================================
-- narrative_actors: rename description → notes
-- ============================================================

ALTER TABLE narrative_actors RENAME COLUMN description TO notes;

-- ============================================================
-- narrative_actors: rename typ → actor_type
-- ============================================================

-- Drop the existing CHECK constraint (auto-named in previous migration)
ALTER TABLE narrative_actors DROP CONSTRAINT narrative_actors_typ_check;
-- Rename the column
ALTER TABLE narrative_actors RENAME COLUMN typ TO actor_type;
-- Re-add the constraint with the new column name
ALTER TABLE narrative_actors ADD CONSTRAINT narrative_actors_actor_type_check
    CHECK (actor_type IN ('individual', 'organisation', 'group', 'institution', 'abstract_entity'));

-- ============================================================
-- narrative_actors: add entity_ref
-- ============================================================

ALTER TABLE narrative_actors ADD COLUMN entity_ref TEXT DEFAULT NULL;

-- ============================================================
-- claims: add label, status, wirkgefuege_ref
-- ============================================================

ALTER TABLE claims ADD COLUMN label TEXT NOT NULL DEFAULT '';
ALTER TABLE claims ADD COLUMN status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'linked', 'unresolved'));
ALTER TABLE claims ADD COLUMN wirkgefuege_ref TEXT DEFAULT NULL;

-- Backfill label from text for existing rows (first 80 chars)
UPDATE claims SET label = left(text, 80) WHERE label = '';

-- Remove the default so future inserts must provide a label
ALTER TABLE claims ALTER COLUMN label DROP DEFAULT;
```

- [ ] **Step 2: Apply the migration**

If using local Supabase:
```bash
cd /Users/thormar/klartext && supabase db push
```

Or apply via CLI:
```bash
cd /Users/thormar/klartext && supabase migration up
```

- [ ] **Step 3: Verify migration applied**

```bash
cd /Users/thormar/klartext && supabase db diff --use-migra 2>/dev/null | head -5
```

Expected: No diff (schema matches migrations).

- [ ] **Step 4: Run integration tests**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_repository.py -v 2>&1 | tail -20
```

Expected: All PASSED (actor reads/writes use new column names).

- [ ] **Step 5: Commit**

```bash
cd /Users/thormar/klartext && git add supabase/migrations/20260603000001_actor_claim_evolution.sql
git commit -m "feat: DB migration — rename actor columns, add entity_ref and claim evolution columns"
```

---

## Task 9: Update Frontend

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/pages/NarrativeEditor.tsx`

- [ ] **Step 1: Update `frontend/src/lib/api.ts`**

**1a — Update `Actor` interface:**

```typescript
export interface Actor {
  id: string;
  label: string;
  actor_type: string;
  notes: string | null;
  entity_ref: string | null;
}
```

**1b — Update `addActor` function:**

```typescript
    addActor: (
      narrativeId: string,
      label: string,
      actor_type: string,
      notes: string | null,
      entity_ref?: string | null,
    ) =>
      request<Actor>(`/narratives/${narrativeId}/actors`, {
        method: "POST",
        body: JSON.stringify({ label, actor_type, notes, entity_ref: entity_ref ?? null }),
      }),
```

**1c — Update `updateActor` function:**

```typescript
    updateActor: (
      narrativeId: string,
      actorId: string,
      label: string,
      actor_type: string,
      notes: string | null,
    ) =>
      request<Actor>(`/narratives/${narrativeId}/actors/${actorId}`, {
        method: "PUT",
        body: JSON.stringify({ label, actor_type, notes }),
      }),
```

- [ ] **Step 2: Update `frontend/src/pages/NarrativeEditor.tsx`**

**2a — Update state variable names:**

Replace:
```typescript
  const [actorName, setActorName] = useState("");
  const [actorTyp, setActorTyp] = useState("figur");
  const [actorDescription, setActorDescription] = useState("");
```
With:
```typescript
  const [actorLabel, setActorLabel] = useState("");
  const [actorType, setActorType] = useState("individual");
  const [actorNotes, setActorNotes] = useState("");
```

**2b — Update `openAddActor()`:**

```typescript
  function openAddActor() {
    setShowAddActor(true);
    setSelectedActorId(null);

    setActorLabel("");
    setActorType("individual");
    setActorNotes("");
  }
```

**2c — Update `selectActor()`:**

```typescript
  function selectActor(actor: Actor) {
    setSelectedActorId(actor.id);
    setShowAddActor(false);

    setActorLabel(actor.label);
    setActorType(actor.actor_type);
    setActorNotes(actor.notes ?? "");
  }
```

**2d — Update `cancelActorForm()`:**

```typescript
  function cancelActorForm() {
    setShowAddActor(false);
    setSelectedActorId(null);
    setActorLabel("");
    setActorType("individual");
    setActorNotes("");
  }
```

**2e — Update `addActor()` call:**

```typescript
  async function addActor() {
    if (!selected || !actorLabel.trim()) return;
    try {
      const actor = await api.narratives.addActor(
        selected.id,
        actorLabel.trim(),
        actorType,
        actorNotes.trim() || null,
      );
      setSelected((prev) => prev ? { ...prev, actors: [...prev.actors, actor] } : prev);
      setSelectedActorId(actor.id);
      setShowAddActor(false);
      ...
```

**2f — Update `updateActor()` call:**

```typescript
  async function updateActor() {
    if (!selected || !selectedActorId || !actorLabel.trim()) return;
    try {
      const updated = await api.narratives.updateActor(
        selected.id,
        selectedActorId,
        actorLabel.trim(),
        actorType,
        actorNotes.trim() || null,
      );
```

**2g — Update actor list rendering** (the part that displays actors):

```typescript
              {selected.actors.map((actor) => (
                <div key={actor.id} ...>
                  ...
                  <span title={actor.label}>
                    {actor.label}
                  </span>
                  <span>{ACTOR_TYPE_LABELS[actor.actor_type] ?? actor.actor_type}</span>
```

**2h — Update `ACTOR_TYPE_LABELS` map** (if it exists, update the keys):

Find the `ACTOR_TYPE_LABELS` constant and update keys from German to English type values if needed. Check what keys it uses:

```bash
grep -n "ACTOR_TYPE_LABELS\|figur\|gruppe\|individual\|group" /Users/thormar/klartext/frontend/src/pages/NarrativeEditor.tsx | head -20
```

Update accordingly — keys should match `actor_type` values: `individual`, `organisation`, `group`, `institution`, `abstract_entity`.

**2i — Update all form input bindings** (the JSX input/select elements for the actor form):

Find all `actorName`, `actorTyp`, `actorDescription` references and replace them with `actorLabel`, `actorType`, `actorNotes` respectively.

- [ ] **Step 3: Verify TypeScript compilation**

```bash
cd /Users/thormar/klartext/frontend && npx tsc --noEmit 2>&1
```

Expected: No TypeScript errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/thormar/klartext && git add frontend/src/lib/api.ts frontend/src/pages/NarrativeEditor.tsx
git commit -m "feat: update frontend Actor interface and NarrativeEditor to new label/actor_type/notes API"
```

---

## Task 10: Full Regression Run

- [ ] **Step 1: Run all unit + service tests**

```bash
cd /Users/thormar/klartext/api && python -m pytest \
  tests/test_narrative_domain.py \
  tests/test_claim_domain.py \
  tests/test_narrative_service.py \
  tests/test_narratives_router.py \
  tests/test_scene_claims_router.py \
  tests/test_claim_extractor_service.py \
  tests/test_claude_claim_extraction_provider.py \
  tests/test_seeddata.py \
  -v 2>&1 | tail -30
```

Expected: All PASSED.

- [ ] **Step 2: Run integration tests (requires running local Supabase)**

```bash
cd /Users/thormar/klartext/api && python -m pytest tests/test_narrative_repository.py -v 2>&1 | tail -20
```

Expected: All PASSED.

- [ ] **Step 3: Update `docs/superpowers/plans/PENDING.md`**

Remove Plan B from the PENDING.md document:

```markdown
## Plan B — Actor + Claim Evolution

**Status:** ~~Tests written and RED. Plan not yet written.~~ **DONE** (2026-06-03)
```

Or simply delete the Plan B section from PENDING.md.

- [ ] **Step 4: Final commit**

```bash
cd /Users/thormar/klartext && git add docs/superpowers/plans/PENDING.md
git commit -m "docs: mark Plan B (Actor + Claim Evolution) as complete"
```

---

## Self-Review

### Spec Coverage Check

| Requirement | Task |
|---|---|
| Actor `name → label` | Task 1, 3–9 |
| Actor `typ → actor_type` | Task 1, 3–9 |
| Actor `description → notes` | Task 1, 3–9 |
| Actor `+ entity_ref` | Task 1, 3–9 |
| Claim `+ label` | Task 2, 7–8 |
| Claim `+ ClaimStatus` (DRAFT/LINKED/UNRESOLVED) | Task 2 |
| Claim `+ wirkgefuege_ref` | Task 2, 7–8 |
| Claim `link_to_wirkgefuege()` method | Task 2 |
| Claim `mark_unresolved()` method | Task 2 |
| Schemas updated | Task 5 |
| Service updated | Task 4 |
| Repository updated | Task 6, 7 |
| DB migration | Task 8 |
| Frontend updated | Task 9 |
| Seeddata updated | Task 7 |

All requirements covered. ✅

### Type Consistency Check

- `Actor.create(label=, actor_type=, notes=, entity_ref=)` — used consistently in Tasks 1, 3, 4, 5, 6
- `Actor.from_record({"label":, "actor_type":, "notes":, "entity_ref":})` — used in Tasks 1, 6
- `Actor.update(label=, actor_type=, notes=)` — used in Tasks 1, 4, 5
- `actor.label`, `actor.actor_type`, `actor.notes`, `actor.entity_ref` — consistent throughout
- `Claim.create(label=, text=, typ=, confidence=)` — consistent in Tasks 2, 3, 7
- `Claim.from_record({"label":, ...})` — consistent in Tasks 2, 7
- `ClaimStatus.DRAFT/LINKED/UNRESOLVED` — consistent throughout
