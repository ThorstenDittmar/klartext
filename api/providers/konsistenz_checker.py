"""KonsistenzChecker port and result types.

Follows the Ports & Adapters pattern: KonsistenzChecker is the port (ABC),
ClaudeKonsistenzChecker is the production adapter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.wirkmodell import Axiom


@dataclass
class KonsistenzKonflikt:
    """Describes a detected conflict between a scene and an Axiom."""

    axiom_label: str
    beschreibung: str
    vorschlag: str | None = None


@dataclass
class KonsistenzResult:
    """The result of a consistency check for one scene against a set of Axiome."""

    konsistent: bool
    konflikte: list[KonsistenzKonflikt] = field(default_factory=list)


class KonsistenzChecker(ABC):
    """Port — defines the contract for consistency checking."""

    @abstractmethod
    async def check(self, szenen_text: str, axiome: list[Axiom]) -> KonsistenzResult:
        """Checks whether the scene text is consistent with all given Axiome.

        Returns a KonsistenzResult with konsistent=True if no conflicts are found,
        or a list of KonsistenzKonflikte with descriptions and optional suggestions.
        """
