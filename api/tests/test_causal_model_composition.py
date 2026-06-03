"""Tests for Wirkgefüge domain composition.

Covers the full in-memory object model — building a CausalModel from Slots,
Zustands, CausalRelations and DefinitoryRelations, verifying traversal,
namespace enforcement, completeness, and CausalMixin reuse.

The composition model uses actual Slot references, not string IDs. Persistence
(ID-based) is a concern of the repository layer.
"""

from __future__ import annotations

import pytest

from api.exceptions.causal_model import (
    CausalRelationValidationError,
    NamespaceConflictError,
)
from api.models.causal_model import (
    CausalMixin,
    CausalModel,
    CausalRelation,
    DefinitoryRelation,
    Entity,
    EpistemicStatus,
    Polarity,
    Slot,
    SlotType,
    Zustand,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slot(identifier: str, slot_type: SlotType = SlotType.PHYSICAL_QUANTITY) -> Slot:
    return Slot.create(identifier=identifier, slot_type=slot_type)


def _entity(identifier: str) -> Entity:
    return Entity.create(identifier=identifier, slot_type=SlotType.ENTITY_STATE)


def _relation(
    identifier: str,
    source: Slot,
    target: Slot,
    mechanism: str | None = None,
) -> CausalRelation:
    return CausalRelation.create(
        identifier=identifier,
        source=source,
        target=target,
        mechanism=mechanism,
    )


def _model(identifier: str = "model", title: str = "Test Model") -> CausalModel:
    return CausalModel.create(identifier=identifier, title=title)


# ---------------------------------------------------------------------------
# Zustand
# ---------------------------------------------------------------------------


def test_zustand_create_stores_value_and_slot() -> None:
    """Expects value and the associated Slot to be accessible after creation."""
    slot = _slot("co2_concentration")
    zustand = Zustand.create(value="high", slot=slot)

    assert zustand.value == "high"
    assert zustand.slot is slot


def test_zustand_default_epistemic_status_is_incomplete() -> None:
    """Expects INCOMPLETE as the default — Zustand not yet formalised."""
    slot = _slot("co2_concentration")
    zustand = Zustand.create(value="high", slot=slot)

    assert zustand.epistemic_status == EpistemicStatus.INCOMPLETE


def test_zustand_can_be_created_axiomatic() -> None:
    """Expects AXIOMATIC Zustand to be valid — the value is set as a premise."""
    slot = _slot("baseline_temp")
    zustand = Zustand.create(
        value="14.0",
        slot=slot,
        epistemic_status=EpistemicStatus.AXIOMATIC,
    )

    assert zustand.epistemic_status == EpistemicStatus.AXIOMATIC


def test_zustand_numeric_value_is_stored() -> None:
    """Expects float values to be stored without conversion."""
    slot = _slot("co2_ppm")
    zustand = Zustand.create(value=421.0, slot=slot)

    assert zustand.value == 421.0


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------


def test_entity_is_a_slot() -> None:
    """Expects Entity to be a subtype of Slot — it participates in the same composition."""
    entity = _entity("central_bank")

    assert isinstance(entity, Slot)


def test_entity_has_entity_state_slot_type() -> None:
    """Expects Entity to use ENTITY_STATE slot type by convention."""
    entity = _entity("central_bank")

    assert entity.slot_type == SlotType.ENTITY_STATE


def test_entity_zustand_describes_capacity_not_measurement() -> None:
    """Expects qualitative states on Entity to be valid — capacity is not a measurement."""
    entity = _entity("central_bank")
    zustand = Zustand.create(value="active", slot=entity)

    assert zustand.value == "active"


# ---------------------------------------------------------------------------
# CausalRelation — object model (source/target are Slot instances)
# ---------------------------------------------------------------------------


def test_causal_relation_stores_source_and_target_slots() -> None:
    """Expects source and target to be the actual Slot objects passed at creation."""
    source = _slot("co2")
    target = _slot("temperature")
    relation = _relation("co2_warms", source, target)

    assert relation.source is source
    assert relation.target is target


def test_causal_relation_stores_mechanism() -> None:
    """Expects mechanism to describe the causal pathway when provided."""
    source = _slot("co2")
    target = _slot("temperature")
    relation = _relation("co2_warms", source, target, mechanism="Greenhouse effect")

    assert relation.mechanism == "Greenhouse effect"


def test_causal_relation_stores_source_and_target_conditions() -> None:
    """Expects source_condition and target_effect to narrow when the relation applies."""
    source = _slot("co2")
    target = _slot("temperature")
    z_source = Zustand.create("high", source)
    z_target = Zustand.create("rising", target)

    relation = CausalRelation.create(
        identifier="co2_warms",
        source=source,
        target=target,
        source_condition=z_source,
        target_effect=z_target,
    )

    assert relation.source_condition is z_source
    assert relation.target_effect is z_target


def test_causal_relation_stores_polarity() -> None:
    """Expects polarity to describe the direction of the causal effect."""
    source = _slot("co2")
    target = _slot("temperature")
    relation = CausalRelation.create(
        identifier="r",
        source=source,
        target=target,
        polarity=Polarity.POSITIVE,
    )

    assert relation.polarity == Polarity.POSITIVE


def test_causal_relation_raises_for_self_loop() -> None:
    """Expects CausalRelationValidationError — a Slot cannot causally affect itself."""
    slot = _slot("co2")

    with pytest.raises(CausalRelationValidationError):
        _relation("self_loop", slot, slot)


def test_causal_relation_raises_for_empty_identifier() -> None:
    """Expects CausalRelationValidationError when the identifier is empty."""
    source = _slot("a")
    target = _slot("b")

    with pytest.raises(CausalRelationValidationError):
        _relation("", source, target)


# ---------------------------------------------------------------------------
# DefinitoryRelation
# ---------------------------------------------------------------------------


def test_definitory_relation_stores_defined_slot_and_definition() -> None:
    """Expects DefinitoryRelation to capture what a Slot means conceptually."""
    slot_gdp = _slot("gdp")
    slot_consumption = _slot("consumption")
    relation = DefinitoryRelation.create(
        identifier="gdp_def",
        source=slot_gdp,
        target=slot_consumption,
        definition="GDP includes consumption as a component.",
    )

    assert relation.source is slot_gdp
    assert relation.target is slot_consumption
    assert relation.definition == "GDP includes consumption as a component."


def test_definitory_relation_raises_for_self_reference() -> None:
    """Expects CausalRelationValidationError — a Slot cannot define itself."""
    slot = _slot("x")

    with pytest.raises(CausalRelationValidationError):
        DefinitoryRelation.create(
            identifier="self_def",
            source=slot,
            target=slot,
            definition="Irrelevant.",
        )


# ---------------------------------------------------------------------------
# CausalModel — add() and traversal
# ---------------------------------------------------------------------------


def test_causal_model_add_slot_makes_it_retrievable_via_get_slots() -> None:
    """Expects a Slot added via add() to appear in get_slots()."""
    model = _model()
    slot = _slot("co2")

    model.add(slot)

    assert slot in model.get_slots()


def test_causal_model_add_relation_makes_it_retrievable_via_get_relations() -> None:
    """Expects a CausalRelation added via add() to appear in get_relations()."""
    model = _model()
    source = _slot("co2")
    target = _slot("temperature")
    relation = _relation("co2_warms", source, target)

    model.add(source)
    model.add(target)
    model.add(relation)

    assert relation in model.get_relations()


def test_causal_model_get_slots_includes_entities() -> None:
    """Expects Entity (subtype of Slot) to appear in get_slots()."""
    model = _model()
    entity = _entity("central_bank")

    model.add(entity)

    assert entity in model.get_slots()


def test_causal_model_get_slots_returns_only_slots() -> None:
    """Expects get_slots() to exclude Relations."""
    model = _model()
    source = _slot("a")
    target = _slot("b")
    relation = _relation("r", source, target)

    model.add(source)
    model.add(target)
    model.add(relation)

    assert relation not in model.get_slots()
    assert len(model.get_slots()) == 2


def test_causal_model_get_relations_returns_only_relations() -> None:
    """Expects get_relations() to exclude Slots."""
    model = _model()
    source = _slot("a")
    target = _slot("b")
    relation = _relation("r", source, target)

    model.add(source)
    model.add(target)
    model.add(relation)

    assert source not in model.get_relations()
    assert len(model.get_relations()) == 1


# ---------------------------------------------------------------------------
# CausalModel — namespace enforcement
# ---------------------------------------------------------------------------


def test_causal_model_add_raises_namespace_conflict_for_duplicate_identifier() -> None:
    """Expects NamespaceConflictError when a Slot with an already-used identifier is added."""
    model = _model()
    model.add(_slot("co2"))

    with pytest.raises(NamespaceConflictError):
        model.add(_slot("co2"))  # same identifier


def test_causal_model_allows_different_identifiers() -> None:
    """Expects two Slots with distinct identifiers to coexist without conflict."""
    model = _model()
    model.add(_slot("co2"))
    model.add(_slot("temperature"))  # no error

    assert len(model.get_slots()) == 2


def test_causal_model_relation_identifier_must_be_unique_in_namespace() -> None:
    """Expects NamespaceConflictError when two Relations share an identifier."""
    model = _model()
    source = _slot("a")
    target = _slot("b")
    model.add(source)
    model.add(target)
    model.add(_relation("rel", source, target))

    with pytest.raises(NamespaceConflictError):
        model.add(_relation("rel", source, target))  # same identifier


# ---------------------------------------------------------------------------
# CausalModel — axiomatic_space and is_complete
# ---------------------------------------------------------------------------


def test_causal_model_axiomatic_space_returns_axiomatic_elements() -> None:
    """Expects axiomatic_space() to return only elements with AXIOMATIC status."""
    model = _model()
    slot_a = Slot.create(
        "a", SlotType.PHYSICAL_QUANTITY, epistemic_status=EpistemicStatus.AXIOMATIC
    )
    slot_b = Slot.create("b", SlotType.PHYSICAL_QUANTITY)  # INCOMPLETE

    model.add(slot_a)
    model.add(slot_b)

    axiomatic = model.axiomatic_space()
    assert slot_a in axiomatic
    assert slot_b not in axiomatic


def test_causal_model_is_not_complete_with_incomplete_component() -> None:
    """Expects is_complete() to return False when any component is INCOMPLETE."""
    model = _model()
    model.add(_slot("co2"))  # INCOMPLETE by default

    assert not model.is_complete()


def test_causal_model_is_complete_when_all_components_are_axiomatic() -> None:
    """Expects is_complete() to return True when every component is AXIOMATIC."""
    model = _model()
    slot = Slot.create(
        "co2", SlotType.PHYSICAL_QUANTITY, epistemic_status=EpistemicStatus.AXIOMATIC
    )
    model.add(slot)

    assert model.is_complete()


def test_causal_model_is_not_complete_when_empty() -> None:
    """Expects is_complete() to return False for a model with no components."""
    model = _model()

    assert not model.is_complete()


def test_causal_model_is_complete_with_mixed_axiomatic_components() -> None:
    """Expects is_complete() to return False when even one component is INCOMPLETE."""
    model = _model()
    model.add(
        Slot.create("a", SlotType.PHYSICAL_QUANTITY, epistemic_status=EpistemicStatus.AXIOMATIC)
    )
    model.add(
        Slot.create("b", SlotType.PHYSICAL_QUANTITY, epistemic_status=EpistemicStatus.AXIOMATIC)
    )
    model.add(_slot("c"))  # INCOMPLETE

    assert not model.is_complete()


# ---------------------------------------------------------------------------
# CausalMixin — reusable fragment
# ---------------------------------------------------------------------------


def test_causal_mixin_get_slots_returns_own_slots() -> None:
    """Expects get_slots() on a CausalMixin to return its directly contained Slots."""
    mixin = CausalMixin.create(identifier="climate_mixin")
    slot = _slot("co2")
    mixin.add(slot)

    assert slot in mixin.get_slots()


def test_causal_model_applies_mixin_makes_its_slots_accessible() -> None:
    """Expects Slots from an applied CausalMixin to appear in CausalModel.get_slots()."""
    mixin = CausalMixin.create(identifier="climate_mixin")
    slot = _slot("co2")
    mixin.add(slot)

    model = _model()
    model.applies(mixin)

    assert slot in model.get_slots()


def test_causal_model_applies_mixin_makes_its_relations_accessible() -> None:
    """Expects Relations from an applied CausalMixin to appear in CausalModel.get_relations()."""
    mixin = CausalMixin.create(identifier="climate_mixin")
    source = _slot("co2")
    target = _slot("temperature")
    relation = _relation("co2_warms", source, target)
    mixin.add(source)
    mixin.add(target)
    mixin.add(relation)

    model = _model()
    model.applies(mixin)

    assert relation in model.get_relations()


def test_causal_model_own_slot_shadows_mixin_slot_with_same_identifier() -> None:
    """Expects the model's own Slot to win when it shares an identifier with a mixin Slot."""
    mixin = CausalMixin.create(identifier="base_mixin")
    mixin_slot = Slot.create("x", SlotType.PHYSICAL_QUANTITY)
    mixin.add(mixin_slot)

    model = _model()
    model_slot = Slot.create("x", SlotType.SOCIAL_QUANTITY)  # same identifier, different type
    model.add(model_slot)
    model.applies(mixin)

    # model's own slot takes precedence
    slots_named_x = [s for s in model.get_slots() if s.identifier == "x"]
    assert len(slots_named_x) == 1
    assert slots_named_x[0] is model_slot


def test_two_mixins_with_conflicting_identifier_without_model_override_raises() -> None:
    """Expects NamespaceConflictError when two mixins share an identifier.

    When no model-level override exists, the collision cannot be resolved.
    """
    mixin_a = CausalMixin.create(identifier="mixin_a")
    mixin_a.add(_slot("shared_slot"))

    mixin_b = CausalMixin.create(identifier="mixin_b")
    mixin_b.add(_slot("shared_slot"))  # same identifier as mixin_a

    model = _model()
    model.applies(mixin_a)

    with pytest.raises(NamespaceConflictError):
        model.applies(mixin_b)  # collision — model has no override


def test_causal_model_is_complete_includes_mixin_components() -> None:
    """Expects is_complete() to consider components from applied mixins."""
    mixin = CausalMixin.create(identifier="m")
    mixin.add(_slot("incomplete_slot"))  # INCOMPLETE

    model = _model()
    model.applies(mixin)

    assert not model.is_complete()


# ---------------------------------------------------------------------------
# Deep nesting — CausalMixin containing CausalMixin
# ---------------------------------------------------------------------------


def test_nested_mixin_slots_are_accessible_from_top_level_model() -> None:
    """Expects get_slots() to aggregate transitively through nested CausalMixins."""
    inner_mixin = CausalMixin.create(identifier="inner")
    deep_slot = _slot("deep_co2")
    inner_mixin.add(deep_slot)

    outer_mixin = CausalMixin.create(identifier="outer")
    outer_mixin.applies(inner_mixin)

    model = _model()
    model.applies(outer_mixin)

    assert deep_slot in model.get_slots()


def test_nested_mixin_relations_are_accessible_from_top_level_model() -> None:
    """Expects get_relations() to aggregate transitively through nested CausalMixins."""
    inner_mixin = CausalMixin.create(identifier="inner")
    source = _slot("a")
    target = _slot("b")
    deep_relation = _relation("deep_r", source, target)
    inner_mixin.add(source)
    inner_mixin.add(target)
    inner_mixin.add(deep_relation)

    outer_mixin = CausalMixin.create(identifier="outer")
    outer_mixin.applies(inner_mixin)

    model = _model()
    model.applies(outer_mixin)

    assert deep_relation in model.get_relations()


def test_three_level_nesting_is_complete_only_when_all_leaves_are_axiomatic() -> None:
    """Expects is_complete() to traverse all three nesting levels and detect INCOMPLETE leaves."""
    deep_mixin = CausalMixin.create(identifier="deep")
    deep_mixin.add(
        Slot.create("leaf", SlotType.PHYSICAL_QUANTITY, epistemic_status=EpistemicStatus.AXIOMATIC)
    )

    mid_mixin = CausalMixin.create(identifier="mid")
    mid_mixin.applies(deep_mixin)

    model = _model()
    model.applies(mid_mixin)
    model.add(
        Slot.create("own", SlotType.PHYSICAL_QUANTITY, epistemic_status=EpistemicStatus.AXIOMATIC)
    )

    assert model.is_complete()


def test_three_level_nesting_incomplete_leaf_fails_is_complete() -> None:
    """Expects is_complete() to return False when a deeply nested leaf is INCOMPLETE."""
    deep_mixin = CausalMixin.create(identifier="deep")
    deep_mixin.add(_slot("hidden_incomplete"))  # INCOMPLETE

    mid_mixin = CausalMixin.create(identifier="mid")
    mid_mixin.applies(deep_mixin)

    model = _model()
    model.applies(mid_mixin)

    assert not model.is_complete()
