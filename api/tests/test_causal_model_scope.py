"""Tests for the Scope system: TimeSlice, SpatialRegion, Discipline, Scope.

Scope describes the validity boundaries of a CausalComponent: temporal,
spatial and disciplinary. Two distinct operations are tested:
- includes(): does one scope entirely contain another? (used by add())
- is_compatible(): do two scopes overlap at all? (used for conflict detection)
"""

from __future__ import annotations

from datetime import date

import pytest

from api.exceptions.causal_model import ScopeConflictError
from api.models.causal_model import (
    CausalModel,
    Discipline,
    Scope,
    Slot,
    SlotType,
    SpatialRegion,
    TimeSlice,
)

# ---------------------------------------------------------------------------
# TimeSlice
# ---------------------------------------------------------------------------


def test_timeslice_stores_start_and_end() -> None:
    """Expects start and end dates to be accessible after creation."""
    ts = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31))

    assert ts.start == date(2000, 1, 1)
    assert ts.end == date(2010, 12, 31)


def test_timeslice_auto_generates_identifier_from_years() -> None:
    """Expects identifier to default to 'YYYY-YYYY' when not explicitly set."""
    ts = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31))

    assert ts.identifier == "2000-2010"


def test_timeslice_explicit_identifier_overrides_auto() -> None:
    """Expects a user-supplied identifier to take precedence over the auto-generated one."""
    ts = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31), identifier="pre_crisis")

    assert ts.identifier == "pre_crisis"


def test_timeslice_includes_itself() -> None:
    """Expects a TimeSlice to include itself — a slice is within its own bounds."""
    ts = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31))

    assert ts.includes(ts)


def test_timeslice_includes_strictly_shorter_slice_within_bounds() -> None:
    """Expects includes() to return True when the inner slice fits entirely."""
    outer = TimeSlice(start=date(2000, 1, 1), end=date(2020, 12, 31))
    inner = TimeSlice(start=date(2005, 1, 1), end=date(2015, 12, 31))

    assert outer.includes(inner)


def test_timeslice_does_not_include_slice_starting_before() -> None:
    """Expects includes() to return False when the other slice starts before this one."""
    ts = TimeSlice(start=date(2005, 1, 1), end=date(2015, 12, 31))
    earlier = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31))

    assert not ts.includes(earlier)


def test_timeslice_does_not_include_slice_ending_after() -> None:
    """Expects includes() to return False when the other slice ends after this one."""
    ts = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31))
    later = TimeSlice(start=date(2005, 1, 1), end=date(2020, 12, 31))

    assert not ts.includes(later)


def test_timeslice_intersects_overlapping_slices() -> None:
    """Expects intersects() to return True when slices share any common period."""
    ts1 = TimeSlice(start=date(2000, 1, 1), end=date(2010, 12, 31))
    ts2 = TimeSlice(start=date(2008, 1, 1), end=date(2018, 12, 31))

    assert ts1.intersects(ts2)
    assert ts2.intersects(ts1)  # symmetric


def test_timeslice_does_not_intersect_non_overlapping_slices() -> None:
    """Expects intersects() to return False when slices are completely separate."""
    ts1 = TimeSlice(start=date(2000, 1, 1), end=date(2005, 12, 31))
    ts2 = TimeSlice(start=date(2010, 1, 1), end=date(2020, 12, 31))

    assert not ts1.intersects(ts2)
    assert not ts2.intersects(ts1)


def test_timeslice_adjacent_slices_do_not_intersect() -> None:
    """Expects adjacent (touching but not overlapping) slices to not intersect."""
    ts1 = TimeSlice(start=date(2000, 1, 1), end=date(2009, 12, 31))
    ts2 = TimeSlice(start=date(2010, 1, 1), end=date(2020, 12, 31))

    assert not ts1.intersects(ts2)


# ---------------------------------------------------------------------------
# SpatialRegion
# ---------------------------------------------------------------------------


def test_spatial_region_includes_itself() -> None:
    """Expects a region to include itself."""
    region = SpatialRegion(identifier="europe")

    assert region.includes(region)


def test_spatial_region_includes_child_region() -> None:
    """Expects a parent region to include any of its child regions."""
    europe = SpatialRegion(identifier="europe")
    germany = SpatialRegion(identifier="germany", parent=europe)

    assert europe.includes(germany)


def test_spatial_region_includes_grandchild_region() -> None:
    """Expects includes() to traverse the full parent chain (transitive containment)."""
    europe = SpatialRegion(identifier="europe")
    germany = SpatialRegion(identifier="germany", parent=europe)
    bavaria = SpatialRegion(identifier="bavaria", parent=germany)

    assert europe.includes(bavaria)


def test_spatial_region_does_not_include_sibling() -> None:
    """Expects includes() to return False for regions in different subtrees."""
    europe = SpatialRegion(identifier="europe")
    germany = SpatialRegion(identifier="germany", parent=europe)
    france = SpatialRegion(identifier="france", parent=europe)

    assert not germany.includes(france)
    assert not france.includes(germany)


def test_spatial_region_child_does_not_include_parent() -> None:
    """Expects includes() to be asymmetric — a region does not contain its parent."""
    europe = SpatialRegion(identifier="europe")
    germany = SpatialRegion(identifier="germany", parent=europe)

    assert not germany.includes(europe)


# ---------------------------------------------------------------------------
# Discipline
# ---------------------------------------------------------------------------


def test_discipline_includes_itself() -> None:
    """Expects a discipline to include itself."""
    climate = Discipline(identifier="climate_science")

    assert climate.includes(climate)


def test_discipline_includes_subdiscipline() -> None:
    """Expects a parent discipline to include its subdiscipline."""
    climate = Discipline(identifier="climate_science")
    attribution = Discipline(identifier="attribution_science", parent=climate)

    assert climate.includes(attribution)


def test_discipline_does_not_include_sibling() -> None:
    """Expects includes() to return False for disciplines in different subtrees."""
    science = Discipline(identifier="natural_science")
    climate = Discipline(identifier="climate_science", parent=science)
    ecology = Discipline(identifier="ecology", parent=science)

    assert not climate.includes(ecology)


# ---------------------------------------------------------------------------
# Scope — includes (for add() validation)
# ---------------------------------------------------------------------------


def test_scope_includes_scope_with_narrower_temporal() -> None:
    """Expects Scope.includes() to return True when the inner temporal fits within the outer."""
    outer = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2020, 12, 31)))
    inner = Scope(temporal=TimeSlice(date(2005, 1, 1), date(2015, 12, 31)))

    assert outer.includes(inner)


def test_scope_does_not_include_scope_with_wider_temporal() -> None:
    """Expects Scope.includes() to return False when the inner temporal exceeds the outer."""
    outer = Scope(temporal=TimeSlice(date(2005, 1, 1), date(2015, 12, 31)))
    inner = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2020, 12, 31)))

    assert not outer.includes(inner)


def test_scope_with_no_constraint_includes_anything() -> None:
    """Expects a fully unconstrained Scope (all None) to include any other Scope.

    None means INCOMPLETE — not 'universal'. But for include-checking of
    add(), a missing dimension is not a blocker: we only conflict where
    both sides are defined.
    """
    unconstrained = Scope()
    any_scope = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2020, 12, 31)))

    assert unconstrained.includes(any_scope)


def test_scope_includes_checks_all_defined_dimensions() -> None:
    """Expects Scope.includes() to check spatial dimension when both sides define it."""
    europe = SpatialRegion(identifier="europe")
    germany = SpatialRegion(identifier="germany", parent=europe)

    outer = Scope(spatial=europe)
    inner = Scope(spatial=germany)
    outside = Scope(spatial=SpatialRegion(identifier="asia"))

    assert outer.includes(inner)
    assert not outer.includes(outside)


# ---------------------------------------------------------------------------
# Scope — is_compatible (for conflict detection)
# ---------------------------------------------------------------------------


def test_scope_is_compatible_with_overlapping_temporal() -> None:
    """Expects is_compatible() to return True when temporal scopes overlap."""
    scope_a = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2010, 12, 31)))
    scope_b = Scope(temporal=TimeSlice(date(2008, 1, 1), date(2018, 12, 31)))

    assert scope_a.is_compatible(scope_b)


def test_scope_is_not_compatible_with_non_overlapping_temporal() -> None:
    """Expects is_compatible() to return False when temporal scopes do not overlap."""
    scope_a = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2005, 12, 31)))
    scope_b = Scope(temporal=TimeSlice(date(2010, 1, 1), date(2020, 12, 31)))

    assert not scope_a.is_compatible(scope_b)


def test_scope_is_complete_only_when_all_dimensions_are_set() -> None:
    """Expects is_complete() to return True only when temporal, spatial and disciplinary are set."""
    full_scope = Scope(
        temporal=TimeSlice(date(2000, 1, 1), date(2010, 12, 31)),
        spatial=SpatialRegion(identifier="europe"),
        disciplinary=Discipline(identifier="climate_science"),
    )
    partial_scope = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2010, 12, 31)))

    assert full_scope.is_complete()
    assert not partial_scope.is_complete()


# ---------------------------------------------------------------------------
# Scope enforcement in CausalModel.add()
# ---------------------------------------------------------------------------


def test_causal_model_add_raises_scope_conflict_for_incompatible_temporal() -> None:
    """Expects ScopeConflictError when a component scope is incompatible with the model scope."""
    model_scope = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2010, 12, 31)))
    model = CausalModel.create(identifier="m", title="M", scope=model_scope)

    outside_scope = Scope(temporal=TimeSlice(date(2020, 1, 1), date(2030, 12, 31)))
    slot = Slot.create(
        identifier="co2",
        slot_type=SlotType.PHYSICAL_QUANTITY,
        scope=outside_scope,
    )

    with pytest.raises(ScopeConflictError):
        model.add(slot)


def test_causal_model_add_accepts_component_within_model_scope() -> None:
    """Expects add() to succeed when the component scope fits within the model scope."""
    model_scope = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2020, 12, 31)))
    model = CausalModel.create(identifier="m", title="M", scope=model_scope)

    inner_scope = Scope(temporal=TimeSlice(date(2005, 1, 1), date(2015, 12, 31)))
    slot = Slot.create(
        identifier="co2",
        slot_type=SlotType.PHYSICAL_QUANTITY,
        scope=inner_scope,
    )

    model.add(slot)  # no error

    assert slot in model.get_slots()


def test_causal_model_add_accepts_component_with_no_scope() -> None:
    """Expects add() to succeed (but not complete) when the component has no scope set."""
    model_scope = Scope(temporal=TimeSlice(date(2000, 1, 1), date(2020, 12, 31)))
    model = CausalModel.create(identifier="m", title="M", scope=model_scope)

    slot = Slot.create(identifier="co2", slot_type=SlotType.PHYSICAL_QUANTITY)  # scope=None

    model.add(slot)  # no error — INCOMPLETE, not a conflict

    assert slot in model.get_slots()
    assert not model.is_complete()
