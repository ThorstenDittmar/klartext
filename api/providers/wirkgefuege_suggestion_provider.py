"""Port: abstract interface for Wirkgefüge suggestion providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.claim import Claim


@dataclass
class SuggestedSlot:
    """A suggested Slot for a minimal Wirkgefüge."""

    identifier: str  # snake_case, English
    slot_type: (
        str  # SlotType.value: physical_quantity | social_quantity | entity_state | trend | process
    )


@dataclass
class SuggestedRelation:
    """A suggested CausalRelation for a minimal Wirkgefüge."""

    source: str  # source slot identifier
    target: str  # target slot identifier
    source_condition: str | None = None  # state description for source
    target_effect: str | None = None  # effect description for target
    mechanism: str | None = None  # causal mechanism
    epistemic_status: str = "incomplete"  # EpistemicStatus.value


@dataclass
class WirkgefuegeSuggestionResult:
    """The full result of suggesting a Wirkgefüge from a set of Claims."""

    suggested_slots: list[SuggestedSlot] = field(default_factory=list)
    suggested_relations: list[SuggestedRelation] = field(default_factory=list)
    from_claims: list[str] = field(default_factory=list)  # claim IDs


class WirkgefuegeSuggestionProvider(ABC):
    """Port: abstract interface for Wirkgefüge suggestion providers.

    Implementations may call an LLM API, a local model, or any other
    strategy — the service knows only this interface.
    """

    @abstractmethod
    async def suggest(self, claims: list[Claim]) -> WirkgefuegeSuggestionResult:
        """Takes a list of DRAFT Claims and returns a suggested minimal Wirkgefüge."""
        ...
