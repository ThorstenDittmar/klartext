# Plan D — Analysis Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two AI-powered endpoints — `POST /narratives/{id}/analyse` (extract actors + claims from a Narrative) and `POST /narratives/{id}/suggest-wirkgefuege` (suggest a minimal Wirkgefüge from DRAFT Claims) — completing Steps 2 and 4 of the analysis workflow.

**Architecture:** Two Port+Adapter pairs following the existing `ClaimExtractionProvider` pattern. Both endpoints return suggestions without persisting anything. `NarrativeAnalysisService` finds the Narrative and calls the provider. `WirkgefuegeSuggestionService` aggregates DRAFT Claims across all scenes and calls the suggestion provider.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, `anthropic` Python SDK, pytest + pytest-asyncio

---

## Context for implementors

This codebase uses a layered architecture:
- `api/routers/` — HTTP only, delegates to services
- `api/services/` — business logic, orchestrates repos + providers
- `api/providers/` — external integrations (Claude API), accessed via abstract ports
- `api/repositories/` — data access via Supabase
- `api/models/` — pure domain objects (no Pydantic, no DB knowledge)
- `api/schemas/` — Pydantic request/response types
- `api/exceptions/` — exception classes per layer

Existing patterns to follow:
- `api/providers/claim_extraction_provider.py` — Port with `@abstractmethod`
- `api/providers/claude_claim_extraction_provider.py` — Claude adapter
- `api/services/claim_extractor_service.py` — Service using provider
- `api/tests/test_claim_extractor_service.py` — Service test with local fake provider

Tests use `pytest-asyncio`, all async. Run unit tests with:
```bash
api/.venv/bin/klartext test
```
Run integration tests (requires running Supabase + ANTHROPIC_API_KEY) with:
```bash
api/.venv/bin/klartext test --integration
```

---

## File Overview

### New files

| File | Responsibility |
|---|---|
| `api/providers/narrative_analysis_provider.py` | Port + result dataclasses (`NarrativeAnalysisResult`, `ActorSuggestion`, etc.) |
| `api/providers/claude_narrative_analysis_provider.py` | Claude adapter |
| `api/providers/wirkgefuege_suggestion_provider.py` | Port + result dataclasses (`WirkgefuegeSuggestionResult`, `SuggestedSlot`, etc.) |
| `api/providers/claude_wirkgefuege_suggestion_provider.py` | Claude adapter |
| `api/services/narrative_analysis_service.py` | Finds Narrative, calls analysis provider |
| `api/services/wirkgefuege_suggestion_service.py` | Aggregates DRAFT Claims, calls suggestion provider |
| `api/tests/fakes/fake_narrative_analysis_provider.py` | Deterministic fake for service tests |
| `api/tests/fakes/fake_wirkgefuege_suggestion_provider.py` | Deterministic fake for service tests |
| `api/tests/test_narrative_analysis_service.py` | Service unit tests |
| `api/tests/test_wirkgefuege_suggestion_service.py` | Service unit tests |
| `api/tests/test_claude_narrative_analysis_provider.py` | Integration test (real Claude API) |
| `api/tests/test_claude_wirkgefuege_suggestion_provider.py` | Integration test (real Claude API) |

### Modified files

| File | Changes |
|---|---|
| `api/exceptions/narrative.py` | Add `NarrativeAnalysisError`, `WirkgefuegeSuggestionError` |
| `api/schemas/narratives.py` | Add response schemas for both new endpoints |
| `api/routers/narratives.py` | Add `POST /{narrative_id}/analyse` and `POST /{narrative_id}/suggest-wirkgefuege` |
| `api/dependencies.py` | Add `get_narrative_analysis_service`, `get_wirkgefuege_suggestion_service` |
| `api/tests/test_narratives_router.py` | Add router tests for both new endpoints |

---

## Task 1: NarrativeAnalysisProvider port + FakeNarrativeAnalysisProvider

**Files:**
- Create: `api/providers/narrative_analysis_provider.py`
- Create: `api/tests/fakes/fake_narrative_analysis_provider.py`

There are no isolated unit tests for the port itself (abstract) or the fake. They are tested indirectly in Task 2.

- [ ] **Step 1: Create the provider port**

`api/providers/narrative_analysis_provider.py`:

```python
"""Port: abstract interface for narrative analysis providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.narrative import Narrative


@dataclass
class WirkgefuegeSuggestion:
    """A suggestion for how a Claim maps to a Wirkgefüge element."""

    suggestion_type: str  # "slot_zustand" or "causal_relation"
    slot: str | None = None             # slot_zustand: slot identifier (snake_case)
    zustand: str | None = None          # slot_zustand: state description
    source_slot: str | None = None      # causal_relation: source slot identifier
    source_condition: str | None = None  # causal_relation: source state
    target_slot: str | None = None      # causal_relation: target slot identifier
    target_effect: str | None = None    # causal_relation: target effect
    mechanism: str | None = None        # causal_relation: causal mechanism description


@dataclass
class ActorSuggestion:
    """A suggested Actor extracted from a Narrative."""

    label: str
    actor_type: str                                    # ActorType.value
    occurrences: list[str] = field(default_factory=list)  # scene titles
    entity_suggestion: str | None = None               # causal model identifier (snake_case)


@dataclass
class ClaimSuggestion:
    """A suggested Claim extracted from a Narrative scene."""

    label: str
    text: str
    claim_type: str                                   # ClaimType.value
    confidence: float
    wirkgefuege_suggestion: WirkgefuegeSuggestion | None = None


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
```

- [ ] **Step 2: Create FakeNarrativeAnalysisProvider**

`api/tests/fakes/fake_narrative_analysis_provider.py`:

```python
"""Fake NarrativeAnalysisProvider for use in service and router tests."""

from __future__ import annotations

from api.models.narrative import Narrative
from api.providers.narrative_analysis_provider import (
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
    WirkgefuegeSuggestion,
)


class FakeNarrativeAnalysisProvider(NarrativeAnalysisProvider):
    """Returns a fixed deterministic result without calling any external API.

    Used in service and router tests to avoid Claude API calls.
    """

    async def analyse(self, narrative: Narrative) -> NarrativeAnalysisResult:
        """Returns one actor and one causal claim regardless of input."""
        return NarrativeAnalysisResult(
            actors=[
                ActorSuggestion(
                    label="Central Bank",
                    actor_type="institution",
                    occurrences=["Scene 1"],
                    entity_suggestion="central_bank",
                )
            ],
            claims=[
                ClaimSuggestion(
                    label="Money supply causes inflation",
                    text="An increase in money supply leads to higher inflation.",
                    claim_type="causal",
                    confidence=0.87,
                    wirkgefuege_suggestion=WirkgefuegeSuggestion(
                        suggestion_type="causal_relation",
                        source_slot="money_supply",
                        source_condition="high",
                        target_slot="inflation",
                        target_effect="rising",
                        mechanism="quantity_theory",
                    ),
                )
            ],
        )
```

- [ ] **Step 3: Verify both files are importable**

```bash
cd /path/to/klartext && api/.venv/bin/python -c "
from api.providers.narrative_analysis_provider import NarrativeAnalysisProvider, NarrativeAnalysisResult
from tests.fakes.fake_narrative_analysis_provider import FakeNarrativeAnalysisProvider
print('OK')
"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add api/providers/narrative_analysis_provider.py api/tests/fakes/fake_narrative_analysis_provider.py
git commit -m "feat: add NarrativeAnalysisProvider port and fake"
```

---

## Task 2: NarrativeAnalysisService + exceptions + tests

**Files:**
- Modify: `api/exceptions/narrative.py` (add `NarrativeAnalysisError`)
- Create: `api/services/narrative_analysis_service.py`
- Create: `api/tests/test_narrative_analysis_service.py`

- [ ] **Step 1: Write the failing tests**

`api/tests/test_narrative_analysis_service.py`:

```python
"""Tests for NarrativeAnalysisService.

Uses FakeNarrativeRepository and FakeNarrativeAnalysisProvider — no DB or API calls.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative import NarrativeNotFoundError
from api.providers.narrative_analysis_provider import (
    NarrativeAnalysisResult,
)
from api.services.narrative_analysis_service import NarrativeAnalysisService
from tests.fakes.fake_narrative_analysis_provider import FakeNarrativeAnalysisProvider
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from tests.mothers.narrative_mother import NarrativeMother


@pytest.mark.asyncio
async def test_narrative_analysis_service_returns_analysis_result() -> None:
    """Expects the service to return a NarrativeAnalysisResult for a known narrative."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert isinstance(result, NarrativeAnalysisResult)


@pytest.mark.asyncio
async def test_narrative_analysis_service_result_contains_actors() -> None:
    """Expects at least one actor in the result when the provider returns actors."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert len(result.actors) == 1
    assert result.actors[0].label == "Central Bank"


@pytest.mark.asyncio
async def test_narrative_analysis_service_result_contains_claims() -> None:
    """Expects at least one claim in the result when the provider returns claims."""
    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    result = await service.analyse(saved.id)  # type: ignore[arg-type]

    assert len(result.claims) == 1
    assert result.claims[0].claim_type == "causal"


@pytest.mark.asyncio
async def test_narrative_analysis_service_passes_narrative_to_provider() -> None:
    """Expects the service to pass the correct Narrative to the provider."""

    class CapturingProvider(FakeNarrativeAnalysisProvider):
        def __init__(self) -> None:
            self.received_id: str | None = None

        async def analyse(self, narrative):  # type: ignore[override]
            self.received_id = narrative.id
            return await super().analyse(narrative)

    repo = FakeNarrativeRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    provider = CapturingProvider()
    service = NarrativeAnalysisService(repository=repo, provider=provider)

    await service.analyse(saved.id)  # type: ignore[arg-type]

    assert provider.received_id == saved.id


@pytest.mark.asyncio
async def test_narrative_analysis_service_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    repo = FakeNarrativeRepository()
    service = NarrativeAnalysisService(repository=repo, provider=FakeNarrativeAnalysisProvider())

    with pytest.raises(NarrativeNotFoundError):
        await service.analyse("00000000-0000-0000-0000-000000000000")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
api/.venv/bin/pytest api/tests/test_narrative_analysis_service.py -v
```
Expected: `ImportError` or `ModuleNotFoundError` — `NarrativeAnalysisService` does not exist yet.

- [ ] **Step 3: Add NarrativeAnalysisError to exceptions**

Open `api/exceptions/narrative.py` and add at the end:

```python
class NarrativeAnalysisError(ServiceError):
    """Raised when narrative analysis fails (e.g. provider error or invalid response)."""
```

- [ ] **Step 4: Create the service**

`api/services/narrative_analysis_service.py`:

```python
"""Service: analyses a Narrative by calling a NarrativeAnalysisProvider."""

from __future__ import annotations

from api.providers.narrative_analysis_provider import (
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
)
from api.repositories.narrative_repository import NarrativeRepository


class NarrativeAnalysisService:
    """Finds the Narrative and delegates analysis to the injected provider.

    Does not persist any results — the caller decides what to do with the suggestions.
    """

    def __init__(
        self,
        repository: NarrativeRepository,
        provider: NarrativeAnalysisProvider,
    ) -> None:
        self._repository = repository
        self._provider = provider

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        """Analyses the Narrative with the given ID.

        Returns suggested actors and claims. Does not persist anything.
        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        """
        narrative = await self._repository.find_by_id(narrative_id)
        return await self._provider.analyse(narrative)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
api/.venv/bin/pytest api/tests/test_narrative_analysis_service.py -v
```
Expected: `5 passed`

- [ ] **Step 6: Run full suite to confirm nothing broken**

```bash
api/.venv/bin/klartext test
```
Expected: all passing

- [ ] **Step 7: Commit**

```bash
git add api/exceptions/narrative.py api/services/narrative_analysis_service.py api/tests/test_narrative_analysis_service.py
git commit -m "feat: add NarrativeAnalysisService with NarrativeAnalysisError"
```

---

## Task 3: WirkgefuegeSuggestionProvider port + FakeWirkgefuegeSuggestionProvider

**Files:**
- Create: `api/providers/wirkgefuege_suggestion_provider.py`
- Create: `api/tests/fakes/fake_wirkgefuege_suggestion_provider.py`

- [ ] **Step 1: Create the provider port**

`api/providers/wirkgefuege_suggestion_provider.py`:

```python
"""Port: abstract interface for Wirkgefüge suggestion providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from api.models.claim import Claim


@dataclass
class SuggestedSlot:
    """A suggested Slot for a minimal Wirkgefüge."""

    identifier: str   # snake_case, English
    slot_type: str    # SlotType.value: physical_quantity | social_quantity | entity_state | trend | process


@dataclass
class SuggestedRelation:
    """A suggested CausalRelation for a minimal Wirkgefüge."""

    source: str                               # source slot identifier
    target: str                               # target slot identifier
    source_condition: str | None = None       # state description for source
    target_effect: str | None = None          # effect description for target
    mechanism: str | None = None              # causal mechanism
    epistemic_status: str = "incomplete"      # EpistemicStatus.value


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
```

- [ ] **Step 2: Create FakeWirkgefuegeSuggestionProvider**

`api/tests/fakes/fake_wirkgefuege_suggestion_provider.py`:

```python
"""Fake WirkgefuegeSuggestionProvider for use in service and router tests."""

from __future__ import annotations

from api.models.claim import Claim
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionProvider,
    WirkgefuegeSuggestionResult,
)


class FakeWirkgefuegeSuggestionProvider(WirkgefuegeSuggestionProvider):
    """Returns a fixed deterministic result without calling any external API.

    Used in service and router tests to avoid Claude API calls.
    """

    async def suggest(self, claims: list[Claim]) -> WirkgefuegeSuggestionResult:
        """Returns two slots and one relation, referencing the provided claim IDs."""
        return WirkgefuegeSuggestionResult(
            suggested_slots=[
                SuggestedSlot(identifier="money_supply", slot_type="physical_quantity"),
                SuggestedSlot(identifier="inflation", slot_type="trend"),
            ],
            suggested_relations=[
                SuggestedRelation(
                    source="money_supply",
                    target="inflation",
                    source_condition="high",
                    target_effect="rising",
                    mechanism="quantity_theory",
                    epistemic_status="incomplete",
                )
            ],
            from_claims=[c.id for c in claims if c.id is not None],
        )
```

- [ ] **Step 3: Verify imports work**

```bash
api/.venv/bin/python -c "
from api.providers.wirkgefuege_suggestion_provider import WirkgefuegeSuggestionProvider, WirkgefuegeSuggestionResult
from tests.fakes.fake_wirkgefuege_suggestion_provider import FakeWirkgefuegeSuggestionProvider
print('OK')
"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add api/providers/wirkgefuege_suggestion_provider.py api/tests/fakes/fake_wirkgefuege_suggestion_provider.py
git commit -m "feat: add WirkgefuegeSuggestionProvider port and fake"
```

---

## Task 4: WirkgefuegeSuggestionService + tests

**Files:**
- Modify: `api/exceptions/narrative.py` (add `WirkgefuegeSuggestionError`)
- Create: `api/services/wirkgefuege_suggestion_service.py`
- Create: `api/tests/test_wirkgefuege_suggestion_service.py`

Context: `WirkgefuegeSuggestionService` needs `NarrativeRepository` (to get scene IDs) and `ClaimRepository` (to load claims per scene). Claims are filtered to `status == ClaimStatus.DRAFT`. If no DRAFT claims exist, return an empty `WirkgefuegeSuggestionResult` without calling the provider.

`FakeNarrativeRepository` is in `api/tests/fakes/fake_narrative_repository.py`. To save a narrative with scenes, use `NarrativeMother.with_one_scene()` from `api/tests/mothers/narrative_mother.py`.

`FakeClaimRepository` is in `api/tests/fakes/fake_claim_repository.py`. Its `save_all(claims, scene_id)` method stores claims; `find_by_scene_id(scene_id)` retrieves them.

`ClaimMother` is in `api/tests/mothers/claim_mother.py`. Use `ClaimMother.causal()` for a single CAUSAL/DRAFT claim. Use `ClaimMother.collection()` for 3 claims (all DRAFT initially).

- [ ] **Step 1: Write the failing tests**

`api/tests/test_wirkgefuege_suggestion_service.py`:

```python
"""Tests for WirkgefuegeSuggestionService.

Uses FakeNarrativeRepository, FakeClaimRepository, and FakeWirkgefuegeSuggestionProvider
— no DB or API calls.
"""

from __future__ import annotations

import pytest

from api.exceptions.narrative import NarrativeNotFoundError
from api.models.claim import ClaimStatus
from api.providers.wirkgefuege_suggestion_provider import WirkgefuegeSuggestionResult
from api.services.wirkgefuege_suggestion_service import WirkgefuegeSuggestionService
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from tests.fakes.fake_wirkgefuege_suggestion_provider import FakeWirkgefuegeSuggestionProvider
from tests.mothers.claim_mother import ClaimMother
from tests.mothers.narrative_mother import NarrativeMother


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_returns_result() -> None:
    """Expects a WirkgefuegeSuggestionResult for a narrative with DRAFT claims."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]
    await claim_repo.save_all(ClaimMother.collection(), scene_id=scene_id)

    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    result = await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert isinstance(result, WirkgefuegeSuggestionResult)
    assert len(result.suggested_slots) == 2


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_includes_claim_ids_in_result() -> None:
    """Expects from_claims to reference the IDs of the DRAFT claims passed to the provider."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]
    saved_claims = await claim_repo.save_all(ClaimMother.collection(), scene_id=scene_id)

    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    result = await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert set(result.from_claims) == {c.id for c in saved_claims}


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_returns_empty_when_no_draft_claims() -> None:
    """Expects an empty WirkgefuegeSuggestionResult when no DRAFT claims exist."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]

    # Save one claim and mark it LINKED — not DRAFT
    [saved_claim] = await claim_repo.save_all([ClaimMother.causal()], scene_id=scene_id)
    saved_claim.link_to_wirkgefuege("slot-xyz")
    await claim_repo.update(saved_claim)

    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    result = await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert result.suggested_slots == []
    assert result.suggested_relations == []
    assert result.from_claims == []


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_only_passes_draft_claims() -> None:
    """Expects only DRAFT claims to be passed to the provider (not LINKED or UNRESOLVED)."""

    class CapturingProvider(FakeWirkgefuegeSuggestionProvider):
        def __init__(self) -> None:
            self.received_claims: list = []

        async def suggest(self, claims):  # type: ignore[override]
            self.received_claims = list(claims)
            return await super().suggest(claims)

    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved_narrative = await narrative_repo.save(NarrativeMother.with_one_scene())
    scene_id: str = saved_narrative.scenes[0].id  # type: ignore[assignment]

    [draft_claim, linked_claim, unresolved_claim] = await claim_repo.save_all(
        ClaimMother.collection(), scene_id=scene_id
    )
    linked_claim.link_to_wirkgefuege("slot-abc")
    await claim_repo.update(linked_claim)
    unresolved_claim.mark_unresolved()
    await claim_repo.update(unresolved_claim)

    provider = CapturingProvider()
    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=provider,
    )

    await service.suggest_for_narrative(saved_narrative.id)  # type: ignore[arg-type]

    assert len(provider.received_claims) == 1
    assert provider.received_claims[0].status == ClaimStatus.DRAFT


@pytest.mark.asyncio
async def test_wirkgefuege_suggestion_service_raises_for_unknown_narrative() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    service = WirkgefuegeSuggestionService(
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        provider=FakeWirkgefuegeSuggestionProvider(),
    )

    with pytest.raises(NarrativeNotFoundError):
        await service.suggest_for_narrative("00000000-0000-0000-0000-000000000000")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
api/.venv/bin/pytest api/tests/test_wirkgefuege_suggestion_service.py -v
```
Expected: `ImportError` — `WirkgefuegeSuggestionService` does not exist yet.

- [ ] **Step 3: Add WirkgefuegeSuggestionError to exceptions**

Open `api/exceptions/narrative.py` and add at the end:

```python
class WirkgefuegeSuggestionError(ServiceError):
    """Raised when Wirkgefüge suggestion fails (e.g. provider error or invalid response)."""
```

- [ ] **Step 4: Create the service**

`api/services/wirkgefuege_suggestion_service.py`:

```python
"""Service: suggests a minimal Wirkgefüge from DRAFT Claims of a Narrative."""

from __future__ import annotations

from api.models.claim import ClaimStatus
from api.providers.wirkgefuege_suggestion_provider import (
    WirkgefuegeSuggestionProvider,
    WirkgefuegeSuggestionResult,
)
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository


class WirkgefuegeSuggestionService:
    """Aggregates DRAFT Claims for a Narrative and delegates suggestion to the injected provider.

    Does not persist any results — the caller decides what to do with the suggestions.
    Returns an empty WirkgefuegeSuggestionResult when no DRAFT Claims exist.
    """

    def __init__(
        self,
        narrative_repository: NarrativeRepository,
        claim_repository: ClaimRepository,
        provider: WirkgefuegeSuggestionProvider,
    ) -> None:
        self._narrative_repository = narrative_repository
        self._claim_repository = claim_repository
        self._provider = provider

    async def suggest_for_narrative(self, narrative_id: str) -> WirkgefuegeSuggestionResult:
        """Suggests a minimal Wirkgefüge from all DRAFT Claims of the Narrative.

        Loads the Narrative to get scene IDs, then fetches DRAFT Claims for each scene.
        Returns an empty result when no DRAFT Claims exist (no API call made).
        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        """
        narrative = await self._narrative_repository.find_by_id(narrative_id)

        draft_claims = []
        for scene in narrative.scenes:
            claims = await self._claim_repository.find_by_scene_id(scene.id)  # type: ignore[arg-type]
            draft_claims.extend(c for c in claims if c.status == ClaimStatus.DRAFT)

        if not draft_claims:
            return WirkgefuegeSuggestionResult()

        return await self._provider.suggest(draft_claims)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
api/.venv/bin/pytest api/tests/test_wirkgefuege_suggestion_service.py -v
```
Expected: `5 passed`

- [ ] **Step 6: Run full suite**

```bash
api/.venv/bin/klartext test
```
Expected: all passing

- [ ] **Step 7: Commit**

```bash
git add api/exceptions/narrative.py api/services/wirkgefuege_suggestion_service.py api/tests/test_wirkgefuege_suggestion_service.py
git commit -m "feat: add WirkgefuegeSuggestionService"
```

---

## Task 5: Schemas + Router endpoints + Router tests + Dependencies wiring

**Files:**
- Modify: `api/schemas/narratives.py` (add new response schemas)
- Modify: `api/routers/narratives.py` (add 2 new endpoints)
- Modify: `api/dependencies.py` (add `get_narrative_analysis_service`, `get_wirkgefuege_suggestion_service`)
- Modify: `api/tests/test_narratives_router.py` (add router tests)

### Sub-step A: Schemas

- [ ] **Step 1: Write the failing schema tests** (no separate test file needed — schemas are tested via router tests below)

- [ ] **Step 2: Add schemas to `api/schemas/narratives.py`**

Open `api/schemas/narratives.py` and add at the end:

```python
# ---------------------------------------------------------------------------
# Analysis endpoint schemas
# ---------------------------------------------------------------------------


class WirkgefuegeSuggestionSchema(BaseModel):
    """Schema for a Wirkgefüge suggestion within a ClaimSuggestionResponse."""

    suggestion_type: str
    slot: str | None = None
    zustand: str | None = None
    source_slot: str | None = None
    source_condition: str | None = None
    target_slot: str | None = None
    target_effect: str | None = None
    mechanism: str | None = None


class ActorSuggestionResponse(BaseModel):
    """Schema for a suggested Actor in the analysis response."""

    label: str
    actor_type: str
    occurrences: list[str]
    entity_suggestion: str | None


class ClaimSuggestionResponse(BaseModel):
    """Schema for a suggested Claim in the analysis response."""

    label: str
    text: str
    claim_type: str
    confidence: float
    wirkgefuege_suggestion: WirkgefuegeSuggestionSchema | None


class AnalyseNarrativeResponse(BaseModel):
    """Response from POST /narratives/{id}/analyse."""

    actors: list[ActorSuggestionResponse]
    claims: list[ClaimSuggestionResponse]


# ---------------------------------------------------------------------------
# Wirkgefüge suggestion endpoint schemas
# ---------------------------------------------------------------------------


class SuggestedSlotResponse(BaseModel):
    """Schema for a suggested Slot in the Wirkgefüge suggestion response."""

    identifier: str
    slot_type: str


class SuggestedRelationResponse(BaseModel):
    """Schema for a suggested CausalRelation in the Wirkgefüge suggestion response."""

    source: str
    target: str
    source_condition: str | None
    target_effect: str | None
    mechanism: str | None
    epistemic_status: str


class SuggestWirkgefuegeResponse(BaseModel):
    """Response from POST /narratives/{id}/suggest-wirkgefuege."""

    suggested_slots: list[SuggestedSlotResponse]
    suggested_relations: list[SuggestedRelationResponse]
    from_claims: list[str]
```

Note: `BaseModel` is already imported in `api/schemas/narratives.py`. Do not add a second import.

### Sub-step B: Dependencies

- [ ] **Step 3: Wire up both new services in `api/dependencies.py`**

Add to the docstring comment block at the top of `dependencies.py` (update DI chain comment):
```python
#  get_narrative_analysis_service ─────────────────────────────────────────► (narrative analysis)
#  get_wirkgefuege_suggestion_service ──────────────────────────────────────► (wirkgefuege suggestion)
```

Add these imports at the top of `api/dependencies.py` (after existing service imports):
```python
from api.services.narrative_analysis_service import NarrativeAnalysisService
from api.services.wirkgefuege_suggestion_service import WirkgefuegeSuggestionService
```

Add to `api/dependencies.py` at the end. Note the **lazy imports** inside each function — this avoids `ImportError` if the Claude provider files don't exist yet (they are created in Task 6), since the function body runs only at request time, not at module import time.

```python
async def get_narrative_analysis_service_async(
    repository: NarrativeRepository = Depends(get_narrative_repository),
) -> NarrativeAnalysisService:
    """Wires SupabaseNarrativeRepository and ClaudeNarrativeAnalysisProvider into NarrativeAnalysisService.

    Uses a lazy import for ClaudeNarrativeAnalysisProvider so the module can be loaded
    even before the Claude provider file is created (Task 6).
    """
    from api.providers.claude_narrative_analysis_provider import ClaudeNarrativeAnalysisProvider  # noqa: PLC0415

    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    provider = ClaudeNarrativeAnalysisProvider(client=client)
    return NarrativeAnalysisService(repository=repository, provider=provider)


async def get_wirkgefuege_suggestion_service(
    narrative_repository: NarrativeRepository = Depends(get_narrative_repository),
    claim_repository: ClaimRepository = Depends(get_claim_repository),
) -> WirkgefuegeSuggestionService:
    """Wires repositories and ClaudeWirkgefuegeSuggestionProvider into WirkgefuegeSuggestionService.

    Uses a lazy import for ClaudeWirkgefuegeSuggestionProvider so the module can be loaded
    even before the Claude provider file is created (Task 6).
    """
    from api.providers.claude_wirkgefuege_suggestion_provider import ClaudeWirkgefuegeSuggestionProvider  # noqa: PLC0415

    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    provider = ClaudeWirkgefuegeSuggestionProvider(client=client)
    return WirkgefuegeSuggestionService(
        narrative_repository=narrative_repository,
        claim_repository=claim_repository,
        provider=provider,
    )
```

### Sub-step C: Router endpoints + Router tests

- [ ] **Step 4: Write the failing router tests**

Open `api/tests/test_narratives_router.py` and add at the end. First add these imports at the top (after existing imports):

```python
from api.dependencies import get_narrative_analysis_service_async, get_wirkgefuege_suggestion_service
from api.providers.narrative_analysis_provider import (
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisResult,
)
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionResult,
)
```

Then add these classes and tests at the end of `api/tests/test_narratives_router.py`:

```python
# ---------------------------------------------------------------------------
# Fake services for analysis endpoints
# ---------------------------------------------------------------------------


class FakeNarrativeAnalysisService:
    """Returns preset analysis results without hitting the DB or Claude API."""

    def __init__(
        self,
        *,
        raise_on_analyse: Exception | None = None,
    ) -> None:
        self._raise_on_analyse = raise_on_analyse

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        if self._raise_on_analyse:
            raise self._raise_on_analyse
        return NarrativeAnalysisResult(
            actors=[
                ActorSuggestion(
                    label="Central Bank",
                    actor_type="institution",
                    occurrences=["Scene 1"],
                    entity_suggestion="central_bank",
                )
            ],
            claims=[
                ClaimSuggestion(
                    label="Money supply causes inflation",
                    text="Higher money supply leads to inflation.",
                    claim_type="causal",
                    confidence=0.87,
                    wirkgefuege_suggestion=None,
                )
            ],
        )


class FakeWirkgefuegeSuggestionService:
    """Returns preset suggestion results without hitting the DB or Claude API."""

    def __init__(
        self,
        *,
        raise_on_suggest: Exception | None = None,
    ) -> None:
        self._raise_on_suggest = raise_on_suggest

    async def suggest_for_narrative(self, narrative_id: str) -> WirkgefuegeSuggestionResult:
        if self._raise_on_suggest:
            raise self._raise_on_suggest
        return WirkgefuegeSuggestionResult(
            suggested_slots=[
                SuggestedSlot(identifier="money_supply", slot_type="physical_quantity"),
                SuggestedSlot(identifier="inflation", slot_type="trend"),
            ],
            suggested_relations=[
                SuggestedRelation(
                    source="money_supply",
                    target="inflation",
                    mechanism="quantity_theory",
                    epistemic_status="incomplete",
                )
            ],
            from_claims=["claim-uuid-1"],
        )


# ---------------------------------------------------------------------------
# Tests for POST /{narrative_id}/analyse
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyse_narrative_returns_actors_and_claims() -> None:
    """Expects 200 with actors and claims when the service succeeds."""
    app.dependency_overrides[get_narrative_analysis_service_async] = (
        lambda: FakeNarrativeAnalysisService()
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(f"/narratives/{SAVED_NARRATIVE_ID}/analyse")

        assert response.status_code == 200
        body = response.json()
        assert len(body["actors"]) == 1
        assert body["actors"][0]["label"] == "Central Bank"
        assert len(body["claims"]) == 1
        assert body["claims"][0]["claim_type"] == "causal"
    finally:
        app.dependency_overrides.pop(get_narrative_analysis_service_async, None)


@pytest.mark.asyncio
async def test_analyse_narrative_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    from api.exceptions.narrative import NarrativeNotFoundError

    app.dependency_overrides[get_narrative_analysis_service_async] = lambda: (
        FakeNarrativeAnalysisService(raise_on_analyse=NarrativeNotFoundError("not found"))
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/narratives/does-not-exist/analyse")

        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_narrative_analysis_service_async, None)


# ---------------------------------------------------------------------------
# Tests for POST /{narrative_id}/suggest-wirkgefuege
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_wirkgefuege_returns_slots_and_relations() -> None:
    """Expects 200 with suggested slots and relations when the service succeeds."""
    app.dependency_overrides[get_wirkgefuege_suggestion_service] = (
        lambda: FakeWirkgefuegeSuggestionService()
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"/narratives/{SAVED_NARRATIVE_ID}/suggest-wirkgefuege"
            )

        assert response.status_code == 200
        body = response.json()
        assert len(body["suggested_slots"]) == 2
        assert body["suggested_slots"][0]["identifier"] == "money_supply"
        assert len(body["suggested_relations"]) == 1
        assert body["from_claims"] == ["claim-uuid-1"]
    finally:
        app.dependency_overrides.pop(get_wirkgefuege_suggestion_service, None)


@pytest.mark.asyncio
async def test_suggest_wirkgefuege_returns_404_for_unknown_narrative() -> None:
    """Expects 404 when the service raises NarrativeNotFoundError."""
    from api.exceptions.narrative import NarrativeNotFoundError

    app.dependency_overrides[get_wirkgefuege_suggestion_service] = lambda: (
        FakeWirkgefuegeSuggestionService(
            raise_on_suggest=NarrativeNotFoundError("not found")
        )
    )
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/narratives/does-not-exist/suggest-wirkgefuege")

        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_wirkgefuege_suggestion_service, None)
```

- [ ] **Step 5: Run router tests to verify they fail**

```bash
api/.venv/bin/pytest api/tests/test_narratives_router.py -v -k "analyse or suggest"
```
Expected: `ImportError` — endpoints not defined yet.

- [ ] **Step 6: Add the two endpoints to `api/routers/narratives.py`**

First add these imports at the top of `api/routers/narratives.py` (after existing imports):

```python
from api.dependencies import get_narrative_analysis_service_async, get_wirkgefuege_suggestion_service
from api.providers.narrative_analysis_provider import (
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisResult,
    WirkgefuegeSuggestion,
)
from api.providers.wirkgefuege_suggestion_provider import WirkgefuegeSuggestionResult
from api.schemas.narratives import (
    ActorSuggestionResponse,
    AnalyseNarrativeResponse,
    ClaimSuggestionResponse,
    SuggestedRelationResponse,
    SuggestedSlotResponse,
    SuggestWirkgefuegeResponse,
    WirkgefuegeSuggestionSchema,
)
from api.services.narrative_analysis_service import NarrativeAnalysisService
from api.services.wirkgefuege_suggestion_service import WirkgefuegeSuggestionService
```

Then add these helper functions after the existing helpers (before the `# Narrative endpoints` section):

```python
def _to_wirkgefuege_suggestion_schema(
    ws: WirkgefuegeSuggestion,
) -> WirkgefuegeSuggestionSchema:
    """Converts a WirkgefuegeSuggestion dataclass to its Pydantic schema."""
    return WirkgefuegeSuggestionSchema(
        suggestion_type=ws.suggestion_type,
        slot=ws.slot,
        zustand=ws.zustand,
        source_slot=ws.source_slot,
        source_condition=ws.source_condition,
        target_slot=ws.target_slot,
        target_effect=ws.target_effect,
        mechanism=ws.mechanism,
    )


def _to_analyse_response(result: NarrativeAnalysisResult) -> AnalyseNarrativeResponse:
    """Converts a NarrativeAnalysisResult to AnalyseNarrativeResponse."""
    return AnalyseNarrativeResponse(
        actors=[
            ActorSuggestionResponse(
                label=a.label,
                actor_type=a.actor_type,
                occurrences=a.occurrences,
                entity_suggestion=a.entity_suggestion,
            )
            for a in result.actors
        ],
        claims=[
            ClaimSuggestionResponse(
                label=c.label,
                text=c.text,
                claim_type=c.claim_type,
                confidence=c.confidence,
                wirkgefuege_suggestion=(
                    _to_wirkgefuege_suggestion_schema(c.wirkgefuege_suggestion)
                    if c.wirkgefuege_suggestion
                    else None
                ),
            )
            for c in result.claims
        ],
    )


def _to_suggest_response(result: WirkgefuegeSuggestionResult) -> SuggestWirkgefuegeResponse:
    """Converts a WirkgefuegeSuggestionResult to SuggestWirkgefuegeResponse."""
    return SuggestWirkgefuegeResponse(
        suggested_slots=[
            SuggestedSlotResponse(identifier=s.identifier, slot_type=s.slot_type)
            for s in result.suggested_slots
        ],
        suggested_relations=[
            SuggestedRelationResponse(
                source=r.source,
                target=r.target,
                source_condition=r.source_condition,
                target_effect=r.target_effect,
                mechanism=r.mechanism,
                epistemic_status=r.epistemic_status,
            )
            for r in result.suggested_relations
        ],
        from_claims=result.from_claims,
    )
```

Then add the two endpoints after the existing `link_to_causal_model` endpoint and before the `# Scene claims endpoints` section:

```python
# ---------------------------------------------------------------------------
# Analysis endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/{narrative_id}/analyse",
    response_model=AnalyseNarrativeResponse,
)
async def analyse_narrative(
    narrative_id: str,
    service: NarrativeAnalysisService = Depends(get_narrative_analysis_service_async),
) -> AnalyseNarrativeResponse:
    """Analyses all scenes in the Narrative and returns suggested actors and claims.

    Does not persist anything — the caller confirms actors/claims via separate endpoints.
    Raises NarrativeNotFoundError (→ 404) if the Narrative does not exist.
    """
    result = await service.analyse(narrative_id)
    return _to_analyse_response(result)


@router.post(
    "/{narrative_id}/suggest-wirkgefuege",
    response_model=SuggestWirkgefuegeResponse,
)
async def suggest_wirkgefuege(
    narrative_id: str,
    service: WirkgefuegeSuggestionService = Depends(get_wirkgefuege_suggestion_service),
) -> SuggestWirkgefuegeResponse:
    """Suggests a minimal Wirkgefüge from all DRAFT Claims of the Narrative.

    Does not persist anything — the caller creates slots/relations via separate endpoints.
    Returns empty suggestions when no DRAFT Claims exist.
    Raises NarrativeNotFoundError (→ 404) if the Narrative does not exist.
    """
    result = await service.suggest_for_narrative(narrative_id)
    return _to_suggest_response(result)
```

- [ ] **Step 7: Run router tests to verify they pass**

```bash
api/.venv/bin/pytest api/tests/test_narratives_router.py -v -k "analyse or suggest"
```
Expected: `4 passed`

- [ ] **Step 8: Run full suite**

```bash
api/.venv/bin/klartext test
```
Expected: all passing

- [ ] **Step 9: Commit**

```bash
git add api/exceptions/narrative.py api/schemas/narratives.py api/routers/narratives.py api/dependencies.py api/tests/test_narratives_router.py
git commit -m "feat: add /analyse and /suggest-wirkgefuege endpoints to narratives router"
```

---

## Task 6: Claude providers + integration tests

**Files:**
- Create: `api/providers/claude_narrative_analysis_provider.py`
- Create: `api/providers/claude_wirkgefuege_suggestion_provider.py`
- Create: `api/tests/test_claude_narrative_analysis_provider.py`
- Create: `api/tests/test_claude_wirkgefuege_suggestion_provider.py`

Context on existing patterns:
- `api/providers/claude_claim_extraction_provider.py` — the reference implementation
- It uses `anthropic.AsyncAnthropic` client, calls `messages.create`, strips code fences, parses JSON
- Integration test is in `api/tests/test_claude_claim_extraction_provider.py` (marked `@pytest.mark.integration`)
- The Anthropic client is injected via constructor so tests can provide mocks

Existing enum values (for prompts):
- `ActorType`: `individual | organisation | group | institution | abstract_entity`
- `ClaimType`: `empirical | causal | definitional | normative | prognostic | counterfactual | methodological | uncertainty`
- `SlotType`: `physical_quantity | social_quantity | entity_state | trend | process`
- `EpistemicStatus`: `incomplete | axiomatic`

- [ ] **Step 1: Write the integration tests first**

`api/tests/test_claude_narrative_analysis_provider.py`:

```python
"""Integration test for ClaudeNarrativeAnalysisProvider.

Requires a real Anthropic API key (ANTHROPIC_API_KEY environment variable).
Run with: pytest -m integration
"""

from __future__ import annotations

import pytest

from api.models.narrative import Narrative, Scene
from api.providers.narrative_analysis_provider import NarrativeAnalysisResult


@pytest.mark.integration
@pytest.mark.asyncio
async def test_claude_narrative_analysis_provider_returns_actors_and_claims() -> None:
    """Calls the real Claude API. Expects at least one actor and one claim to be returned."""
    import os

    import anthropic

    from api.providers.claude_narrative_analysis_provider import (
        ClaudeNarrativeAnalysisProvider,
    )

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    provider = ClaudeNarrativeAnalysisProvider(client=client)

    narrative = Narrative(id="test-id", title="Inflation Test")
    scene = Scene(
        id="scene-1",
        title="Scene 1",
        text=(
            "Die Europäische Zentralbank erhöhte die Zinsen auf 4 Prozent. "
            "Ökonomen erwarten dass höhere Zinsen die Inflation dämpfen werden, "
            "weil Kredite teurer werden und die Nachfrage sinkt."
        ),
        position=1,
    )
    narrative.add_scene(scene)

    result = await provider.analyse(narrative)

    assert isinstance(result, NarrativeAnalysisResult)
    assert len(result.actors) >= 1
    assert len(result.claims) >= 1
    assert all(a.label for a in result.actors)
    assert all(c.confidence >= 0.0 for c in result.claims)
    assert all(c.confidence <= 1.0 for c in result.claims)
```

`api/tests/test_claude_wirkgefuege_suggestion_provider.py`:

```python
"""Integration test for ClaudeWirkgefuegeSuggestionProvider.

Requires a real Anthropic API key (ANTHROPIC_API_KEY environment variable).
Run with: pytest -m integration
"""

from __future__ import annotations

import pytest

from api.providers.wirkgefuege_suggestion_provider import WirkgefuegeSuggestionResult


@pytest.mark.integration
@pytest.mark.asyncio
async def test_claude_wirkgefuege_suggestion_provider_returns_slots_and_relations() -> None:
    """Calls the real Claude API. Expects at least one slot and one relation."""
    import os

    import anthropic

    from api.models.claim import Claim, ClaimType
    from api.providers.claude_wirkgefuege_suggestion_provider import (
        ClaudeWirkgefuegeSuggestionProvider,
    )

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    provider = ClaudeWirkgefuegeSuggestionProvider(client=client)

    claims = [
        Claim(
            id="claim-1",
            label="Interest rate hikes dampen demand",
            text="Higher interest rates reduce consumer demand because loans become more expensive.",
            typ=ClaimType.CAUSAL,
            confidence=0.85,
        ),
        Claim(
            id="claim-2",
            label="Reduced demand lowers inflation",
            text="Lower consumer demand reduces price pressure and thereby lowers inflation.",
            typ=ClaimType.CAUSAL,
            confidence=0.80,
        ),
    ]

    result = await provider.suggest(claims)

    assert isinstance(result, WirkgefuegeSuggestionResult)
    assert len(result.suggested_slots) >= 2
    assert len(result.suggested_relations) >= 1
    assert all(s.identifier for s in result.suggested_slots)
    assert all(r.source and r.target for r in result.suggested_relations)
    # All source/target identifiers must reference a suggested slot
    slot_identifiers = {s.identifier for s in result.suggested_slots}
    for rel in result.suggested_relations:
        assert rel.source in slot_identifiers
        assert rel.target in slot_identifiers
```

- [ ] **Step 2: Verify tests fail (providers don't exist yet)**

```bash
api/.venv/bin/pytest api/tests/test_claude_narrative_analysis_provider.py api/tests/test_claude_wirkgefuege_suggestion_provider.py -m integration -v
```
Expected: `ImportError` — modules don't exist yet.

- [ ] **Step 3: Create ClaudeNarrativeAnalysisProvider**

`api/providers/claude_narrative_analysis_provider.py`:

```python
"""Adapter: analyses a Narrative by calling the Claude API."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from api.exceptions.narrative import NarrativeAnalysisError
from api.models.narrative import ActorType, Narrative
from api.models.claim import ClaimType
from api.providers.narrative_analysis_provider import (
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
    WirkgefuegeSuggestion,
)

_ACTOR_TYPES = " | ".join(t.value for t in ActorType)
_CLAIM_TYPES = " | ".join(t.value for t in ClaimType)

_SYSTEM_PROMPT = f"""Du bist ein Experte für die strukturierte Analyse politischer und wissenschaftlicher Narrative.

Deine Aufgabe: Analysiere den vollständigen Narrativ-Text und extrahiere Akteure und Claims.

Antworte ausschließlich mit einem JSON-Objekt mit zwei Feldern:

"actors": Array von Objekten mit:
- "label": Name oder Bezeichnung des Akteurs
- "actor_type": Einer von: {_ACTOR_TYPES}
- "occurrences": Array von Szenen-Titeln in denen der Akteur vorkommt
- "entity_suggestion": Englischer snake_case-Bezeichner für ein Kausalmodell-Element (z.B. "central_bank"), null falls unbekannt

"claims": Array von Objekten mit:
- "label": Kurzer englischer Titel (max. 80 Zeichen)
- "text": Die extrahierte Aussage (vollständiger Satz, max. 200 Zeichen)
- "claim_type": Einer von: {_CLAIM_TYPES}
- "confidence": Float zwischen 0.0 und 1.0
- "wirkgefuege_suggestion": null oder Objekt mit:
  - "type": "slot_zustand" oder "causal_relation"
  - Für "slot_zustand": "slot" (snake_case, englisch), "zustand" (Zustandsbeschreibung)
  - Für "causal_relation": "source_slot", "source_condition", "target_slot", "target_effect", "mechanism" (alles snake_case/englisch)

Maximal 5 Akteure und 10 Claims. Nur was explizit oder klar implizit im Text vorhanden ist."""


class ClaudeNarrativeAnalysisProvider(NarrativeAnalysisProvider):
    """Calls the Claude API to analyse a Narrative and return actor and claim suggestions.

    The Anthropic client is injected via the constructor so that tests can
    supply a mock without patching module-level imports.
    """

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def analyse(self, narrative: Narrative) -> NarrativeAnalysisResult:
        """Sends all scene texts to Claude and returns parsed actor and claim suggestions."""
        narrative_text = self._format_narrative(narrative)

        message = await self._client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Analysiere folgenden Narrativ:\n\n{narrative_text}",
                }
            ],
        )

        first_block = message.content[0]
        if not isinstance(first_block, anthropic.types.TextBlock):
            raise NarrativeAnalysisError(
                f"Unexpected content block type from Claude API: {type(first_block)}"
            )

        raw = self._strip_code_fences(first_block.text.strip())

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise NarrativeAnalysisError(
                f"Claude API returned invalid JSON: {e}"
            ) from e

        if not isinstance(parsed, dict):
            raise NarrativeAnalysisError(
                f"Claude API returned unexpected type: {type(parsed)}"
            )

        return NarrativeAnalysisResult(
            actors=[self._parse_actor(a) for a in parsed.get("actors", [])],
            claims=[self._parse_claim(c) for c in parsed.get("claims", [])],
        )

    def _format_narrative(self, narrative: Narrative) -> str:
        """Formats all scenes into a single text block with scene headers."""
        parts = [f"# {narrative.title}"]
        for scene in narrative.scenes:
            parts.append(f"\n## {scene.title}\n\n{scene.text}")
        return "\n".join(parts)

    def _strip_code_fences(self, text: str) -> str:
        """Removes markdown code fences that Claude sometimes wraps its response in."""
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return text.strip()

    def _parse_actor(self, record: dict[str, Any]) -> ActorSuggestion:
        """Converts a raw actor record to an ActorSuggestion.

        Falls back to 'abstract_entity' for unrecognised actor_type values.
        """
        try:
            ActorType(record.get("actor_type", ""))
            actor_type = record["actor_type"]
        except ValueError:
            actor_type = "abstract_entity"
        return ActorSuggestion(
            label=record.get("label", "Unknown"),
            actor_type=actor_type,
            occurrences=record.get("occurrences", []),
            entity_suggestion=record.get("entity_suggestion"),
        )

    def _parse_claim(self, record: dict[str, Any]) -> ClaimSuggestion:
        """Converts a raw claim record to a ClaimSuggestion.

        Falls back to 'empirical' for unrecognised claim_type values.
        Clamps confidence to 0.0–1.0.
        """
        try:
            ClaimType(record.get("claim_type", ""))
            claim_type = record["claim_type"]
        except ValueError:
            claim_type = "empirical"

        confidence = max(0.0, min(1.0, float(record.get("confidence", 0.5))))

        raw_ws = record.get("wirkgefuege_suggestion")
        wirkgefuege_suggestion = self._parse_wirkgefuege_suggestion(raw_ws) if raw_ws else None

        return ClaimSuggestion(
            label=record.get("label") or record.get("text", "")[:80],
            text=record.get("text", ""),
            claim_type=claim_type,
            confidence=confidence,
            wirkgefuege_suggestion=wirkgefuege_suggestion,
        )

    def _parse_wirkgefuege_suggestion(self, record: dict[str, Any]) -> WirkgefuegeSuggestion:
        """Converts a raw wirkgefuege_suggestion record to a WirkgefuegeSuggestion."""
        return WirkgefuegeSuggestion(
            suggestion_type=record.get("type", "slot_zustand"),
            slot=record.get("slot"),
            zustand=record.get("zustand"),
            source_slot=record.get("source_slot"),
            source_condition=record.get("source_condition"),
            target_slot=record.get("target_slot"),
            target_effect=record.get("target_effect"),
            mechanism=record.get("mechanism"),
        )
```

- [ ] **Step 4: Create ClaudeWirkgefuegeSuggestionProvider**

`api/providers/claude_wirkgefuege_suggestion_provider.py`:

```python
"""Adapter: suggests a minimal Wirkgefüge from Claims by calling the Claude API."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from api.exceptions.narrative import WirkgefuegeSuggestionError
from api.models.causal_model import EpistemicStatus, SlotType
from api.models.claim import Claim
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionProvider,
    WirkgefuegeSuggestionResult,
)

_SLOT_TYPES = " | ".join(t.value for t in SlotType)
_EPISTEMIC_STATUSES = " | ".join(t.value for t in EpistemicStatus)

_SYSTEM_PROMPT = f"""Du bist ein Experte für kausale Modellierung.

Gegeben eine Liste von Claims, erstelle ein minimales Wirkgefüge.

Antworte ausschließlich mit einem JSON-Objekt:

"suggested_slots": Array von Objekten mit:
- "identifier": Englischer snake_case-Bezeichner (z.B. "co2_emissions")
- "slot_type": Einer von: {_SLOT_TYPES}

"suggested_relations": Array von Objekten mit:
- "source": Quell-Slot Bezeichner (muss in suggested_slots vorkommen)
- "target": Ziel-Slot Bezeichner (muss in suggested_slots vorkommen)
- "source_condition": Zustandsbeschreibung des Quell-Slots (optional, null)
- "target_effect": Effekt auf den Ziel-Slot (optional, null)
- "mechanism": Kausaler Mechanismus (optional, null)
- "epistemic_status": Einer von: {_EPISTEMIC_STATUSES}

"from_claims": Array der Claim-IDs die zu den Vorschlägen beigetragen haben

Minimale Repräsentation — nur die wichtigsten Slots und Relationen.
Jeder Slot in suggested_relations muss in suggested_slots definiert sein."""


class ClaudeWirkgefuegeSuggestionProvider(WirkgefuegeSuggestionProvider):
    """Calls the Claude API to suggest a minimal Wirkgefüge from a list of Claims.

    The Anthropic client is injected via the constructor so that tests can
    supply a mock without patching module-level imports.
    """

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def suggest(self, claims: list[Claim]) -> WirkgefuegeSuggestionResult:
        """Sends the claims to Claude and returns a suggested Wirkgefüge."""
        claims_text = self._format_claims(claims)

        message = await self._client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Schlage ein Wirkgefüge für folgende Claims vor:\n\n{claims_text}",
                }
            ],
        )

        first_block = message.content[0]
        if not isinstance(first_block, anthropic.types.TextBlock):
            raise WirkgefuegeSuggestionError(
                f"Unexpected content block type from Claude API: {type(first_block)}"
            )

        raw = self._strip_code_fences(first_block.text.strip())

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise WirkgefuegeSuggestionError(
                f"Claude API returned invalid JSON: {e}"
            ) from e

        if not isinstance(parsed, dict):
            raise WirkgefuegeSuggestionError(
                f"Claude API returned unexpected type: {type(parsed)}"
            )

        return WirkgefuegeSuggestionResult(
            suggested_slots=[
                self._parse_slot(s) for s in parsed.get("suggested_slots", [])
            ],
            suggested_relations=[
                self._parse_relation(r) for r in parsed.get("suggested_relations", [])
            ],
            from_claims=parsed.get("from_claims", [c.id for c in claims if c.id]),
        )

    def _format_claims(self, claims: list[Claim]) -> str:
        """Formats claims as a numbered list with ID, label, text and type."""
        lines = []
        for i, claim in enumerate(claims, 1):
            lines.append(
                f"{i}. ID: {claim.id}\n"
                f"   Label: {claim.label}\n"
                f"   Text: {claim.text}\n"
                f"   Type: {claim.typ.value}"
            )
        return "\n\n".join(lines)

    def _strip_code_fences(self, text: str) -> str:
        """Removes markdown code fences that Claude sometimes wraps its response in."""
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return text.strip()

    def _parse_slot(self, record: dict[str, Any]) -> SuggestedSlot:
        """Converts a raw slot record to a SuggestedSlot.

        Falls back to 'entity_state' for unrecognised slot_type values.
        """
        try:
            SlotType(record.get("slot_type", ""))
            slot_type = record["slot_type"]
        except ValueError:
            slot_type = "entity_state"
        return SuggestedSlot(
            identifier=record.get("identifier", "unknown"),
            slot_type=slot_type,
        )

    def _parse_relation(self, record: dict[str, Any]) -> SuggestedRelation:
        """Converts a raw relation record to a SuggestedRelation.

        Falls back to 'incomplete' for unrecognised epistemic_status values.
        """
        try:
            EpistemicStatus(record.get("epistemic_status", ""))
            epistemic_status = record["epistemic_status"]
        except ValueError:
            epistemic_status = "incomplete"
        return SuggestedRelation(
            source=record.get("source", ""),
            target=record.get("target", ""),
            source_condition=record.get("source_condition"),
            target_effect=record.get("target_effect"),
            mechanism=record.get("mechanism"),
            epistemic_status=epistemic_status,
        )
```

- [ ] **Step 5: Run integration tests**

```bash
api/.venv/bin/klartext test --integration
```
Expected: `test_claude_narrative_analysis_provider_*` and `test_claude_wirkgefuege_suggestion_provider_*` pass. The 2 pre-existing Anthropic API failures (`test_claude_claim_extraction_provider`, `test_consistency_checker`) may still fail if `ANTHROPIC_API_KEY` is not set or blocked.

- [ ] **Step 6: Run full unit test suite**

```bash
api/.venv/bin/klartext test
```
Expected: all passing

- [ ] **Step 7: Commit**

```bash
git add api/providers/claude_narrative_analysis_provider.py \
        api/providers/claude_wirkgefuege_suggestion_provider.py \
        api/tests/test_claude_narrative_analysis_provider.py \
        api/tests/test_claude_wirkgefuege_suggestion_provider.py
git commit -m "feat: add Claude providers for narrative analysis and Wirkgefüge suggestion"
```

---

## Task 7: Full regression run

**Files:** None new — verification only.

- [ ] **Step 1: Run all unit tests**

```bash
api/.venv/bin/klartext test
```
Expected: all unit tests passing (435+ tests)

- [ ] **Step 2: Run integration tests**

```bash
api/.venv/bin/klartext test --integration
```
Expected: all Supabase integration tests passing; Anthropic API tests pass if `ANTHROPIC_API_KEY` is set.

- [ ] **Step 3: Update PENDING.md**

Open `docs/superpowers/plans/PENDING.md` and mark Plan D as DONE, add date.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/PENDING.md
git commit -m "docs: mark Plan D complete"
```

---

## Self-Review Checklist

### Spec coverage

From `experiment_scope.md`:

| Requirement | Task |
|---|---|
| `POST /narratives/{id}/analyse` → actors + claims | Task 5 |
| Claims with `wirkgefuege_suggestion` (slot_zustand / causal_relation) | Task 1, 5, 6 |
| Actors with `entity_suggestion` | Task 1, 5, 6 |
| `POST /narratives/{id}/suggest-wirkgefuege` | Task 5 |
| Suggestion aggregates DRAFT claims | Task 4 |
| Suggestion returns `from_claims` | Task 3, 4, 6 |
| Claude API for analysis | Task 6 |
| Claude API for suggestion | Task 6 |
| No persistence (suggestions only) | Task 2, 4 |

All spec requirements covered. ✅

### What this plan does NOT cover (out of scope for Plan D)

- Frontend extensions (separate plan after this)
- Steps 3 and 5 (confirm actors/claims, adjust slots/relations) use existing endpoints from Plans B+C — no new code needed
- Step 6 (save CausalModel) uses existing endpoints from Plan C — no new code needed
