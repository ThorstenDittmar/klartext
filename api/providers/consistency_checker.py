"""ConsistencyChecker port and result types.

Follows the Ports & Adapters pattern: ConsistencyChecker is the port (ABC),
ClaudeConsistencyChecker is the production adapter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.causal_model import Axiom


@dataclass
class ConsistencyConflict:
    """Describes a detected conflict between a scene and an Axiom."""

    axiom_label: str
    description: str
    suggestion: str | None = None


@dataclass
class ConsistencyResult:
    """The result of a consistency check for one scene against a set of Axioms."""

    consistent: bool
    conflicts: list[ConsistencyConflict] = field(default_factory=list)


class ConsistencyChecker(ABC):
    """Port — defines the contract for consistency checking."""

    @abstractmethod
    async def check(self, scene_text: str, axioms: list[Axiom]) -> ConsistencyResult:
        """Checks whether the scene text is consistent with all given Axioms.

        Returns a ConsistencyResult with consistent=True if no conflicts are found,
        or a list of ConsistencyConflicts with descriptions and optional suggestions.
        """
