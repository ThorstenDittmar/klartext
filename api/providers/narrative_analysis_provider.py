"""Port: abstract interface for narrative analysis providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.narrative import Narrative


@dataclass
class WirkgefuegeSuggestion:
    """A suggestion for how a Claim maps to a Wirkgefüge element."""

    suggestion_type: str  # "slot_state" or "causal_relation"
    slot: str | None = None  # slot_state: slot identifier (snake_case)
    slot_state: str | None = None  # slot_state: state description
    source_slot: str | None = None  # causal_relation: source slot identifier
    source_condition: str | None = None  # causal_relation: source state
    target_slot: str | None = None  # causal_relation: target slot identifier
    target_effect: str | None = None  # causal_relation: target effect
    mechanism: str | None = None  # causal_relation: causal mechanism description


@dataclass
class ActorOccurrence:
    """A single occurrence of an Actor in a scene, with character offsets.

    Offsets are 0-indexed character positions relative to the scene text.
    They are a one-way tool: used to construct DocumentLinks in Phase 2,
    then discarded. Implicit actors (actor_type='group' inferred from context)
    have no direct text reference and therefore leave start_offset/end_offset as None.
    """

    scene_title: str
    start_offset: int | None = None  # None for implicit actors without a direct text reference
    end_offset: int | None = None  # None for implicit actors without a direct text reference


@dataclass
class ActorSuggestion:
    """A suggested Actor extracted from a Narrative."""

    label: str
    actor_type: str  # ActorType.value
    # All occurrences in the text with character offsets.
    # Empty list for implicit groups inferred from context without a direct text reference.
    occurrences: list[ActorOccurrence] = field(default_factory=list)
    entity_suggestion: str | None = None


@dataclass
class ClaimSuggestion:
    """A suggested Claim extracted from a Narrative scene."""

    label: str
    text: str
    claim_type: str  # ClaimType.value
    confidence: float
    wirkgefuege_suggestion: WirkgefuegeSuggestion | None = None
    # Character offsets of the claim text within the scene.
    # One-way tool for DocumentLink construction in Phase 2.
    scene_title: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None


@dataclass
class NarrativeAnalysisResult:
    """The full result of analysing a Narrative."""

    actors: list[ActorSuggestion] = field(default_factory=list)
    claims: list[ClaimSuggestion] = field(default_factory=list)


class NarrativeAnalysisProvider(ABC):
    """Port: abstract interface for narrative analysis providers.

    Implementations may call an LLM API, a local model, or any other
    analysis strategy — the service knows only this interface.
    """

    @abstractmethod
    async def analyse(self, narrative: Narrative) -> NarrativeAnalysisResult:
        """Analyses the Narrative (all scenes) and returns suggested actors and claims."""
        ...
