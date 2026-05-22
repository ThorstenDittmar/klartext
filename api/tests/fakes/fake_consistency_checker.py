"""FakeConsistencyChecker — configurable ConsistencyChecker stub for unit tests."""

from __future__ import annotations

from api.models.causal_model import Axiom
from api.providers.consistency_checker import (
    ConsistencyChecker,
    ConsistencyConflict,
    ConsistencyResult,
)


class FakeConsistencyChecker(ConsistencyChecker):
    """In-memory ConsistencyChecker for unit tests.

    Returns a fixed result regardless of input. Configurable at construction time.
    """

    def __init__(self, result: ConsistencyResult | None = None) -> None:
        self._result = result or ConsistencyResult(consistent=True)

    async def check(self, scene_text: str, axioms: list[Axiom]) -> ConsistencyResult:
        """Returns the pre-configured result."""
        return self._result

    @staticmethod
    def consistent() -> "FakeConsistencyChecker":
        """Returns a checker that always reports no conflicts."""
        return FakeConsistencyChecker(ConsistencyResult(consistent=True))

    @staticmethod
    def with_conflict(axiom_label: str = "A-01", description: str = "Konflikt erkannt.") -> "FakeConsistencyChecker":
        """Returns a checker that always reports one conflict."""
        return FakeConsistencyChecker(
            ConsistencyResult(
                consistent=False,
                conflicts=[ConsistencyConflict(axiom_label=axiom_label, description=description)],
            )
        )
