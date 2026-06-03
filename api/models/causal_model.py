"""Domain objects for CausalModels and their Axioms."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any

from api.exceptions.causal_model import (
    AxiomValidationError,
    CausalModelValidationError,
    CausalRelationValidationError,
    NamespaceConflictError,
    SlotValidationError,
)

# ── Enums ──────────────────────────────────────────────────────────────────


class EpistemicStatus(StrEnum):
    """Transparency status of a CausalComponent.

    INCOMPLETE: default — element not yet formalised.
    AXIOMATIC: set as a premise; not derived within this model.
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


# ── Slot and Entity ────────────────────────────────────────────────────────


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
        scope: Scope | None = None,
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
        scope: Scope | None = None,
    ) -> Slot:
        """Creates a new Slot. Raises SlotValidationError for empty identifier."""
        if not identifier.strip():
            raise SlotValidationError("identifier must not be empty")
        return cls(
            id=None,
            identifier=identifier,
            slot_type=slot_type,
            epistemic_status=epistemic_status,
            scope=scope,
        )

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Slot:
        """Reconstructs a Slot from a database record.

        Raises SlotValidationError for an unrecognised slot_type.
        """
        try:
            slot_type = SlotType(record["slot_type"])
        except ValueError as e:
            raise SlotValidationError(f"Unknown slot type in record: {record['slot_type']}") from e
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
    def scope(self) -> Scope | None:
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
    def create(
        cls,
        identifier: str,
        slot_type: SlotType = SlotType.ENTITY_STATE,
        epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE,
        scope: Scope | None = None,
    ) -> Entity:
        """Creates a new Entity. Raises SlotValidationError for empty identifier."""
        if not identifier.strip():
            raise SlotValidationError("identifier must not be empty")
        return cls(
            id=None,
            identifier=identifier,
            slot_type=slot_type,
            epistemic_status=epistemic_status,
            scope=scope,
        )


# ── Zustand ────────────────────────────────────────────────────────────────


class Zustand:
    """A concrete value of a Slot at a point in time or within a Scope.

    Not a CausalComponent — exists relative to a Slot and is not placed
    directly in a CausalModel's component list.
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
    ) -> Zustand:
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


# ── Relations ──────────────────────────────────────────────────────────────


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
        preconditions: list[Precondition] | None = None,
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
        self.preconditions: list[Precondition] = preconditions or []

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
    ) -> CausalRelation:
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
    def from_record(cls, record: dict[str, Any]) -> CausalRelation:
        """Reconstructs a CausalRelation from a record that contains Slot objects."""
        return cls(
            id=record["id"],
            identifier=record["identifier"],
            source=record["source"],
            target=record["target"],
            mechanism=record.get("mechanism"),
            epistemic_status=EpistemicStatus(record.get("epistemic_status", "incomplete")),
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
    ) -> DefinitoryRelation:
        """Creates a DefinitoryRelation.

        Raises CausalRelationValidationError for empty identifier or self-reference.
        """
        if not identifier.strip():
            raise CausalRelationValidationError("identifier must not be empty")
        if source is target:
            raise CausalRelationValidationError(
                f"DefinitoryRelation '{identifier}': a Slot cannot define itself"
            )
        return cls(
            id=None,
            identifier=identifier,
            source=source,
            target=target,
            definition=definition,
            epistemic_status=epistemic_status,
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
    def definition(self) -> str:
        return self._definition

    @property
    def epistemic_status(self) -> EpistemicStatus:
        return self._epistemic_status

    @property
    def is_axiomatic(self) -> bool:
        return self._epistemic_status == EpistemicStatus.AXIOMATIC


# ── Scope system ───────────────────────────────────────────────────────────


@dataclass
class TimeSlice:
    """A bounded time interval for temporal scoping."""

    start: date
    end: date
    identifier: str = ""

    def __post_init__(self) -> None:
        """Sets a default identifier from start/end years when none is given."""
        if not self.identifier:
            self.identifier = f"{self.start.year}-{self.end.year}"

    def includes(self, other: TimeSlice) -> bool:
        """True if *other* lies entirely within this slice."""
        return self.start <= other.start and other.end <= self.end

    def intersects(self, other: TimeSlice) -> bool:
        """True if the two slices share any common period."""
        return self.start <= other.end and other.start <= self.end


@dataclass
class SpatialRegion:
    """A node in a spatial hierarchy (e.g. europe → germany → bavaria)."""

    identifier: str
    parent: SpatialRegion | None = None

    def includes(self, other: SpatialRegion) -> bool:
        """True if *other* is this region or any descendant."""
        current: SpatialRegion | None = other
        while current is not None:
            if current.identifier == self.identifier:
                return True
            current = current.parent
        return False


@dataclass
class Discipline:
    """A node in an academic discipline hierarchy."""

    identifier: str
    parent: Discipline | None = None

    def includes(self, other: Discipline) -> bool:
        """True if *other* is this discipline or any sub-discipline."""
        current: Discipline | None = other
        while current is not None:
            if current.identifier == self.identifier:
                return True
            current = current.parent
        return False


@dataclass
class Scope:
    """Validity boundary of a CausalComponent across three orthogonal dimensions."""

    temporal: TimeSlice | None = None
    spatial: SpatialRegion | None = None
    disciplinary: Discipline | None = None

    def includes(self, other: Scope) -> bool:
        """True when *other* lies entirely within this scope (used by add())."""
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

    def is_compatible(self, other: Scope) -> bool:
        """True when the two scopes overlap in the temporal dimension."""
        if self.temporal is not None and other.temporal is not None:
            return self.temporal.intersects(other.temporal)
        return True

    def is_complete(self) -> bool:
        """True when all three dimensions are set."""
        return (
            self.temporal is not None and self.spatial is not None and self.disciplinary is not None
        )


# ── Conditions ─────────────────────────────────────────────────────────────


class Condition:
    """Base for Precondition and Postcondition.

    Two conditions are incompatible when they address the same Slot but require
    different state values.
    """

    def __init__(self, slot: Slot, state: Zustand, scope: Scope) -> None:
        self.slot = slot
        self.state = state
        self.scope = scope

    def is_compatible_with(self, other: Condition) -> bool:
        """True when the two conditions can coexist without contradiction."""
        if self.slot.identifier != other.slot.identifier:
            return True
        return str(self.state.value) == str(other.state.value)


class Precondition(Condition):
    """A condition that must hold before a CausalRelation or model transition is valid."""


class Postcondition(Condition):
    """A condition expected to hold after a CausalModel's period ends.

    Propagates forward to successor models until consumed by a compatible Precondition.
    """


@dataclass
class ConditionConflict:
    """A conflict between a Postcondition and a Precondition on the same Slot."""

    postcondition: Postcondition
    precondition: Precondition


# ── CausalMixin ────────────────────────────────────────────────────────────

_Component = Slot | CausalRelation | DefinitoryRelation


class CausalMixin:
    """A reusable, potentially incomplete fragment of a CausalModel.

    Applied to a container via applies(). Own definitions shadow mixin definitions.
    """

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self._components: list[_Component] = []
        self._applied_mixins: list[CausalMixin] = []

    @classmethod
    def create(cls, identifier: str) -> CausalMixin:
        """Creates a new empty CausalMixin."""
        return cls(identifier=identifier)

    def add(self, component: _Component) -> None:
        """Adds a component. Raises NamespaceConflictError if identifier already in use."""
        own_ids = {c.identifier for c in self._components}
        if component.identifier in own_ids:
            raise NamespaceConflictError(
                f"Identifier '{component.identifier}' already exists in '{self.identifier}'"
            )
        self._components.append(component)

    def applies(self, mixin: CausalMixin) -> None:
        """Includes a mixin's elements. Raises NamespaceConflictError on unresolvable collision."""
        own_ids = {c.identifier for c in self._components}
        new_ids = {c.identifier for c in mixin.get_slots() + mixin.get_relations()}

        for existing_mixin in self._applied_mixins:
            existing_ids = {
                c.identifier for c in existing_mixin.get_slots() + existing_mixin.get_relations()
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
            if isinstance(c, CausalRelation | DefinitoryRelation)
        }
        result: list[CausalRelation | DefinitoryRelation] = [
            c for c in self._components if isinstance(c, CausalRelation | DefinitoryRelation)
        ]
        for mixin in self._applied_mixins:
            for rel in mixin.get_relations():
                if rel.identifier not in own_ids:
                    result.append(rel)
        return result


# ── CausalModelStatus ──────────────────────────────────────────────────────


class CausalModelStatus(StrEnum):
    """Publication status of a CausalModel — controls visibility and editability."""

    PRIVATE = "private"
    SHARED = "shared"
    REVIEWABLE = "reviewable"
    INTERNAL = "internal"
    CATALOG = "catalogue"
    ARCHIVED = "archived"
    REPLACED = "superseded"
    WITHDRAWN = "withdrawn"


class Axiom:
    """An axiomatic assumption within a CausalModel.

    An Axiom is the simplest model element: a labelled statement that is
    set as a premise and not derived from other elements. It forms the
    basis for consistency checking against narrative scenes.

    Invariants enforced at construction time:
    - label must not be empty
    - description must not be empty
    """

    def __init__(self, id: str | None, label: str, description: str) -> None:
        self._id = id
        self._label = label
        self._description = description

    @classmethod
    def create(cls, label: str, description: str) -> Axiom:
        """Creates a new Axiom. Raises AxiomValidationError for empty label or description."""
        if not label.strip():
            raise AxiomValidationError("label must not be empty")
        if not description.strip():
            raise AxiomValidationError("description must not be empty")
        return cls(id=None, label=label, description=description)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> Axiom:
        """Reconstructs an Axiom from a database record."""
        return cls(
            id=record["id"],
            label=record["label"],
            description=record["description"],
        )

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def description(self) -> str:
        return self._description


class CausalModel:
    """A formal, versionable causal model.

    A CausalModel defines a bounded domain of assumptions (Axioms), entities,
    relations and claims. It serves as the reference against which narrative
    scenes are checked for consistency.

    Invariants enforced at construction time:
    - title must not be empty
    """

    def __init__(
        self,
        id: str | None,
        title: str,
        status: CausalModelStatus = CausalModelStatus.PRIVATE,
    ) -> None:
        self._id = id
        self._title = title
        self._status = status
        self._axioms: list[Axiom] = []

    @classmethod
    def create(cls, title: str) -> CausalModel:
        """Creates a new CausalModel with status 'private'.

        Raises CausalModelValidationError for empty title.
        """
        if not title.strip():
            raise CausalModelValidationError("title must not be empty")
        return cls(id=None, title=title)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> CausalModel:
        """Reconstructs a CausalModel from a database record."""
        return cls(
            id=record["id"],
            title=record["title"],
            status=CausalModelStatus(record["status"]),
        )

    def add_axiom(self, axiom: Axiom) -> None:
        """Appends an Axiom to the CausalModel in the order it is called."""
        self._axioms.append(axiom)

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
    def axioms(self) -> list[Axiom]:
        return self._axioms
