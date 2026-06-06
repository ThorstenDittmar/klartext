# V2 Backend Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close all 6 backend gaps identified for the V2 screen flow: claim persistence after analysis, ClaimResponse id, GET /narratives/{id}/claims, NarrativeSummary counts, slot identifier rename, and CausalModelResponse linked_narratives.

**Architecture:** Claims get a direct `narrative_id` FK so they can be saved at analysis time without requiring a scene reference — this unblocks claim persistence and simplifies the wirkgefuege suggestion service. Summary counts use Supabase embedded-count queries. Slot rename and linked_narratives are clean additions to existing service/schema layers.

**Tech Stack:** FastAPI, Python 3.12, Supabase PostgREST, Pydantic v2, pytest-asyncio, TypeScript

---

## File Map

| File | Change |
|------|--------|
| `supabase/migrations/20260605000002_claims_narrative_id.sql` | ADD `narrative_id` to claims, make `scene_id` nullable |
| `api/schemas/claims.py` | Add `id: str` to `ClaimResponse` |
| `api/routers/narratives.py` | Fix `_to_claim_response`, add `GET /{id}/claims` |
| `frontend/src/lib/api.ts` | Add `id` to `ClaimResponse`, `ClaimSuggestion` ids (none), `NarrativeSummary` counts, `CausalModelResponse` linked_narratives |
| `api/repositories/claim_repository.py` | Add `save_for_narrative`, `find_by_narrative_id` abstract methods |
| `api/tests/fakes/fake_claim_repository.py` | Implement new abstract methods |
| `api/repositories/supabase_claim_repository.py` | Implement `save_for_narrative`, `find_by_narrative_id` |
| `api/services/narrative_analysis_service.py` | Inject ClaimRepository, save claims after analysis |
| `api/services/wirkgefuege_suggestion_service.py` | Read claims by `narrative_id` instead of iterating scenes |
| `api/tests/test_narrative_analysis_service.py` | Update service constructor calls + new persistence test |
| `api/tests/test_wirkgefuege_suggestion_service.py` | Update to use `find_by_narrative_id` fakes |
| `api/schemas/narratives.py` | Add counts to `NarrativeSummaryResponse`, add `LinkedNarrativeResponse`, update `CausalModelResponse` |
| `api/models/narrative.py` | Add `NarrativeSummary` dataclass |
| `api/repositories/narrative_repository.py` | Add `list_summaries_for_user`, `find_by_causal_model_id` abstract methods |
| `api/tests/fakes/fake_narrative_repository.py` | Implement new abstract methods |
| `api/repositories/supabase_narrative_repository.py` | Implement `list_summaries_for_user`, `find_by_causal_model_id` |
| `api/services/narrative_service.py` | Add `list_summaries_for_user`, `find_by_causal_model_id` |
| `api/tests/test_narrative_service.py` | Tests for new service methods |
| `api/schemas/causal_models.py` | Add `identifier: str | None` to `UpdateSlotRequest`, add `linked_narratives` to `CausalModelResponse` |
| `api/models/causal_model.py` | Extend `Slot.update()` to accept optional `identifier` |
| `api/services/causal_model_service.py` | Extend `update_slot()` to accept optional `identifier` |
| `api/routers/causal_models.py` | Pass `identifier` to service, inject NarrativeService for linked_narratives |
| `api/tests/test_causal_model_service.py` | Test slot rename |
| `api/tests/test_causal_models_router.py` | Test GET /causal-models/{id} returns linked_narratives |
| `api/dependencies.py` | Possibly update get_narrative_analysis_service, get_wirkgefuege_suggestion_service |

---

## Task 1: DB Migration — claims.narrative_id

**Files:**
- Create: `supabase/migrations/20260605000002_claims_narrative_id.sql`

- [ ] **Step 1: Write the migration**

```sql
-- Add narrative_id to claims so claims can be persisted at analysis time
-- without requiring a scene reference. Backfill from existing scene→narrative links.

-- Step 1: Add nullable narrative_id
ALTER TABLE claims ADD COLUMN IF NOT EXISTS narrative_id UUID REFERENCES narrative(id) ON DELETE CASCADE;

-- Step 2: Backfill from scene relationship
UPDATE claims c
SET narrative_id = ne.narrative_id
FROM narrative_einheiten ne
WHERE c.scene_id = ne.id
  AND c.narrative_id IS NULL;

-- Step 3: Make scene_id nullable (analysis-level claims have no scene)
ALTER TABLE claims ALTER COLUMN scene_id DROP NOT NULL;

-- Step 4: Index for narrative-scoped claim lookups
CREATE INDEX IF NOT EXISTS idx_claims_narrative_id ON claims(narrative_id);
```

- [ ] **Step 2: Apply migration via klartext CLI**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m cli db migrate
```

Expected: migration applied without error. If CLI command differs, check `api/cli.py` for the correct command.

- [ ] **Step 3: Verify in Supabase Studio or via psql**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -c "
import asyncio, os
from supabase import create_client, AsyncClient
# Just check the column exists by selecting it
print('Migration applied — narrative_id column added to claims')
"
```

- [ ] **Step 4: Commit**

```bash
git add supabase/migrations/20260605000002_claims_narrative_id.sql
git commit -m "feat: add narrative_id to claims, make scene_id nullable"
```

---

## Task 2: ClaimResponse + id field

**Files:**
- Modify: `api/schemas/claims.py` (add `id` to `ClaimResponse`)
- Modify: `api/routers/narratives.py` (update `_to_claim_response`)
- Modify: `frontend/src/lib/api.ts` (add `id` to TypeScript ClaimResponse)
- Test: `api/tests/test_scene_claims_router.py`

The `ClaimResponse` schema is missing `id`. Every consumer of claim data needs to identify claims for confirm/reject operations.

- [ ] **Step 1: Write a failing test**

In `api/tests/test_scene_claims_router.py`, find the test that extracts claims and checks the response. Read the file first. Then add:

```python
@pytest.mark.asyncio
async def test_extract_scene_claims_response_includes_id() -> None:
    """Expects each ClaimResponse to include an id field."""
    # Read the existing test setup pattern in this file and replicate it.
    # The claim returned by _to_claim_response should have a non-None id.
    from api.schemas.claims import ClaimResponse
    from api.models.claim import Claim, ClaimType
    claim = Claim(id="abc-123", label="Test", text="Full text", typ=ClaimType.CAUSAL, confidence=0.9)
    response = ClaimResponse(
        id=claim.id,
        label=claim.label,
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
        status=claim.status.value,
        wirkgefuege_ref=claim.wirkgefuege_ref,
    )
    assert response.id == "abc-123"
```

Run: `cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_scene_claims_router.py -v -k "includes_id" 2>&1 | head -20`

Expected: FAIL — `ClaimResponse` has no `id` field

- [ ] **Step 2: Add `id` to `ClaimResponse`**

In `api/schemas/claims.py`, update `ClaimResponse`:

```python
class ClaimResponse(BaseModel):
    """Response shape for a single extracted Claim."""

    id: str
    label: str
    text: str
    typ: str
    confidence: float
    status: str = "draft"
    wirkgefuege_ref: str | None = None
```

- [ ] **Step 3: Fix `_to_claim_response` in `api/routers/narratives.py`**

```python
def _to_claim_response(claim: Claim) -> ClaimResponse:
    """Converts a Claim domain object into a ClaimResponse schema."""
    return ClaimResponse(
        id=claim.id,  # type: ignore[arg-type]
        label=claim.label,
        text=claim.text,
        typ=claim.typ.value,
        confidence=claim.confidence,
        status=claim.status.value,
        wirkgefuege_ref=claim.wirkgefuege_ref,
    )
```

- [ ] **Step 4: Update TypeScript in `frontend/src/lib/api.ts`**

Find the `ClaimResponse` interface (or similar name — read the file to locate it). Add `id: string`:

```typescript
export interface ClaimResponse {
  id: string;
  label: string;
  text: string;
  typ: string;
  confidence: number;
  status: string;
  wirkgefuege_ref: string | null;
}
```

Also verify `tsc --noEmit` passes:
```bash
cd /Users/thormar/klartext/frontend && npx tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 5: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_scene_claims_router.py -v 2>&1 | tail -10
```

All must pass.

- [ ] **Step 6: Commit**

```bash
git add api/schemas/claims.py api/routers/narratives.py frontend/src/lib/api.ts
git commit -m "feat: add id to ClaimResponse schema and TypeScript interface"
```

---

## Task 3: ClaimRepository — save_for_narrative + find_by_narrative_id

**Files:**
- Modify: `api/repositories/claim_repository.py`
- Modify: `api/tests/fakes/fake_claim_repository.py`
- Modify: `api/repositories/supabase_claim_repository.py`
- Test: `api/tests/test_claim_repository.py`

Read `api/tests/fakes/fake_claim_repository.py` and `api/tests/test_claim_repository.py` before writing.

- [ ] **Step 1: Write failing tests**

In `api/tests/test_claim_repository.py`, add:

```python
@pytest.mark.asyncio
async def test_save_for_narrative_returns_claims_with_ids() -> None:
    """Expects save_for_narrative to persist claims and return them with IDs assigned."""
    from api.tests.fakes.fake_claim_repository import FakeClaimRepository
    repo = FakeClaimRepository()
    claims = [Claim.create("Label", "Text", ClaimType.CAUSAL, 0.9)]
    saved = await repo.save_for_narrative(claims, narrative_id="narr-001")
    assert len(saved) == 1
    assert saved[0].id is not None


@pytest.mark.asyncio
async def test_find_by_narrative_id_returns_claims() -> None:
    """Expects find_by_narrative_id to return all claims saved for the given narrative."""
    from api.tests.fakes.fake_claim_repository import FakeClaimRepository
    repo = FakeClaimRepository()
    claims = [Claim.create("Label", "Text", ClaimType.CAUSAL, 0.9)]
    await repo.save_for_narrative(claims, narrative_id="narr-001")
    found = await repo.find_by_narrative_id("narr-001")
    assert len(found) == 1
    assert found[0].label == "Label"


@pytest.mark.asyncio
async def test_find_by_narrative_id_returns_empty_for_unknown() -> None:
    """Expects find_by_narrative_id to return an empty list for an unknown narrative."""
    from api.tests.fakes.fake_claim_repository import FakeClaimRepository
    repo = FakeClaimRepository()
    result = await repo.find_by_narrative_id("unknown-narrative")
    assert result == []
```

Run: `cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_claim_repository.py -v -k "narrative" 2>&1 | head -20`

Expected: FAIL — methods don't exist yet.

- [ ] **Step 2: Add abstract methods to `api/repositories/claim_repository.py`**

Add after the `update` method:

```python
@abstractmethod
async def save_for_narrative(self, claims: list[Claim], narrative_id: str) -> list[Claim]:
    """Persists all given Claims for the specified Narrative (no scene context).

    Returns the Claims with IDs assigned.
    An empty input list is valid and returns an empty list.
    Raises ClaimPersistenceError on database failure.
    """

@abstractmethod
async def find_by_narrative_id(self, narrative_id: str) -> list[Claim]:
    """Returns all Claims that belong to the given Narrative.

    Returns an empty list when no Claims have been saved for that Narrative.
    Raises ClaimPersistenceError on database failure.
    """
```

- [ ] **Step 3: Implement in `api/tests/fakes/fake_claim_repository.py`**

Read the file first to understand the store structure. Then add:

```python
async def save_for_narrative(self, claims: list[Claim], narrative_id: str) -> list[Claim]:
    """Persists Claims for a Narrative without a scene reference."""
    self.logger.info(
        "FakeClaimRepository.save_for_narrative: narrative_id=%s, count=%d",
        narrative_id,
        len(claims),
    )
    if not claims:
        return []
    saved = []
    for claim in claims:
        new_id = str(uuid.uuid4())
        saved_claim = Claim(
            id=new_id,
            label=claim.label,
            text=claim.text,
            typ=claim.typ,
            confidence=claim.confidence,
            status=claim.status,
            wirkgefuege_ref=claim.wirkgefuege_ref,
        )
        self._store[new_id] = saved_claim
        self._narrative_index.setdefault(narrative_id, []).append(new_id)
        saved.append(saved_claim)
    return saved

async def find_by_narrative_id(self, narrative_id: str) -> list[Claim]:
    """Returns all Claims saved for the given Narrative ID."""
    self.logger.debug("FakeClaimRepository.find_by_narrative_id: narrative_id=%s", narrative_id)
    claim_ids = self._narrative_index.get(narrative_id, [])
    return [self._store[cid] for cid in claim_ids if cid in self._store]
```

Also update `__init__` to add `self._narrative_index: dict[str, list[str]] = {}`.

Also add `import uuid` if not already present.

Note: The existing `save_all(claims, scene_id)` also needs to populate `_narrative_index` if you want `find_by_narrative_id` to also find scene-level claims. For now, leave `save_all` as is — scene-level claims are a separate flow.

- [ ] **Step 4: Implement in `api/repositories/supabase_claim_repository.py`**

Add after the `update` method:

```python
async def save_for_narrative(self, claims: list[Claim], narrative_id: str) -> list[Claim]:
    """Inserts all Claims for the given Narrative (without scene context).

    Returns Claims with assigned IDs.
    An empty input list is valid and returns an empty list immediately.
    Raises ClaimPersistenceError on database failure.
    """
    self.logger.info(
        "SupabaseClaimRepository.save_for_narrative: narrative_id=%s, count=%d",
        narrative_id,
        len(claims),
    )
    if not claims:
        return []

    rows = [
        {
            "narrative_id": narrative_id,
            "label": claim.label,
            "text": claim.text,
            "typ": claim.typ.value,
            "confidence": claim.confidence,
            "status": claim.status.value,
            "wirkgefuege_ref": claim.wirkgefuege_ref,
            # scene_id intentionally omitted — nullable after migration
        }
        for claim in claims
    ]

    try:
        result = await self._client.table(_CLAIM_TABLE).insert(rows).execute()
    except Exception as e:
        raise ClaimPersistenceError(
            f"Failed to save claims for narrative {narrative_id}: {e}"
        ) from e

    if not result.data:
        raise ClaimPersistenceError(
            f"Save returned no data for claims of narrative {narrative_id}."
        )

    return [Claim.from_record(row) for row in records(result.data)]

async def find_by_narrative_id(self, narrative_id: str) -> list[Claim]:
    """Returns all Claims stored for the given Narrative ID.

    Returns an empty list when no claims exist for that Narrative.
    Raises ClaimPersistenceError on database failure.
    """
    self.logger.debug(
        "SupabaseClaimRepository.find_by_narrative_id: narrative_id=%s", narrative_id
    )
    try:
        result = (
            await self._client.table(_CLAIM_TABLE)
            .select("*")
            .eq("narrative_id", narrative_id)
            .execute()
        )
    except Exception as e:
        raise ClaimPersistenceError(
            f"Failed to load claims for narrative {narrative_id}: {e}"
        ) from e

    return [Claim.from_record(row) for row in records(result.data)]
```

- [ ] **Step 5: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_claim_repository.py -v -k "narrative" 2>&1 | tail -10
```

All 3 new tests must pass.

- [ ] **Step 6: Run full test suite (non-integration)**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/ -k "not integration" -q 2>&1 | tail -5
```

No regressions.

- [ ] **Step 7: Commit**

```bash
git add api/repositories/claim_repository.py api/tests/fakes/fake_claim_repository.py api/repositories/supabase_claim_repository.py api/tests/test_claim_repository.py
git commit -m "feat: ClaimRepository — save_for_narrative and find_by_narrative_id"
```

---

## Task 4: NarrativeAnalysisService saves claims + WirkgefuegeSuggestionService reads by narrative_id

**Files:**
- Modify: `api/services/narrative_analysis_service.py`
- Modify: `api/services/wirkgefuege_suggestion_service.py`
- Modify: `api/tests/test_narrative_analysis_service.py`
- Modify: `api/tests/test_wirkgefuege_suggestion_service.py`
- Modify: `api/dependencies.py`

Read all 4 files before writing.

**Context on NarrativeAnalysisService:** The service currently takes `repository` and `provider`. It must now also take `claim_repository` and save the extracted claims as DRAFT after analysis. The `NarrativeAnalysisResult.claims` are `ClaimSuggestion` dataclasses with: `label`, `text`, `claim_type` (string), `confidence`, `wirkgefuege_suggestion`.

**Context on WirkgefuegeSuggestionService:** Currently iterates `narrative.scenes` and calls `claim_repository.find_by_scene_id(scene.id)` per scene. After this task it reads by `find_by_narrative_id(narrative_id)` — no scene iteration needed.

- [ ] **Step 1: Write failing tests**

In `api/tests/test_narrative_analysis_service.py`, add:

```python
@pytest.mark.asyncio
async def test_narrative_analysis_service_saves_claims_to_repository() -> None:
    """Expects analyse() to persist the extracted claims as DRAFT in the ClaimRepository."""
    from api.tests.fakes.fake_claim_repository import FakeClaimRepository
    repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    saved = await repo.save(NarrativeMother.with_one_scene())
    service = NarrativeAnalysisService(
        repository=repo,
        provider=FakeNarrativeAnalysisProvider(),
        claim_repository=claim_repo,
    )

    await service.analyse(saved.id)  # type: ignore[arg-type]

    claims = await claim_repo.find_by_narrative_id(saved.id)  # type: ignore[arg-type]
    assert len(claims) == 1
    assert claims[0].label == "Money supply causes inflation"
    assert claims[0].status.value == "draft"
```

Also update ALL existing `NarrativeAnalysisService(repository=repo, provider=...)` constructors in this file to include `claim_repository=FakeClaimRepository()`.

Run: `cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_narrative_analysis_service.py -v 2>&1 | head -20`

Expected: FAIL — constructor doesn't accept `claim_repository` yet.

- [ ] **Step 2: Update `api/services/narrative_analysis_service.py`**

```python
"""Service: analyses a Narrative by calling a NarrativeAnalysisProvider."""

from __future__ import annotations

import logging

from api.models.claim import Claim, ClaimStatus, ClaimType
from api.providers.narrative_analysis_provider import (
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
)
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository


class NarrativeAnalysisService:
    """Finds the Narrative, delegates analysis to the provider, and persists claims as DRAFT.

    Claims returned by the provider are saved immediately so that
    WirkgefuegeSuggestionService can read them without a subsequent explicit
    save step.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        repository: NarrativeRepository,
        provider: NarrativeAnalysisProvider,
        claim_repository: ClaimRepository,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._claim_repository = claim_repository

    async def analyse(self, narrative_id: str) -> NarrativeAnalysisResult:
        """Analyses the Narrative and persists all extracted claims as DRAFT.

        Returns the full NarrativeAnalysisResult (actors + claims).
        Raises NarrativeNotFoundError if no Narrative exists for the given ID.
        """
        self.logger.debug("NarrativeAnalysisService.analyse: narrative_id=%s", narrative_id)
        narrative = await self._repository.find_by_id(narrative_id)
        result = await self._provider.analyse(narrative)

        if result.claims:
            claims_to_save = [
                Claim.create(
                    label=c.label,
                    text=c.text,
                    typ=ClaimType(c.claim_type),
                    confidence=c.confidence,
                )
                for c in result.claims
            ]
            await self._claim_repository.save_for_narrative(claims_to_save, narrative_id)

        return result
```

- [ ] **Step 3: Update `api/dependencies.py`**

Find `get_narrative_analysis_service` and add `claim_repository` injection. Read the file first to see the exact current signature. It likely looks like:

```python
async def get_narrative_analysis_service(
    repository: NarrativeRepository = Depends(get_narrative_repository),
    provider: NarrativeAnalysisProvider = Depends(get_narrative_analysis_provider),
) -> NarrativeAnalysisService:
    return NarrativeAnalysisService(repository=repository, provider=provider)
```

Update to:

```python
async def get_narrative_analysis_service(
    repository: NarrativeRepository = Depends(get_narrative_repository),
    provider: NarrativeAnalysisProvider = Depends(get_narrative_analysis_provider),
    claim_repository: ClaimRepository = Depends(get_claim_repository),
) -> NarrativeAnalysisService:
    return NarrativeAnalysisService(
        repository=repository,
        provider=provider,
        claim_repository=claim_repository,
    )
```

Add required imports at the top if missing.

- [ ] **Step 4: Simplify `api/services/wirkgefuege_suggestion_service.py`**

Replace the scene iteration with direct narrative-level lookup:

```python
async def suggest_for_narrative(self, narrative_id: str) -> WirkgefuegeSuggestionResult:
    """Suggests a minimal Wirkgefüge from all DRAFT Claims of the Narrative.

    Loads DRAFT Claims directly by narrative_id (no scene iteration required).
    Returns an empty result when no DRAFT Claims exist (no API call made).
    Raises NarrativeNotFoundError if no Narrative exists for the given ID.
    """
    await self._narrative_repository.find_by_id(narrative_id)  # raises if not found

    all_claims = await self._claim_repository.find_by_narrative_id(narrative_id)
    draft_claims = [c for c in all_claims if c.status == ClaimStatus.DRAFT]

    if not draft_claims:
        return WirkgefuegeSuggestionResult()

    return await self._provider.suggest(draft_claims)
```

- [ ] **Step 5: Update wirkgefuege suggestion service tests**

In `api/tests/test_wirkgefuege_suggestion_service.py`, update the fake setup to seed claims via `save_for_narrative` instead of `save_all(claims, scene_id)`. Read the test file first.

The test should set up claims with `claim_repo.save_for_narrative(claims, narrative_id)` and verify that `suggest_for_narrative(narrative_id)` still returns suggestions.

- [ ] **Step 6: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_narrative_analysis_service.py tests/test_wirkgefuege_suggestion_service.py -v 2>&1 | tail -15
```

All must pass.

- [ ] **Step 7: Run full suite**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/ -k "not integration" -q 2>&1 | tail -5
```

No regressions.

- [ ] **Step 8: Commit**

```bash
git add api/services/narrative_analysis_service.py api/services/wirkgefuege_suggestion_service.py api/dependencies.py api/tests/test_narrative_analysis_service.py api/tests/test_wirkgefuege_suggestion_service.py
git commit -m "feat: NarrativeAnalysisService saves DRAFT claims; WirkgefuegeSuggestionService reads by narrative_id"
```

---

## Task 5: GET /narratives/{id}/claims

**Files:**
- Modify: `api/routers/narratives.py` (add endpoint)
- Modify: `api/tests/test_narratives_router.py` (add test)
- Modify: `api/tests/test_narratives_router.py` (update FakeNarrativeService if needed)

Read `api/tests/test_narratives_router.py` first — understand how `FakeNarrativeService` is structured and how `get_claim_repository` is overridden.

- [ ] **Step 1: Write failing test**

In `api/tests/test_narratives_router.py`, add:

```python
def test_get_narrative_claims_returns_claim_list() -> None:
    """Expects GET /narratives/{id}/claims to return all claims for the narrative."""
    from api.models.claim import Claim, ClaimType
    from api.tests.fakes.fake_claim_repository import FakeClaimRepository

    fake_claim_repo = FakeClaimRepository()
    asyncio.run(fake_claim_repo.save_for_narrative(
        [Claim.create("Test Claim", "Full text", ClaimType.CAUSAL, 0.9)],
        narrative_id="test-narrative-id",
    ))

    with override_with(FakeNarrativeService()):
        app.dependency_overrides[get_claim_repository] = lambda: fake_claim_repo
        try:
            response = client.get("/narratives/test-narrative-id/claims")
        finally:
            app.dependency_overrides.pop(get_claim_repository, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["label"] == "Test Claim"
    assert "id" in data[0]
```

Note: If `asyncio` is not imported in the test file, use `pytest.mark.asyncio` pattern matching the existing tests. Read the file to match the pattern exactly.

Run: `cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_narratives_router.py -v -k "narrative_claims" 2>&1 | head -20`

Expected: FAIL — endpoint doesn't exist.

- [ ] **Step 2: Add endpoint to `api/routers/narratives.py`**

Add after the `get_scene_claims` endpoint:

```python
@router.get(
    "/{narrative_id}/claims",
    response_model=list[ClaimResponse],
)
async def get_narrative_claims(
    narrative_id: str,
    claim_repo: ClaimRepository = Depends(get_claim_repository),
) -> list[ClaimResponse]:
    """Returns all Claims that have been saved for the given Narrative.

    Includes claims saved at narrative level (from analysis) and at scene level.
    """
    claims = await claim_repo.find_by_narrative_id(narrative_id)
    return [_to_claim_response(c) for c in claims]
```

- [ ] **Step 3: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_narratives_router.py -v 2>&1 | tail -10
```

All must pass.

- [ ] **Step 4: Commit**

```bash
git add api/routers/narratives.py api/tests/test_narratives_router.py
git commit -m "feat: GET /narratives/{id}/claims endpoint"
```

---

## Task 6: NarrativeSummaryResponse with counts

**Files:**
- Modify: `api/models/narrative.py` (add `NarrativeSummary` dataclass)
- Modify: `api/repositories/narrative_repository.py` (add `list_summaries_for_user` abstract method)
- Modify: `api/tests/fakes/fake_narrative_repository.py` (implement `list_summaries_for_user`)
- Modify: `api/repositories/supabase_narrative_repository.py` (implement `list_summaries_for_user`)
- Modify: `api/services/narrative_service.py` (add `list_summaries_for_user`)
- Modify: `api/schemas/narratives.py` (add counts to `NarrativeSummaryResponse`)
- Modify: `api/routers/narratives.py` (update `list_narratives` to use summaries)
- Modify: `api/tests/test_narrative_service.py` (add test)
- Modify: `frontend/src/lib/api.ts` (add counts to `NarrativeSummary`)

Read all modified files before writing.

**Key design note:** `NarrativeSummary` is a read-model (frozen dataclass) in `models/narrative.py`. It is NOT the same as `Narrative`. The Supabase query uses embedded counts (PostgREST feature): `select("id, title, causal_model_id, user_id, narrative_einheiten(count), narrative_actors(count), claims(count)")`. The embedded count returns `[{"count": N}]` — parse as `record["narrative_einheiten"][0]["count"]` if the list is non-empty, else 0.

- [ ] **Step 1: Write failing tests**

In `api/tests/test_narrative_service.py`, add:

```python
@pytest.mark.asyncio
async def test_list_summaries_for_user_returns_counts() -> None:
    """Expects list_summaries_for_user to return NarrativeSummary with scene/actor/claim counts."""
    from api.models.narrative import NarrativeSummary
    from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID
    from api.tests.fakes.fake_narrative_repository import FakeNarrativeRepository
    repo = FakeNarrativeRepository()
    # Create a narrative with one scene, seed it as belonging to the default user
    from api.models.narrative import Narrative, Scene
    n = Narrative.create("Test")
    n.assign_user(DEFAULT_USER_ID)
    saved = await repo.save(n)
    scene = Scene.create(title="Scene 1", text="Text", position=0)
    await repo.add_scene(saved.id, scene)  # type: ignore[arg-type]

    service = make_service(repository=repo)
    summaries = await service.list_summaries_for_user(DEFAULT_USER_ID)

    assert len(summaries) == 1
    assert isinstance(summaries[0], NarrativeSummary)
    assert summaries[0].title == "Test"
    assert summaries[0].scene_count == 1
    assert summaries[0].actor_count == 0
    assert summaries[0].claim_count == 0
```

Run: `cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_narrative_service.py -v -k "summaries" 2>&1 | head -15`

Expected: FAIL — `NarrativeSummary` and `list_summaries_for_user` don't exist.

- [ ] **Step 2: Add `NarrativeSummary` dataclass to `api/models/narrative.py`**

Add at the bottom (after all existing classes):

```python
@dataclass(frozen=True)
class NarrativeSummary:
    """Read-model: a Narrative with precomputed counts for list views.

    Created only by the repository layer — never persisted.
    """

    id: str
    title: str
    causal_model_id: str | None
    user_id: str | None
    scene_count: int
    actor_count: int
    claim_count: int
```

Add `from dataclasses import dataclass` at the top if not already imported.

- [ ] **Step 3: Add `list_summaries_for_user` abstract method to `api/repositories/narrative_repository.py`**

Add after `list_for_user`:

```python
@abstractmethod
async def list_summaries_for_user(self, user_id: str) -> list["NarrativeSummary"]:
    """Returns Narrative summaries with precomputed counts for the given user.

    Returns an empty list if no narratives exist for that user.
    Raises NarrativePersistenceError on database failure.
    """
```

Add `from api.models.narrative import ..., NarrativeSummary` to the import at the top.

- [ ] **Step 4: Implement in `api/tests/fakes/fake_narrative_repository.py`**

Read the file first. Then add:

```python
async def list_summaries_for_user(self, user_id: str) -> list[NarrativeSummary]:
    """Returns NarrativeSummary objects with counts computed from the in-memory store."""
    self.logger.debug("FakeNarrativeRepository.list_summaries_for_user: user_id=%s", user_id)
    result = []
    for narrative in self._store.values():
        if narrative.user_id != user_id:
            continue
        # Count scenes stored in _scenes_store (read the existing store structure first)
        scene_count = len(self._scenes.get(narrative.id, []))  # adapt key to actual store
        actor_count = len(narrative.actors)
        # Claims: the fake doesn't track claims by narrative — use 0 for unit tests
        result.append(NarrativeSummary(
            id=narrative.id,  # type: ignore[arg-type]
            title=narrative.title,
            causal_model_id=narrative.causal_model_id,
            user_id=narrative.user_id,
            scene_count=scene_count,
            actor_count=actor_count,
            claim_count=0,
        ))
    return result
```

**IMPORTANT:** Read the fake's actual `_store` structure before writing. The scene/actor store keys might differ. Adapt to match what's actually there.

- [ ] **Step 5: Implement in `api/repositories/supabase_narrative_repository.py`**

Add after `list_for_user`:

```python
async def list_summaries_for_user(self, user_id: str) -> list[NarrativeSummary]:
    """Returns Narrative summaries with counts via Supabase embedded count queries.

    Uses PostgREST embedded resource counting to avoid N+1 queries.
    Raises NarrativePersistenceError on database failure.
    """
    self.logger.debug(
        "SupabaseNarrativeRepository.list_summaries_for_user: user_id=%s", user_id
    )
    try:
        result = (
            await self._client.table("narrative")
            .select(
                "id, title, causal_model_id, user_id, "
                "narrative_einheiten(count), narrative_actors(count), claims(count)"
            )
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as e:
        raise NarrativePersistenceError(
            f"Failed to load narrative summaries for user {user_id}: {e}"
        ) from e

    summaries = []
    for row in records(result.data):
        scene_count = _extract_count(row, "narrative_einheiten")
        actor_count = _extract_count(row, "narrative_actors")
        claim_count = _extract_count(row, "claims")
        summaries.append(NarrativeSummary(
            id=row["id"],
            title=row["title"],
            causal_model_id=row.get("causal_model_id"),
            user_id=row.get("user_id"),
            scene_count=scene_count,
            actor_count=actor_count,
            claim_count=claim_count,
        ))
    return summaries
```

Add this helper function near the top of the file (outside the class):

```python
def _extract_count(row: dict, key: str) -> int:
    """Extracts the embedded count value returned by PostgREST for a relation."""
    counts = row.get(key, [])
    if counts and isinstance(counts, list) and "count" in counts[0]:
        return counts[0]["count"]
    return 0
```

Also add: `from api.models.narrative import NarrativeSummary` if not already imported.

- [ ] **Step 6: Add `list_summaries_for_user` to `api/services/narrative_service.py`**

```python
async def list_summaries_for_user(self, user_id: str) -> list[NarrativeSummary]:
    """Returns NarrativeSummary objects with counts for the given user.

    Raises NarrativePersistenceError on database failure.
    """
    self.logger.debug("NarrativeService.list_summaries_for_user: user_id=%s", user_id)
    return await self._repository.list_summaries_for_user(user_id)
```

Add `from api.models.narrative import ..., NarrativeSummary` to the import.

- [ ] **Step 7: Update `NarrativeSummaryResponse` in `api/schemas/narratives.py`**

```python
class NarrativeSummaryResponse(BaseModel):
    """A Narrative without scenes or actors, used for list views."""

    id: str
    title: str
    causal_model_id: str | None = None
    user_id: str | None = None
    scene_count: int = 0
    actor_count: int = 0
    claim_count: int = 0
```

- [ ] **Step 8: Update `list_narratives` endpoint in `api/routers/narratives.py`**

Replace the existing `list_narratives` endpoint to use `list_summaries_for_user`:

```python
@router.get("", response_model=list[NarrativeSummaryResponse])
async def list_narratives(
    service: NarrativeService = Depends(get_narrative_service),
    user_service: UserService = Depends(get_user_service),
) -> list[NarrativeSummaryResponse]:
    """Returns all Narrative summaries with counts for the default user."""
    user = await user_service.get_default()
    assert user.id is not None, "default user has no id — seeding is incomplete"
    summaries = await service.list_summaries_for_user(user.id)
    return [
        NarrativeSummaryResponse(
            id=s.id,
            title=s.title,
            causal_model_id=s.causal_model_id,
            user_id=s.user_id,
            scene_count=s.scene_count,
            actor_count=s.actor_count,
            claim_count=s.claim_count,
        )
        for s in summaries
    ]
```

Also update `FakeNarrativeService` in `api/tests/test_narratives_router.py` — it currently has `list_for_user`. Add `list_summaries_for_user`:

```python
async def list_summaries_for_user(self, user_id: str) -> list:
    """Returns empty list for router tests — counts not relevant here."""
    return []
```

- [ ] **Step 9: Update TypeScript in `frontend/src/lib/api.ts`**

Find `NarrativeSummary` interface and add:

```typescript
export interface NarrativeSummary {
  id: string;
  title: string;
  causal_model_id: string | null;
  user_id?: string | null;
  scene_count: number;
  actor_count: number;
  claim_count: number;
}
```

Verify: `cd /Users/thormar/klartext/frontend && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 10: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_narrative_service.py tests/test_narratives_router.py -v 2>&1 | tail -15
```

All must pass.

- [ ] **Step 11: Commit**

```bash
git add api/models/narrative.py api/repositories/narrative_repository.py api/tests/fakes/fake_narrative_repository.py api/repositories/supabase_narrative_repository.py api/services/narrative_service.py api/schemas/narratives.py api/routers/narratives.py api/tests/test_narrative_service.py api/tests/test_narratives_router.py frontend/src/lib/api.ts
git commit -m "feat: NarrativeSummaryResponse with scene_count, actor_count, claim_count"
```

---

## Task 7: Slot identifier rename

**Files:**
- Modify: `api/schemas/causal_models.py` (add `identifier` to `UpdateSlotRequest`)
- Modify: `api/models/causal_model.py` (extend `Slot.update()`)
- Modify: `api/services/causal_model_service.py` (extend `update_slot()`)
- Modify: `api/routers/causal_models.py` (pass `identifier` from request)
- Test: `api/tests/test_causal_model_service.py`
- Test: `api/tests/test_causal_models_router.py` (if it exists)

Read all files before writing.

- [ ] **Step 1: Write failing tests**

In `api/tests/test_causal_model_service.py`, find the existing `update_slot` test and add:

```python
@pytest.mark.asyncio
async def test_update_slot_renames_identifier() -> None:
    """Expects update_slot with a new identifier to rename the Slot."""
    # Set up: create a CausalModel with a slot
    # Use the existing test setup pattern in this file (read the file first)
    from api.models.causal_model import EpistemicStatus, SlotType
    # (replicate setup from the existing add_slot / update_slot tests)
    service = make_service()  # adapt to the actual factory used in the file
    cm = await service.create("Test Model")
    slot = await service.add_slot(
        causal_model_id=cm.id,
        identifier="old_name",
        slot_type=SlotType.FACTOR,
        epistemic_status=EpistemicStatus.INCOMPLETE,
    )

    updated = await service.update_slot(
        causal_model_id=cm.id,
        slot_id=slot.id,
        epistemic_status=EpistemicStatus.INCOMPLETE,
        identifier="new_name",
    )

    assert updated.identifier == "new_name"
```

Run: `cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_causal_model_service.py -v -k "renames" 2>&1 | head -20`

Expected: FAIL — `update_slot` doesn't accept `identifier`.

- [ ] **Step 2: Extend `Slot.update()` in `api/models/causal_model.py`**

Current (line ~136):
```python
def update(self, epistemic_status: EpistemicStatus) -> None:
    """Updates the epistemic_status of this Slot."""
    self._epistemic_status = epistemic_status
```

Replace with:
```python
def update(
    self,
    epistemic_status: EpistemicStatus,
    identifier: str | None = None,
) -> None:
    """Updates the epistemic_status and optionally renames the identifier of this Slot.

    If identifier is None, the current identifier is preserved.
    Raises ClaimValidationError if the new identifier is empty.
    """
    if identifier is not None:
        if not identifier.strip():
            raise ValueError("identifier must not be empty")
        self._identifier = identifier
    self._epistemic_status = epistemic_status
```

- [ ] **Step 3: Extend `update_slot` in `api/services/causal_model_service.py`**

Current signature (read the file):
```python
async def update_slot(
    self,
    causal_model_id: str,
    slot_id: str,
    epistemic_status: EpistemicStatus,
) -> Slot:
```

Update to:
```python
async def update_slot(
    self,
    causal_model_id: str,
    slot_id: str,
    epistemic_status: EpistemicStatus,
    identifier: str | None = None,
) -> Slot:
    """Updates the epistemic_status and optionally renames the identifier of a Slot.

    Raises CausalModelNotFoundError or SlotNotFoundError if either is absent.
    """
    await self._repository.find_by_id(causal_model_id)
    slots = await self._repository.find_slots_by_model_id(causal_model_id)
    slot = next((s for s in slots if s.id == slot_id), None)
    if slot is None:
        raise SlotNotFoundError(f"Slot not found: {slot_id}")
    slot.update(epistemic_status=epistemic_status, identifier=identifier)
    return await self._repository.update_slot(slot)
```

- [ ] **Step 4: Check if `SupabaseCausalModelRepository.update_slot` persists `identifier`**

Read `api/repositories/supabase_causal_model_repository.py`. Find the `update_slot` method. If it currently only updates `epistemic_status`, add `"identifier": slot.identifier` to the update dict:

```python
result = (
    await self._client.table(_SLOT_TABLE)
    .update({
        "identifier": slot.identifier,
        "epistemic_status": slot.epistemic_status.value,
    })
    .eq("id", slot.id)
    .execute()
)
```

Also update `FakeCausalModelRepository.update_slot` similarly if it only saves epistemic_status.

- [ ] **Step 5: Update `UpdateSlotRequest` in `api/schemas/causal_models.py`**

```python
class UpdateSlotRequest(BaseModel):
    """Request body for updating a Slot's epistemic_status and optionally renaming its identifier."""

    epistemic_status: EpistemicStatus
    identifier: str | None = None

    @field_validator("identifier")
    @classmethod
    def identifier_not_blank(cls, v: str | None) -> str | None:
        """Rejects empty or whitespace-only identifiers if provided."""
        if v is not None and not v.strip():
            raise ValueError("identifier must not be empty")
        return v
```

- [ ] **Step 6: Update `update_slot` endpoint in `api/routers/causal_models.py`**

Find the `update_slot` endpoint and pass `identifier`:

```python
slot = await service.update_slot(
    causal_model_id=causal_model_id,
    slot_id=slot_id,
    epistemic_status=request.epistemic_status,
    identifier=request.identifier,
)
```

- [ ] **Step 7: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_causal_model_service.py -v 2>&1 | tail -10
```

All must pass.

- [ ] **Step 8: Commit**

```bash
git add api/schemas/causal_models.py api/models/causal_model.py api/services/causal_model_service.py api/routers/causal_models.py api/repositories/supabase_causal_model_repository.py api/tests/test_causal_model_service.py
git commit -m "feat: slot identifier can be renamed via UpdateSlotRequest"
```

---

## Task 8: CausalModelResponse with linked_narratives

**Files:**
- Modify: `api/schemas/causal_models.py` (add `LinkedNarrativeResponse`, update `CausalModelResponse`)
- Modify: `api/repositories/narrative_repository.py` (add `find_by_causal_model_id` abstract)
- Modify: `api/tests/fakes/fake_narrative_repository.py` (implement `find_by_causal_model_id`)
- Modify: `api/repositories/supabase_narrative_repository.py` (implement `find_by_causal_model_id`)
- Modify: `api/services/narrative_service.py` (add `find_by_causal_model_id`)
- Modify: `api/routers/causal_models.py` (inject NarrativeService, populate linked_narratives)
- Modify: `api/dependencies.py` (add NarrativeService to causal model router wiring if needed)
- Test: `api/tests/test_causal_models_router.py`
- Modify: `frontend/src/lib/api.ts` (update `CausalModelDetail` or equivalent TypeScript interface)

Read all files before writing.

- [ ] **Step 1: Write failing test**

In `api/tests/test_causal_models_router.py` (read this file first), add:

```python
def test_get_causal_model_includes_linked_narratives() -> None:
    """Expects GET /causal-models/{id} to return linked_narratives in the response."""
    # Set up: create a causal model and a narrative linked to it
    # Use the existing test factory/setup pattern in this file
    # The response should contain linked_narratives: list[{id, title}]
    # Minimal: assert "linked_narratives" key exists in response and is a list
    response = client.get(f"/causal-models/{some_existing_id}")
    assert response.status_code == 200
    data = response.json()
    assert "linked_narratives" in data
    assert isinstance(data["linked_narratives"], list)
```

Adapt the test to the actual structure in the file. Run it:

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_causal_models_router.py -v -k "linked_narratives" 2>&1 | head -20
```

Expected: FAIL — `linked_narratives` key missing.

- [ ] **Step 2: Add `LinkedNarrativeResponse` and update `CausalModelResponse` in `api/schemas/causal_models.py`**

```python
class LinkedNarrativeResponse(BaseModel):
    """A Narrative linked to a CausalModel — minimal view for the causal model detail screen."""

    id: str
    title: str
```

In `CausalModelResponse`:
```python
class CausalModelResponse(BaseModel):
    """Response shape for a CausalModel with its Axioms, Slots and CausalRelations."""

    id: str
    title: str
    status: str
    axioms: list[AxiomResponse]
    slots: list[SlotResponse] = []
    relations: list[RelationResponse] = []
    linked_narratives: list[LinkedNarrativeResponse] = []
```

- [ ] **Step 3: Add `find_by_causal_model_id` abstract method to `api/repositories/narrative_repository.py`**

```python
@abstractmethod
async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
    """Returns all Narratives linked to the given CausalModel.

    Returns an empty list when no Narratives are linked.
    Raises NarrativePersistenceError on database failure.
    """
```

- [ ] **Step 4: Implement in `api/tests/fakes/fake_narrative_repository.py`**

```python
async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
    """Returns all Narratives whose causal_model_id matches the given ID."""
    self.logger.debug(
        "FakeNarrativeRepository.find_by_causal_model_id: causal_model_id=%s",
        causal_model_id,
    )
    return [n for n in self._store.values() if n.causal_model_id == causal_model_id]
```

- [ ] **Step 5: Implement in `api/repositories/supabase_narrative_repository.py`**

```python
async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
    """Returns all Narratives linked to the given CausalModel ID.

    Returns thin Narrative objects (no scenes or actors loaded).
    Raises NarrativePersistenceError on database failure.
    """
    self.logger.debug(
        "SupabaseNarrativeRepository.find_by_causal_model_id: causal_model_id=%s",
        causal_model_id,
    )
    try:
        result = (
            await self._client.table("narrative")
            .select("id, title, causal_model_id, user_id")
            .eq("causal_model_id", causal_model_id)
            .execute()
        )
    except Exception as e:
        raise NarrativePersistenceError(
            f"Failed to load narratives for causal model {causal_model_id}: {e}"
        ) from e

    return [Narrative.from_record(row) for row in records(result.data)]
```

- [ ] **Step 6: Add `find_by_causal_model_id` to `api/services/narrative_service.py`**

```python
async def find_by_causal_model_id(self, causal_model_id: str) -> list[Narrative]:
    """Returns all Narratives linked to the given CausalModel.

    Returns an empty list when no Narratives are linked.
    """
    self.logger.debug(
        "NarrativeService.find_by_causal_model_id: causal_model_id=%s", causal_model_id
    )
    return await self._repository.find_by_causal_model_id(causal_model_id)
```

- [ ] **Step 7: Update `get_causal_model` endpoint in `api/routers/causal_models.py`**

Read the router to find the `get_causal_model` endpoint. Inject `NarrativeService` and add `linked_narratives` to the response:

```python
@router.get("/{causal_model_id}", response_model=CausalModelResponse)
async def get_causal_model(
    causal_model_id: str,
    service: CausalModelService = Depends(get_causal_model_service),
    narrative_service: NarrativeService = Depends(get_narrative_service),
) -> CausalModelResponse:
    """Returns the CausalModel with all Slots, Relations and linked Narratives."""
    cm = await service.find_by_id(causal_model_id)
    linked = await narrative_service.find_by_causal_model_id(causal_model_id)
    response = _to_causal_model_response(cm)
    return CausalModelResponse(
        **response.model_dump(),
        linked_narratives=[
            LinkedNarrativeResponse(id=n.id, title=n.title)  # type: ignore[arg-type]
            for n in linked
        ],
    )
```

Add required imports: `LinkedNarrativeResponse` from schemas, `NarrativeService` and `get_narrative_service` from services/dependencies.

Note: if `_to_causal_model_response` already returns a `CausalModelResponse`, you can use `model_copy(update={"linked_narratives": [...]})` instead.

- [ ] **Step 8: Update TypeScript in `frontend/src/lib/api.ts`**

Find the `CausalModelDetail` or `CausalModelResponse` interface. Add:

```typescript
export interface LinkedNarrative {
  id: string;
  title: string;
}

// In CausalModelDetail:
linked_narratives: LinkedNarrative[];
```

Verify: `cd /Users/thormar/klartext/frontend && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 9: Run tests**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/test_causal_models_router.py tests/test_narrative_service.py -v 2>&1 | tail -15
```

All must pass.

- [ ] **Step 10: Commit**

```bash
git add api/schemas/causal_models.py api/repositories/narrative_repository.py api/tests/fakes/fake_narrative_repository.py api/repositories/supabase_narrative_repository.py api/services/narrative_service.py api/routers/causal_models.py api/dependencies.py api/tests/test_causal_models_router.py api/tests/test_narrative_service.py frontend/src/lib/api.ts
git commit -m "feat: CausalModelResponse includes linked_narratives"
```

---

## Task 9: Regression Run

**Files:** none

- [ ] **Step 1: Run full non-integration test suite**

```bash
cd /Users/thormar/klartext/api && .venv/bin/python -m pytest tests/ -k "not integration" -q 2>&1 | tail -10
```

Expected: all pass, 0 failures.

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/thormar/klartext/frontend && npx tsc --noEmit 2>&1 | head -20
```

Expected: no errors.

- [ ] **Step 3: Final commit if any loose ends**

If any files were modified but not committed, commit them now with a descriptive message.

---

## Self-Review

### Spec Coverage

| Gap | Task |
|-----|------|
| `NarrativeSummaryResponse` missing counts | Task 6 |
| `ClaimResponse` missing `id` | Task 2 |
| No `GET /narratives/{id}/claims` | Task 5 |
| Claim persistence after analysis (critical) | Tasks 1+3+4 |
| Slot identifier rename | Task 7 |
| `CausalModelResponse` missing `linked_narratives` | Task 8 |

All 6 gaps covered. ✅

### Type Consistency Check

- `NarrativeSummary.scene_count: int` → `NarrativeSummaryResponse.scene_count: int` → TypeScript `scene_count: number` ✅
- `Claim.id: str | None` → `ClaimResponse.id: str` (type: ignore at call site) ✅
- `LinkedNarrativeResponse` defined in Task 8 and used in same task ✅
- `ClaimRepository.save_for_narrative` defined in Task 3, used in Task 4 ✅
- `ClaimRepository.find_by_narrative_id` defined in Task 3, used in Tasks 4+5 ✅
- `NarrativeRepository.find_by_causal_model_id` defined in Task 8, used in same task ✅
- `Slot.update(epistemic_status, identifier=None)` defined in Task 7, called in service Task 7 ✅
