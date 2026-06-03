"""Tests for Preconditions, Postconditions and CausalModelFederation.

Pre/Postconditions describe the state of a Slot before or after a model is active.
CausalModelFederation chains CausalModels with different temporal scopes (time slices)
and manages the propagation and consumption of Postconditions across transitions.

Transition rules:
- CONSUMED: Postcondition N + compatible Precondition N+1 on the same Slot → valid, ends.
- CONFLICT: same Slot, incompatible state → ConditionConflict.
- PROPAGATED: no Precondition for that Slot → Postcondition continues to next slice.
"""

from __future__ import annotations

from datetime import date

from api.models.causal_model import (
    CausalModel,
    CausalModelFederation,
    CausalRelation,
    ConditionConflict,
    Postcondition,
    Precondition,
    Scope,
    Slot,
    SlotType,
    TimeSlice,
    Zustand,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scope(start_year: int, end_year: int) -> Scope:
    return Scope(temporal=TimeSlice(date(start_year, 1, 1), date(end_year, 12, 31)))


def _slot(identifier: str) -> Slot:
    return Slot.create(identifier=identifier, slot_type=SlotType.PHYSICAL_QUANTITY)


def _model(identifier: str, start_year: int, end_year: int) -> CausalModel:
    return CausalModel.create(
        identifier=identifier,
        title=identifier,
        scope=_scope(start_year, end_year),
    )


# ---------------------------------------------------------------------------
# Precondition and Postcondition — basics
# ---------------------------------------------------------------------------


def test_precondition_stores_slot_state_and_scope() -> None:
    """Expects all three attributes to be accessible after creation."""
    slot = _slot("co2")
    state = Zustand.create("high", slot)
    scope = _scope(2010, 2020)

    precond = Precondition(slot=slot, state=state, scope=scope)

    assert precond.slot is slot
    assert precond.state is state
    assert precond.scope is scope


def test_postcondition_stores_slot_state_and_scope() -> None:
    """Expects all three attributes to be accessible after creation."""
    slot = _slot("temperature")
    state = Zustand.create("rising", slot)
    scope = _scope(2000, 2010)

    postcond = Postcondition(slot=slot, state=state, scope=scope)

    assert postcond.slot is slot
    assert postcond.state is state
    assert postcond.scope is scope


def test_precondition_on_causal_relation() -> None:
    """Expects a Precondition to be attachable to a CausalRelation."""
    source = _slot("co2")
    target = _slot("temperature")
    relation = CausalRelation.create(identifier="r", source=source, target=target)

    precond = Precondition(
        slot=source, state=Zustand.create("high", source), scope=_scope(2000, 2010)
    )
    relation.preconditions.append(precond)

    assert precond in relation.preconditions


# ---------------------------------------------------------------------------
# Condition.is_compatible_with
# ---------------------------------------------------------------------------


def test_conditions_on_different_slots_are_compatible() -> None:
    """Expects two conditions on different Slots to coexist without conflict."""
    slot_a = _slot("co2")
    slot_b = _slot("temperature")
    post = Postcondition(
        slot=slot_a, state=Zustand.create("high", slot_a), scope=_scope(2000, 2010)
    )
    pre = Precondition(
        slot=slot_b, state=Zustand.create("rising", slot_b), scope=_scope(2010, 2020)
    )

    assert post.is_compatible_with(pre)


def test_conditions_on_same_slot_with_same_state_are_compatible() -> None:
    """Expects compatible transition: Postcondition 'rising' consumed by Precondition 'rising'."""
    slot = _slot("co2")
    post = Postcondition(slot=slot, state=Zustand.create("rising", slot), scope=_scope(2000, 2010))
    pre = Precondition(slot=slot, state=Zustand.create("rising", slot), scope=_scope(2010, 2020))

    assert post.is_compatible_with(pre)


def test_conditions_on_same_slot_with_different_states_are_incompatible() -> None:
    """Expects incompatible transition: Postcondition 'rising' vs Precondition 'stable'."""
    slot = _slot("co2")
    post = Postcondition(slot=slot, state=Zustand.create("rising", slot), scope=_scope(2000, 2010))
    pre = Precondition(slot=slot, state=Zustand.create("stable", slot), scope=_scope(2010, 2020))

    assert not post.is_compatible_with(pre)


# ---------------------------------------------------------------------------
# CausalModelFederation — structure
# ---------------------------------------------------------------------------


def test_federation_get_successors_returns_model_with_later_temporal_scope() -> None:
    """Expects the model with the later time slice to be a successor of the earlier one."""
    model_1 = _model("slice_1", 2000, 2009)
    model_2 = _model("slice_2", 2010, 2019)

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    assert model_2 in federation.get_successors(model_1)


def test_federation_get_successors_does_not_return_predecessor() -> None:
    """Expects get_successors() to not return models with earlier or equal temporal scope."""
    model_1 = _model("slice_1", 2000, 2009)
    model_2 = _model("slice_2", 2010, 2019)

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    assert model_1 not in federation.get_successors(model_2)


# ---------------------------------------------------------------------------
# CausalModelFederation — validate_transition
# ---------------------------------------------------------------------------


def test_validate_transition_returns_empty_for_compatible_conditions() -> None:
    """Expects no conflicts when the Postcondition of slice N matches Precondition of slice N+1."""
    slot = _slot("temperature")
    state_rising = Zustand.create("rising", slot)

    model_1 = _model("slice_1", 2000, 2009)
    model_1.postconditions.append(
        Postcondition(slot=slot, state=state_rising, scope=_scope(2000, 2009))
    )

    model_2 = _model("slice_2", 2010, 2019)
    model_2.preconditions.append(
        Precondition(slot=slot, state=state_rising, scope=_scope(2010, 2019))
    )

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    conflicts = federation.validate_transition(model_1, model_2)

    assert conflicts == []


def test_validate_transition_returns_condition_conflict_for_incompatible_states() -> None:
    """Expects a ConditionConflict when Postcondition and Precondition describe different states."""
    slot = _slot("co2")

    model_1 = _model("slice_1", 2000, 2009)
    model_1.postconditions.append(
        Postcondition(slot=slot, state=Zustand.create("rising", slot), scope=_scope(2000, 2009))
    )

    model_2 = _model("slice_2", 2010, 2019)
    model_2.preconditions.append(
        Precondition(slot=slot, state=Zustand.create("stable", slot), scope=_scope(2010, 2019))
    )

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    conflicts = federation.validate_transition(model_1, model_2)

    assert len(conflicts) == 1
    assert isinstance(conflicts[0], ConditionConflict)


def test_validate_transition_detects_multiple_conflicts_for_multiple_slots() -> None:
    """Expects one ConditionConflict per conflicting Slot pair."""
    slot_a = _slot("co2")
    slot_b = _slot("temperature")

    model_1 = _model("slice_1", 2000, 2009)
    model_1.postconditions.append(
        Postcondition(slot=slot_a, state=Zustand.create("rising", slot_a), scope=_scope(2000, 2009))
    )
    model_1.postconditions.append(
        Postcondition(slot=slot_b, state=Zustand.create("rising", slot_b), scope=_scope(2000, 2009))
    )

    model_2 = _model("slice_2", 2010, 2019)
    model_2.preconditions.append(
        Precondition(slot=slot_a, state=Zustand.create("stable", slot_a), scope=_scope(2010, 2019))
    )
    model_2.preconditions.append(
        Precondition(slot=slot_b, state=Zustand.create("stable", slot_b), scope=_scope(2010, 2019))
    )

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    conflicts = federation.validate_transition(model_1, model_2)

    assert len(conflicts) == 2


# ---------------------------------------------------------------------------
# CausalModelFederation — get_active_postconditions (propagation)
# ---------------------------------------------------------------------------


def test_get_active_postconditions_returns_postconditions_from_predecessors() -> None:
    """Expects Postconditions from slice N to be visible at slice N+1 when not consumed."""
    slot = _slot("co2")
    postcond = Postcondition(
        slot=slot, state=Zustand.create("rising", slot), scope=_scope(2000, 2009)
    )

    model_1 = _model("slice_1", 2000, 2009)
    model_1.postconditions.append(postcond)

    model_2 = _model("slice_2", 2010, 2019)
    # model_2 has no precondition for this slot → postcondition propagates

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    active = federation.get_active_postconditions(model_2)

    assert postcond in active


def test_get_active_postconditions_excludes_consumed_postcondition() -> None:
    """Expects a Postcondition consumed by a compatible Precondition to not propagate further."""
    slot = _slot("co2")
    state_rising = Zustand.create("rising", slot)

    model_1 = _model("slice_1", 2000, 2009)
    postcond = Postcondition(slot=slot, state=state_rising, scope=_scope(2000, 2009))
    model_1.postconditions.append(postcond)

    model_2 = _model("slice_2", 2010, 2019)
    model_2.preconditions.append(
        Precondition(slot=slot, state=state_rising, scope=_scope(2010, 2019))
    )

    model_3 = _model("slice_3", 2020, 2029)
    # No preconditions for model_3

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)
    federation.add_model(model_3)

    active_at_3 = federation.get_active_postconditions(model_3)

    assert postcond not in active_at_3  # consumed at slice_2


def test_get_active_postconditions_propagates_across_multiple_slices() -> None:
    """Expects unbounded forward propagation until explicitly consumed."""
    slot = _slot("sea_level")
    postcond = Postcondition(
        slot=slot, state=Zustand.create("rising", slot), scope=_scope(2000, 2009)
    )

    model_1 = _model("slice_1", 2000, 2009)
    model_1.postconditions.append(postcond)

    model_2 = _model("slice_2", 2010, 2019)  # no precondition
    model_3 = _model("slice_3", 2020, 2029)  # no precondition

    federation = CausalModelFederation.create(identifier="fed")
    federation.add_model(model_1)
    federation.add_model(model_2)
    federation.add_model(model_3)

    assert postcond in federation.get_active_postconditions(model_2)
    assert postcond in federation.get_active_postconditions(model_3)


# ---------------------------------------------------------------------------
# Complex scenario — two causal chains across three time slices
# ---------------------------------------------------------------------------


def test_complex_three_slice_scenario_with_valid_and_invalid_transitions() -> None:
    """Builds a three-slice federation where one transition is valid and one conflicts.

    Slice 1 (2000–2009):
      - Slot co2 with CausalRelation → Slot temperature
      - Postcondition: co2 = 'high', temperature = 'rising'

    Slice 2 (2010–2019):
      - Precondition: co2 = 'high'      → consumes Slice 1's Postcondition (compatible)
      - Precondition: temperature = 'stable' → conflicts with Slice 1's Postcondition 'rising'

    Expected: one ConditionConflict for temperature.
    """
    slot_co2 = _slot("co2")
    slot_temp = _slot("temperature")

    model_1 = _model("s1", 2000, 2009)
    model_1.postconditions.append(
        Postcondition(
            slot=slot_co2,
            state=Zustand.create("high", slot_co2),
            scope=_scope(2000, 2009),
        )
    )
    model_1.postconditions.append(
        Postcondition(
            slot=slot_temp,
            state=Zustand.create("rising", slot_temp),
            scope=_scope(2000, 2009),
        )
    )

    model_2 = _model("s2", 2010, 2019)
    model_2.preconditions.append(
        Precondition(
            slot=slot_co2,
            state=Zustand.create("high", slot_co2),  # compatible → consumed
            scope=_scope(2010, 2019),
        )
    )
    model_2.preconditions.append(
        Precondition(
            slot=slot_temp,
            state=Zustand.create("stable", slot_temp),  # incompatible → conflict
            scope=_scope(2010, 2019),
        )
    )

    federation = CausalModelFederation.create(identifier="climate_fed")
    federation.add_model(model_1)
    federation.add_model(model_2)

    conflicts = federation.validate_transition(model_1, model_2)

    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert isinstance(conflict, ConditionConflict)
    assert conflict.postcondition.slot is slot_temp
