# Wirkgefüge Domain Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full in-memory Wirkgefüge object model (Slot, Zustand, CausalRelation, CausalMixin, CausalModel composite, CausalModelFederation, Scope system, Pre/Postconditions) so all 67 new domain tests turn green.

**Architecture:** All new classes are added to `api/models/causal_model.py` to match existing test imports. The existing `CausalModel`, `Axiom`, and `CausalModelStatus` are preserved and extended backward-compatibly. Scope-related types (TimeSlice, SpatialRegion, Discipline, Scope) and condition types (Precondition, Postcondition) are implemented as simple dataclasses in the same file.

**Tech Stack:** Python 3.12, standard library (`dataclasses`, `enum`, `datetime`, `abc`). No new dependencies.

---

## Design Decisions

### CausalRelation API conflict
`test_causal_relation_domain.py` was written with an ID-based API (`source_slot_id: str`). `test_causal_model_composition.py` uses the canonical object-based API (`source: Slot`). **Resolution:** Task 1 updates `test_causal_relation_domain.py` to use the object-based API. ID-based persistence belongs at the repository layer.

### CausalModel backward compatibility
`CausalModel.create(title)` must keep working. Add `identifier: str | None = None` and `scope: Scope | None = None` as optional params. Existing `add_axiom()` keeps working. All new methods (`add()`, `get_slots()`, etc.) are additive.

### CausalModel.is_complete()
Returns `True` when the model has at least one component AND all components have `epistemic_status != INCOMPLETE`.

### Namespace
Implemented as a plain dict (`dict[str, Any]`) inside each container. No separate `Namespace` class yet (the spec marks it as "still open").

### CausalModelFederation.get_successors()
Model B is a successor of A when `B.scope.temporal.start > A.scope.temporal.end`.

### Postcondition consumption
A postcondition from model N is consumed at model M (immediate successor) when M has a precondition for the same slot identifier with the same state value.

---

## File Map

| File | Action | What changes |
|---|---|---|
| `api/models/causal_model.py` | Modify | Add ~300 lines of new classes |
| `api/exceptions/causal_model.py` | Modify | Add 5 new exception classes |
| `api/tests/test_causal_relation_domain.py` | Modify | Switch from ID-based to object-based API |

Tests that must go green (already written — no new tests needed):
- `tests/test_slot_domain.py` (13 tests)
- `tests/test_causal_relation_domain.py` (11 tests — after API fix in Task 1)
- `tests/test_causal_model_composition.py` (31 tests)
- `tests/test_causal_model_scope.py` (21 tests)
- `tests/test_causal_model_federation.py` (15 tests)

---

## Task 1: Fix CausalRelation test API (design alignment)

**Files:**
- Modify: `api/tests/test_causal_relation_domain.py`

The existing tests use `source_slot_id: str`. Update them to use the canonical object-based API that `test_causal_model_composition.py` already uses.

- [ ] **Step 1.1: Replace test_causal_relation_domain.py with object-based API**

Replace the full content of `api/tests/test_causal_relation_domain.py`:

```python
"""Tests for CausalRelation domain object (persistence-layer representation).

CausalRelation stores references to actual Slot objects. These tests verify
that the basic persistence attributes (id, identifier, epistemic_status) and
factory methods work correctly. Composition behaviour is tested in
test_causal_model_composition.py.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import CausalRelationValidationError
from api.models.causal_model import CausalRelation, EpistemicStatus, Slot, SlotType


def _slot(identifier: str) -> Slot:
    return Slot.create(identifier=identifier, slot_type=SlotType.PHYSICAL_QUANTITY)


def test_causal_relation_create_assigns_identifier() -> None:
    """Expects the identifier to be stored and accessible after creation."""
    relation = CausalRelation.create(
        identifier="co2_causes_warming",
        source=_slot("co2"),
        target=_slot("temperature"),
    )

    assert relation.identifier == "co2_causes_warming"


def test_causal_relation_create_assigns_source_and_target() -> None:
    """Expects source and target Slot objects to be stored by reference."""
    source = _slot("co2")
    target = _slot("temperature")
    relation = CausalRelation.create(identifier="r1", source=source, target=target)

    assert relation.source is source
    assert relation.target is target


def test_causal_relation_create_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    relation = CausalRelation.create(
        identifier="r1", source=_slot("a"), target=_slot("b")
    )

    assert relation.id is None


def test_causal_relation_default_epistemic_status_is_incomplete() -> None:
    """Expects INCOMPLETE as the default — the relation has not yet been formalised."""
    relation = CausalRelation.create(
        identifier="r1", source=_slot("a"), target=_slot("b")
    )

    assert relation.epistemic_status == EpistemicStatus.INCOMPLETE


def test_causal_relation_can_be_created_with_axiomatic_status() -> None:
    """Expects AXIOMATIC to be accepted as an explicit epistemic status at creation."""
    relation = CausalRelation.create(
        identifier="r1",
        source=_slot("a"),
        target=_slot("b"),
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert relation.epistemic_status == EpistemicStatus.AXIOMATIC


def test_causal_relation_mechanism_defaults_to_none() -> None:
    """Expects mechanism to be None when not provided."""
    relation = CausalRelation.create(
        identifier="r1", source=_slot("a"), target=_slot("b")
    )

    assert relation.mechanism is None


def test_causal_relation_create_stores_mechanism() -> None:
    """Expects mechanism to be stored when provided."""
    relation = CausalRelation.create(
        identifier="r1",
        source=_slot("a"),
        target=_slot("b"),
        mechanism="Greenhouse effect",
    )

    assert relation.mechanism == "Greenhouse effect"


def test_causal_relation_from_record_reconstructs_all_fields() -> None:
    """Expects all fields including id to be restored when given actual Slot objects."""
    source = _slot("co2")
    target = _slot("temperature")
    record = {
        "id": "cr-001",
        "identifier": "co2_causes_warming",
        "source": source,
        "target": target,
        "mechanism": "Greenhouse effect",
        "epistemic_status": "incomplete",
    }

    relation = CausalRelation.from_record(record)

    assert relation.id == "cr-001"
    assert relation.identifier == "co2_causes_warming"
    assert relation.source is source
    assert relation.mechanism == "Greenhouse effect"
    assert relation.epistemic_status == EpistemicStatus.INCOMPLETE


def test_causal_relation_from_record_handles_null_mechanism() -> None:
    """Expects mechanism to be None when the record contains null."""
    record = {
        "id": "cr-002",
        "identifier": "r1",
        "source": _slot("a"),
        "target": _slot("b"),
        "mechanism": None,
        "epistemic_status": "incomplete",
    }

    relation = CausalRelation.from_record(record)

    assert relation.mechanism is None


def test_causal_relation_create_raises_for_empty_identifier() -> None:
    """Expects CausalRelationValidationError when identifier is empty."""
    with pytest.raises(CausalRelationValidationError):
        CausalRelation.create(identifier="", source=_slot("a"), target=_slot("b"))


def test_causal_relation_create_raises_when_source_equals_target() -> None:
    """Expects CausalRelationValidationError — a slot cannot cause itself."""
    slot = _slot("same")
    with pytest.raises(CausalRelationValidationError):
        CausalRelation.create(identifier="self_loop", source=slot, target=slot)
```

- [ ] **Step 1.2: Verify the tests still fail (implementation missing)**

```bash
cd api && python3.12 -m pytest tests/test_causal_relation_domain.py -q --tb=line 2>&1 | head -5
```
Expected: `ImportError` or `AttributeError` — `EpistemicStatus`, `Slot` etc. don't exist yet.

- [ ] **Step 1.3: Commit**

```bash
git add api/tests/test_causal_relation_domain.py
git commit -m "fix(tests): align CausalRelation tests with object-based domain API"
```

---

## Task 2: New exception classes

**Files:**
- Modify: `api/exceptions/causal_model.py`

- [ ] **Step 2.1: Add five new exception classes**

Replace `api/exceptions/causal_model.py` with:

```python
"""Exceptions for the CausalModel domain, service and repository layers."""

from __future__ import annotations

from api.exceptions.base import DomainError, RepositoryError


class CausalModelValidationError(DomainError):
    """Raised by CausalModel or Axiom when invariants are violated."""


class AxiomValidationError(DomainError):
    """Raised by Axiom when invariants are violated."""


class SlotValidationError(DomainError):
    """Raised by Slot when invariants are violated (empty identifier, unknown type)."""


class CausalRelationValidationError(DomainError):
    """Raised by CausalRelation or DefinitoryRelation when invariants are violated."""


class NamespaceConflictError(DomainError):
    """Raised by CausalModel or CausalMixin when an identifier is already in use."""


class ScopeConflictError(DomainError):
    """Raised by CausalModel.add() when a component scope is incompatible with the model scope."""


class ConditionConflictError(DomainError):
    """Raised when two conditions on the same Slot require incompatible states."""


class CausalModelNotFoundError(RepositoryError):
    """Raised by CausalModelRepository when no CausalModel exists for the given ID."""


class CausalModelPersistenceError(RepositoryError):
    """Raised by CausalModelRepository when a database operation fails."""
```

- [ ] **Step 2.2: Run affected tests**

```bash
cd api && python3.12 -m pytest tests/test_slot_domain.py tests/test_causal_relation_domain.py -q --tb=line 2>&1 | head -8
```
Expected: still `ImportError` for `Slot`, `EpistemicStatus` — exceptions exist now.

- [ ] **Step 2.3: Commit**

```bash
git add api/exceptions/causal_model.py
git commit -m "feat(domain): add Slot, CausalRelation, Namespace and Scope exception classes"
```

---

## Task 3: EpistemicStatus, SlotType, Polarity enums

**Files:**
- Modify: `api/models/causal_model.py` (prepend after imports)

- [ ] **Step 3.1: Add enums at the top of causal_model.py (after existing imports)**

Add after `from __future__ import annotations` and before `class CausalModelStatus`:

```python
from datetime import date
from abc import ABC
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EpistemicStatus(StrEnum):
    """Transparency status of a CausalComponent.

    INCOMPLETE: default — element not yet formalised.
    AXIOMATIC: set as a premise; not derived within this model.
    DERIVED is a computed property (derivation_source is not None), not a stored value.
    """

    INCOMPLETE = "incomplete"
    AXIOMATIC = "axiomatic"


class SlotType(StrEnum):
    """Semantic category of a Slot — determines which Zustand values are valid."""

    PHYSICAL_QUANTITY = "physical_quantity"
    SOCIAL_QUANTITY = "social_quantity"
    ENTITY_STATE = "entity_state"
    TREND = "trend"
    PROCESS = "process"


class Polarity(StrEnum):
    """Direction of a causal effect."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    AMBIVALENT = "ambivalent"
```

- [ ] **Step 3.2: Run enum tests**

```bash
cd api && python3.12 -m pytest tests/test_slot_domain.py::test_epistemic_status_has_incomplete_and_axiomatic tests/test_slot_domain.py::test_slot_type_covers_expected_variants -v 2>&1 | tail -6
```
Expected: PASS for both enum tests.

- [ ] **Step 3.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add EpistemicStatus, SlotType and Polarity enums"
```

---

## Task 4: Slot and Entity classes

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 4.1: Add Slot class after the new enums**

```python
class Slot:
    """A named placeholder for an observable or measurable value in the Wirkgefüge.

    Invariants enforced at construction time:
    - identifier must not be empty
    """

    def __init__(
        self,
        id: str | None,
        identifier: str,
        slot_type: SlotType,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
        scope: "Scope | None" = None,
    ) -> None:
        self._id = id
        self._identifier = identifier
        self._slot_type = slot_type
        self._epistemic_status = epistemic_status
        self._scope = scope

    @classmethod
    def create(
        cls,
        identifier: str,
        slot_type: SlotType,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
        scope: "Scope | None" = None,
    ) -> "Slot":
        """Creates a new Slot. Raises SlotValidationError for empty identifier."""
        if not identifier.strip():
            raise SlotValidationError("identifier must not be empty")
        return cls(id=None, identifier=identifier, slot_type=slot_type,
                   epistemic_status=epistemic_status, scope=scope)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Slot":
        """Reconstructs a Slot from a database record.

        Raises SlotValidationError for an unrecognised slot_type.
        """
        try:
            slot_type = SlotType(record["slot_type"])
        except ValueError as e:
            raise SlotValidationError(
                f"Unknown slot type in record: {record['slot_type']}"
            ) from e
        return cls(
            id=record["id"],
            identifier=record["identifier"],
            slot_type=slot_type,
            epistemic_status=EpistemicStatus(record.get("epistemic_status", "incomplete")),
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def slot_type(self) -> SlotType:
        return self._slot_type

    @property
    def epistemic_status(self) -> EpistemicStatus:
        return self._epistemic_status

    @property
    def scope(self) -> "Scope | None":
        return self._scope

    @property
    def is_axiomatic(self) -> bool:
        """True when this element is set as a premise in the current model."""
        return self._epistemic_status == EpistemicStatus.AXIOMATIC


class Entity(Slot):
    """A Slot representing an actor with agency (organisation, institution, group).

    States describe capacity or status ('active', 'dissolved'), not measurements.
    """

    @classmethod
    def create(  # type: ignore[override]
        cls,
        identifier: str,
        slot_type: SlotType = SlotType.ENTITY_STATE,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
        scope: "Scope | None" = None,
    ) -> "Entity":
        """Creates a new Entity. Raises SlotValidationError for empty identifier."""
        if not identifier.strip():
            raise SlotValidationError("identifier must not be empty")
        return cls(id=None, identifier=identifier, slot_type=slot_type,
                   epistemic_status=epistemic_status, scope=scope)
```

- [ ] **Step 4.2: Run Slot tests**

```bash
cd api && python3.12 -m pytest tests/test_slot_domain.py -v 2>&1 | tail -20
```
Expected: all 13 tests PASS.

- [ ] **Step 4.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add Slot and Entity domain classes with EpistemicStatus"
```

---

## Task 5: Zustand class

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 5.1: Add Zustand after Entity**

```python
class Zustand:
    """A concrete value of a Slot at a point in time or within a Scope.

    Zustand is NOT a CausalComponent — it exists relative to a Slot and is not
    placed directly in a CausalModel's component list.
    """

    def __init__(
        self,
        value: str | float | int,
        slot: Slot,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> None:
        self._value = value
        self._slot = slot
        self._epistemic_status = epistemic_status

    @classmethod
    def create(
        cls,
        value: str | float | int,
        slot: Slot,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> "Zustand":
        """Creates a new Zustand for the given Slot."""
        return cls(value=value, slot=slot, epistemic_status=epistemic_status)

    @property
    def value(self) -> str | float | int:
        return self._value

    @property
    def slot(self) -> Slot:
        return self._slot

    @property
    def epistemic_status(self) -> EpistemicStatus:
        return self._epistemic_status
```

- [ ] **Step 5.2: Run Zustand tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_composition.py::test_zustand_create_stores_value_and_slot tests/test_causal_model_composition.py::test_zustand_numeric_value_is_stored tests/test_causal_model_composition.py::test_zustand_can_be_created_axiomatic -v 2>&1 | tail -8
```
Expected: all 3 PASS.

- [ ] **Step 5.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add Zustand as a value-relative-to-Slot class"
```

---

## Task 6: CausalRelation and DefinitoryRelation

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 6.1: Add CausalRelation and DefinitoryRelation after Zustand**

```python
class CausalRelation:
    """A directed causal link between two Slots.

    Invariants:
    - identifier must not be empty
    - source and target must be different Slot objects
    """

    def __init__(
        self,
        id: str | None,
        identifier: str,
        source: Slot,
        target: Slot,
        mechanism: str | None = None,
        polarity: Polarity | None = None,
        strength: float | None = None,
        uncertainty: float | None = None,
        source_condition: Zustand | None = None,
        target_effect: Zustand | None = None,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
        preconditions: list["Precondition"] | None = None,
    ) -> None:
        self._id = id
        self._identifier = identifier
        self._source = source
        self._target = target
        self._mechanism = mechanism
        self._polarity = polarity
        self._strength = strength
        self._uncertainty = uncertainty
        self._source_condition = source_condition
        self._target_effect = target_effect
        self._epistemic_status = epistemic_status
        self.preconditions: list["Precondition"] = preconditions or []

    @classmethod
    def create(
        cls,
        identifier: str,
        source: Slot,
        target: Slot,
        mechanism: str | None = None,
        polarity: Polarity | None = None,
        source_condition: Zustand | None = None,
        target_effect: Zustand | None = None,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> "CausalRelation":
        """Creates a CausalRelation.

        Raises CausalRelationValidationError for empty identifier or self-loop.
        """
        if not identifier.strip():
            raise CausalRelationValidationError("identifier must not be empty")
        if source is target:
            raise CausalRelationValidationError(
                f"CausalRelation '{identifier}': source and target must be different Slots"
            )
        return cls(
            id=None,
            identifier=identifier,
            source=source,
            target=target,
            mechanism=mechanism,
            polarity=polarity,
            source_condition=source_condition,
            target_effect=target_effect,
            epistemic_status=epistemic_status,
        )

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "CausalRelation":
        """Reconstructs a CausalRelation from a record that contains Slot objects."""
        return cls(
            id=record["id"],
            identifier=record["identifier"],
            source=record["source"],
            target=record["target"],
            mechanism=record.get("mechanism"),
            epistemic_status=EpistemicStatus(
                record.get("epistemic_status", "incomplete")
            ),
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def source(self) -> Slot:
        return self._source

    @property
    def target(self) -> Slot:
        return self._target

    @property
    def mechanism(self) -> str | None:
        return self._mechanism

    @property
    def polarity(self) -> Polarity | None:
        return self._polarity

    @property
    def source_condition(self) -> Zustand | None:
        return self._source_condition

    @property
    def target_effect(self) -> Zustand | None:
        return self._target_effect

    @property
    def epistemic_status(self) -> EpistemicStatus:
        return self._epistemic_status

    @property
    def is_axiomatic(self) -> bool:
        return self._epistemic_status == EpistemicStatus.AXIOMATIC


class DefinitoryRelation:
    """A conceptual equivalence relation — describes what a Slot means, not what it causes.

    Invariants:
    - identifier must not be empty
    - source and target must be different Slot objects
    """

    def __init__(
        self,
        id: str | None,
        identifier: str,
        source: Slot,
        target: Slot,
        definition: str,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> None:
        self._id = id
        self._identifier = identifier
        self._source = source
        self._target = target
        self._definition = definition
        self._epistemic_status = epistemic_status

    @classmethod
    def create(
        cls,
        identifier: str,
        source: Slot,
        target: Slot,
        definition: str,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
    ) -> "DefinitoryRelation":
        """Creates a DefinitoryRelation.

        Raises CausalRelationValidationError for empty identifier or self-reference.
        """
        if not identifier.strip():
            raise CausalRelationValidationError("identifier must not be empty")
        if source is target:
            raise CausalRelationValidationError(
                f"DefinitoryRelation '{identifier}': a Slot cannot define itself"
            )
        return cls(id=None, identifier=identifier, source=source, target=target,
                   definition=definition, epistemic_status=epistemic_status)

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def source(self) -> Slot:
        return self._source

    @property
    def target(self) -> Slot:
        return self._target

    @property
    def definition(self) -> str:
        return self._definition

    @property
    def epistemic_status(self) -> EpistemicStatus:
        return self._epistemic_status

    @property
    def is_axiomatic(self) -> bool:
        return self._epistemic_status == EpistemicStatus.AXIOMATIC
```

- [ ] **Step 6.2: Run CausalRelation tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_relation_domain.py tests/test_causal_model_composition.py -k "relation" -v 2>&1 | tail -20
```
Expected: all relation tests PASS.

- [ ] **Step 6.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add CausalRelation and DefinitoryRelation domain classes"
```

---

## Task 7: Scope system (TimeSlice, SpatialRegion, Discipline, Scope)

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 7.1: Add scope types after DefinitoryRelation**

```python
@dataclass
class TimeSlice:
    """A bounded time interval. Identifies a temporal scope for a CausalModel or component."""

    start: date
    end: date
    identifier: str = ""

    def __post_init__(self) -> None:
        if not self.identifier:
            self.identifier = f"{self.start.year}-{self.end.year}"

    def includes(self, other: "TimeSlice") -> bool:
        """True if *other* lies entirely within this slice (start and end both contained)."""
        return self.start <= other.start and other.end <= self.end

    def intersects(self, other: "TimeSlice") -> bool:
        """True if the two slices share any common period."""
        return self.start <= other.end and other.start <= self.end


@dataclass
class SpatialRegion:
    """A node in a spatial hierarchy (e.g. europe → germany → bavaria)."""

    identifier: str
    parent: "SpatialRegion | None" = None

    def includes(self, other: "SpatialRegion") -> bool:
        """True if *other* is this region or any descendant in the hierarchy."""
        current: SpatialRegion | None = other
        while current is not None:
            if current.identifier == self.identifier:
                return True
            current = current.parent
        return False


@dataclass
class Discipline:
    """A node in an academic discipline hierarchy (e.g. natural_science → climate_science)."""

    identifier: str
    parent: "Discipline | None" = None

    def includes(self, other: "Discipline") -> bool:
        """True if *other* is this discipline or any sub-discipline."""
        current: Discipline | None = other
        while current is not None:
            if current.identifier == self.identifier:
                return True
            current = current.parent
        return False


@dataclass
class Scope:
    """The validity boundary of a CausalComponent across three orthogonal dimensions.

    None on a dimension means INCOMPLETE (not 'universal').
    """

    temporal: TimeSlice | None = None
    spatial: SpatialRegion | None = None
    disciplinary: Discipline | None = None

    def includes(self, other: "Scope") -> bool:
        """True when *other* lies entirely within this scope.

        Used by CausalModel.add() to check component–container compatibility.
        A missing dimension (None) is not a blocker — it skips that check.
        """
        if self.temporal is not None and other.temporal is not None:
            if not self.temporal.includes(other.temporal):
                return False
        if self.spatial is not None and other.spatial is not None:
            if not self.spatial.includes(other.spatial):
                return False
        if self.disciplinary is not None and other.disciplinary is not None:
            if not self.disciplinary.includes(other.disciplinary):
                return False
        return True

    def is_compatible(self, other: "Scope") -> bool:
        """True when the two scopes overlap in the temporal dimension.

        Used for conflict detection — two elements conflict only when their
        scopes intersect in all defined dimensions.
        """
        if self.temporal is not None and other.temporal is not None:
            return self.temporal.intersects(other.temporal)
        return True

    def is_complete(self) -> bool:
        """True when all three dimensions are set."""
        return (
            self.temporal is not None
            and self.spatial is not None
            and self.disciplinary is not None
        )
```

- [ ] **Step 7.2: Run scope tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_scope.py -v 2>&1 | tail -25
```
Expected: all 21 tests PASS except the CausalModel.add() scope tests (CausalModel not fully implemented yet).

- [ ] **Step 7.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add TimeSlice, SpatialRegion, Discipline and Scope classes"
```

---

## Task 8: Condition, Precondition, Postcondition, ConditionConflict

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 8.1: Add condition types after Scope**

```python
class Condition:
    """Abstract base for Precondition and Postcondition.

    A condition describes the required or expected state of a Slot.
    Two conditions are incompatible when they address the same Slot but require
    different state values.
    """

    def __init__(self, slot: Slot, state: Zustand, scope: Scope) -> None:
        self.slot = slot
        self.state = state
        self.scope = scope

    def is_compatible_with(self, other: "Condition") -> bool:
        """True when the two conditions can coexist without contradiction.

        Conditions on different Slots are always compatible.
        Conditions on the same Slot are compatible only when they agree on the value.
        """
        if self.slot.identifier != other.slot.identifier:
            return True
        return str(self.state.value) == str(other.state.value)


class Precondition(Condition):
    """A condition that must hold before a CausalRelation or CausalModel transition is valid."""


class Postcondition(Condition):
    """A condition expected to hold after a CausalModel's time period ends.

    Propagates forward to successor models until consumed by a compatible Precondition.
    """


@dataclass
class ConditionConflict:
    """Describes a conflict between a Postcondition from a predecessor and a Precondition
    in the successor model on the same Slot."""

    postcondition: Postcondition
    precondition: Precondition
```

- [ ] **Step 8.2: Run condition tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_federation.py -k "condition" -v 2>&1 | tail -15
```
Expected: precondition/postcondition basic tests PASS. Federation tests still fail (CausalModelFederation not implemented yet).

- [ ] **Step 8.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add Condition, Precondition, Postcondition and ConditionConflict"
```

---

## Task 9: CausalMixin

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 9.1: Add CausalMixin after ConditionConflict**

```python
# Type alias for anything that can be added to a composite
_Component = Slot | CausalRelation | DefinitoryRelation


class CausalMixin:
    """A reusable, potentially incomplete fragment of a CausalModel.

    Can be applied to a CausalModel or another CausalMixin via applies().
    Elements from applied mixins are accessible via get_slots() and
    get_relations() but can be shadowed by own definitions.
    """

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self._components: list[_Component] = []
        self._applied_mixins: list["CausalMixin"] = []

    @classmethod
    def create(cls, identifier: str) -> "CausalMixin":
        """Creates a new empty CausalMixin."""
        return cls(identifier=identifier)

    def add(self, component: _Component) -> None:
        """Adds a component to this mixin.

        Raises NamespaceConflictError if the identifier is already in use.
        """
        own_ids = {c.identifier for c in self._components}
        if component.identifier in own_ids:
            raise NamespaceConflictError(
                f"Identifier '{component.identifier}' already exists in '{self.identifier}'"
            )
        self._components.append(component)

    def applies(self, mixin: "CausalMixin") -> None:
        """Includes a CausalMixin's elements in this container.

        Raises NamespaceConflictError when two applied mixins introduce the same
        identifier and no own definition shadows it.
        """
        own_ids = {c.identifier for c in self._components}
        new_ids = {c.identifier for c in mixin.get_slots() + mixin.get_relations()}

        for existing_mixin in self._applied_mixins:
            existing_ids = {
                c.identifier
                for c in existing_mixin.get_slots() + existing_mixin.get_relations()
            }
            collisions = new_ids & existing_ids - own_ids
            if collisions:
                raise NamespaceConflictError(
                    f"Identifier(s) {collisions} already introduced by mixin "
                    f"'{existing_mixin.identifier}' and not overridden by '{self.identifier}'"
                )
        self._applied_mixins.append(mixin)

    def get_slots(self) -> list[Slot]:
        """Returns all Slots — own first, then from applied mixins (shadowed by own)."""
        own_ids = {c.identifier for c in self._components if isinstance(c, Slot)}
        result: list[Slot] = [c for c in self._components if isinstance(c, Slot)]
        for mixin in self._applied_mixins:
            for slot in mixin.get_slots():
                if slot.identifier not in own_ids:
                    result.append(slot)
        return result

    def get_relations(self) -> list[CausalRelation | DefinitoryRelation]:
        """Returns all Relations — own first, then from applied mixins (shadowed by own)."""
        own_ids = {
            c.identifier
            for c in self._components
            if isinstance(c, (CausalRelation, DefinitoryRelation))
        }
        result: list[CausalRelation | DefinitoryRelation] = [
            c for c in self._components if isinstance(c, (CausalRelation, DefinitoryRelation))
        ]
        for mixin in self._applied_mixins:
            for rel in mixin.get_relations():
                if rel.identifier not in own_ids:
                    result.append(rel)
        return result
```

- [ ] **Step 9.2: Run mixin tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_composition.py -k "mixin" -v 2>&1 | tail -15
```
Expected: all mixin tests PASS (CausalModel.applies() tests still need CausalModel update).

- [ ] **Step 9.3: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add CausalMixin with applies, get_slots and get_relations"
```

---

## Task 10: Extend CausalModel with composite behaviour

**Files:**
- Modify: `api/models/causal_model.py`

The existing `CausalModel` class needs new attributes and methods while keeping backward compatibility. Add `identifier`, `scope`, `components`, `preconditions`, `postconditions` and all composite methods.

- [ ] **Step 10.1: Update CausalModel.__init__ and create()**

Replace the existing `CausalModel` class (keep Axiom and CausalModelStatus above):

```python
class CausalModel(CausalMixin):
    """A formal, versionable causal model — the top-level Wirkgefüge container.

    Extends CausalMixin with scope, preconditions, postconditions, and a
    scope-enforcing add().

    Backward compatibility: CausalModel.create(title=...) still works.
    add_axiom() still works. The new composite API is additive.
    """

    def __init__(
        self,
        id: str | None,
        title: str,
        identifier: str | None = None,
        status: CausalModelStatus = CausalModelStatus.PRIVATE,
        scope: Scope | None = None,
    ) -> None:
        super().__init__(identifier=identifier or title)
        self._id = id
        self._title = title
        self._status = status
        self._scope = scope
        self._axioms: list[Axiom] = []
        self.preconditions: list[Precondition] = []
        self.postconditions: list[Postcondition] = []

    @classmethod
    def create(  # type: ignore[override]
        cls,
        title: str,
        identifier: str | None = None,
        scope: Scope | None = None,
        status: CausalModelStatus = CausalModelStatus.PRIVATE,
    ) -> "CausalModel":
        """Creates a new CausalModel.

        Raises CausalModelValidationError for empty title.
        """
        if not title.strip():
            raise CausalModelValidationError("title must not be empty")
        return cls(id=None, title=title, identifier=identifier, scope=scope, status=status)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "CausalModel":
        """Reconstructs a CausalModel from a database record."""
        return cls(
            id=record["id"],
            title=record["title"],
            status=CausalModelStatus(record["status"]),
        )

    def add(self, component: _Component) -> None:  # type: ignore[override]
        """Adds a component, enforcing namespace uniqueness and scope compatibility.

        Raises NamespaceConflictError when the identifier is already in use.
        Raises ScopeConflictError when the component scope is not compatible with
        the model scope (both defined and non-overlapping).
        """
        if self._scope is not None and component.scope is not None:
            if not self._scope.includes(component.scope):
                raise ScopeConflictError(
                    f"Component '{component.identifier}' scope is incompatible "
                    f"with model '{self.identifier}' scope"
                )
        super().add(component)

    def add_axiom(self, axiom: Axiom) -> None:
        """Backward-compatible: appends an Axiom.

        Axioms are stored separately and do not participate in namespace or
        scope enforcement.
        """
        self._axioms.append(axiom)

    def axiomatic_space(self) -> list[_Component]:
        """Returns all components with epistemic_status == AXIOMATIC."""
        return [
            c for c in self.get_slots() + self.get_relations()
            if c.is_axiomatic
        ]

    def is_complete(self) -> bool:
        """True when the model has at least one component and none are INCOMPLETE."""
        all_components = self.get_slots() + self.get_relations()
        if not all_components:
            return False
        return all(c.is_axiomatic or c.epistemic_status != EpistemicStatus.INCOMPLETE
                   for c in all_components)

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> CausalModelStatus:
        return self._status

    @property
    def scope(self) -> Scope | None:
        return self._scope

    @scope.setter
    def scope(self, value: Scope | None) -> None:
        self._scope = value

    @property
    def axioms(self) -> list[Axiom]:
        return self._axioms
```

- [ ] **Step 10.2: Run all composition and scope tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_composition.py tests/test_causal_model_scope.py -v 2>&1 | tail -15
```
Expected: all 52 tests PASS.

- [ ] **Step 10.3: Verify existing CausalModel tests still pass**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_domain.py tests/test_causal_model_service.py tests/test_causal_model_router.py -v 2>&1 | tail -10
```
Expected: all existing tests PASS (backward compat preserved).

- [ ] **Step 10.4: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): extend CausalModel with composite add, traversal and is_complete"
```

---

## Task 11: CausalModelFederation

**Files:**
- Modify: `api/models/causal_model.py`

- [ ] **Step 11.1: Add CausalModelFederation after CausalModel**

```python
class CausalModelFederation:
    """Chains multiple CausalModels (time slices) and manages Postcondition propagation.

    Successor detection: Model B is a successor of A when
    B.scope.temporal.start > A.scope.temporal.end.

    Postcondition propagation: a Postcondition from model N propagates forward
    until consumed by a compatible Precondition in a successor model.
    """

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self._models: list[CausalModel] = []

    @classmethod
    def create(cls, identifier: str) -> "CausalModelFederation":
        """Creates a new empty CausalModelFederation."""
        return cls(identifier=identifier)

    def add_model(self, model: CausalModel) -> None:
        """Registers a CausalModel as a member of this federation."""
        self._models.append(model)

    def get_successors(self, model: CausalModel) -> list[CausalModel]:
        """Returns all models whose temporal start is after model's temporal end."""
        if model.scope is None or model.scope.temporal is None:
            return []
        model_end = model.scope.temporal.end
        return [
            m for m in self._models
            if m is not model
            and m.scope is not None
            and m.scope.temporal is not None
            and m.scope.temporal.start > model_end
        ]

    def validate_transition(
        self, predecessor: CausalModel, successor: CausalModel
    ) -> list[ConditionConflict]:
        """Checks each Postcondition from predecessor against each Precondition
        in successor. Returns a ConditionConflict for every incompatible pair."""
        conflicts: list[ConditionConflict] = []
        for postcond in predecessor.postconditions:
            for precond in successor.preconditions:
                if postcond.slot.identifier == precond.slot.identifier:
                    if not postcond.is_compatible_with(precond):
                        conflicts.append(
                            ConditionConflict(
                                postcondition=postcond, precondition=precond
                            )
                        )
        return conflicts

    def get_active_postconditions(self, model: CausalModel) -> list[Postcondition]:
        """Returns all Postconditions that propagate into *model* from any predecessor.

        A Postcondition is consumed (not active) if any model between its origin
        and *model* has a compatible Precondition for the same Slot.
        """
        if model.scope is None or model.scope.temporal is None:
            return []

        active: list[Postcondition] = []
        for other in self._models:
            if other is model:
                continue
            if other.scope is None or other.scope.temporal is None:
                continue
            if other.scope.temporal.end >= model.scope.temporal.start:
                continue  # not a predecessor

            for postcond in other.postconditions:
                if not self._is_consumed_before(postcond, other, model):
                    active.append(postcond)
        return active

    def _is_consumed_before(
        self,
        postcond: Postcondition,
        origin: CausalModel,
        target: CausalModel,
    ) -> bool:
        """True if any model between origin and target consumes postcond."""
        if origin.scope is None or target.scope is None:
            return False
        for inter in self._models:
            if inter is origin or inter is target:
                continue
            if inter.scope is None or inter.scope.temporal is None:
                continue
            # intermediate: starts after origin ends, ends before target starts
            if not (
                inter.scope.temporal.start > origin.scope.temporal.end
                and inter.scope.temporal.end < target.scope.temporal.start
            ):
                continue
            for precond in inter.preconditions:
                if (
                    precond.slot.identifier == postcond.slot.identifier
                    and postcond.is_compatible_with(precond)
                ):
                    return True
        # also check target itself for direct consumption check in get_active
        return False
```

- [ ] **Step 11.2: Run all federation tests**

```bash
cd api && python3.12 -m pytest tests/test_causal_model_federation.py -v 2>&1 | tail -20
```
Expected: all 15 tests PASS.

- [ ] **Step 11.3: Run the full test suite to confirm nothing broke**

```bash
cd api && python3.12 -m pytest tests/ -q --tb=short 2>&1 | tail -8
```
Expected: all tests PASS (including existing `test_causal_model_domain.py`, `test_causal_model_service.py`, `test_causal_model_router.py`).

- [ ] **Step 11.4: Commit**

```bash
git add api/models/causal_model.py
git commit -m "feat(domain): add CausalModelFederation with successor detection and postcondition propagation"
```

---

## Final verification

- [ ] **Run all new domain tests in one pass**

```bash
cd api && python3.12 -m pytest \
  tests/test_slot_domain.py \
  tests/test_causal_relation_domain.py \
  tests/test_causal_model_composition.py \
  tests/test_causal_model_scope.py \
  tests/test_causal_model_federation.py \
  -v 2>&1 | tail -20
```
Expected: 67 tests, all PASS.

- [ ] **Run full test suite**

```bash
cd api && python3.12 -m pytest tests/ -q 2>&1 | tail -5
```
Expected: all tests PASS, no regressions.

- [ ] **Push**

```bash
git push
```

---

## What this plan does NOT cover

The following are separate plans:

- **Plan B — Actor + Claim Evolution**: `name→label`, `typ→actor_type`, `description→notes`, `+entity_ref` on Actor; `ClaimStatus`, `label`, `wirkgefuege_ref` on Claim; DB migrations; all downstream layers.
- **Plan C — Wirkgefüge Persistence**: `slots` + `causal_relations` DB tables, Supabase repositories, Pydantic schemas, router endpoints for `POST /causal-models/{id}/slots` etc.
- **Plan D — Analysis Workflow**: `NarrativeAnalysisService`, `WirkgefuegeSuggestionService`, `POST /narratives/{id}/analyse`, `POST /narratives/{id}/suggest-wirkgefuege`.
