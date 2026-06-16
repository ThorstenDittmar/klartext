# Domain Composition Rules

Rules for testing complex domain object networks. Applied by the QA sub-agent
whenever Wirkgefüge-related objects appear in the diff.

## When These Rules Apply

Apply these rules whenever the diff touches:
- `models/causal_model.py` or `models/causal_model_*.py`
- `models/slot.py`
- `models/causal_relation.py`
- `models/causal_model_scope.py`
- Any method on `CausalModel`, `Slot`, `CausalRelation`, `CausalModelScope`

**Important:** Also apply when only `CausalModel` methods change — not only
when Slot or CausalRelation appear in the diff. CausalModel changes can affect
scope behavior without touching those files directly.

## Rule 1: Null Return Guard

Every method that returns a collection must return an empty collection, not None,
when there are no results.

```python
# Always test this case
def test_scope_resolve_returns_empty_list_for_empty_model() -> None:
    """Expects resolve() to return [] not None for an empty CausalModel."""
    model = CausalModel.create(CreateCausalModelRequest(narrative_id="n1", label="test"))
    scope = CausalModelScope(model)
    assert scope.resolve("anything") == []
```

## Rule 2: Assembled Network Tests

Any new method that operates on multiple domain objects (not just one) needs a test
that assembles the full network and verifies the interaction.

For every new method on `CausalModel` that involves Slots or Relations, write:
1. A test with a minimal network (1–2 nodes, 1 relation)
2. A test with an empty network
3. A test with the specific edge case the method is designed to handle

## Rule 3: Top-Down Operations Only

All semantic operations (namespace resolution, scope checking, completeness verification)
start at `CausalModel` and traverse downward. Never call resolve/validate on a component
directly. Tests must reflect this:

```python
# Correct — operation on the model
result = model.resolve("component_id")

# Wrong — never test this
result = slot.resolve("component_id")  # Slots are context-free
```

## Rule 4: CausalMixin Shared Components

When a component (Slot, Relation) is shared between multiple models via CausalMixin,
test that:
- Adding it to model A does not affect model B's resolution
- Removing it from model A does not remove it from model B
- Scope boundaries are enforced independently per model

## Composition Test Template

```python
class TestCausalModelComposition:
    """Tests for CausalModel behavior when components are assembled."""

    def _build_minimal_model(self) -> CausalModel:
        """Builds a CausalModel with one slot and one relation for testing."""
        model = CausalModel.create(
            CreateCausalModelRequest(narrative_id="n-001", label="test model")
        )
        slot_a = model.add_slot(SlotRequest(label="A", description="first"))
        slot_b = model.add_slot(SlotRequest(label="B", description="second"))
        model.add_relation(RelationRequest(source_id=slot_a.id, target_id=slot_b.id))
        return model

    def test_resolve_returns_all_slots(self) -> None:
        """Expects resolve() to return all slots in the model."""
        model = self._build_minimal_model()
        result = model.resolve_all_slots()
        assert len(result) == 2

    def test_resolve_empty_model_returns_empty_list(self) -> None:
        """Expects resolve() to return [] (not None) for an empty model."""
        model = CausalModel.create(
            CreateCausalModelRequest(narrative_id="n-001", label="empty")
        )
        assert model.resolve_all_slots() == []
```
