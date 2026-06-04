# Plan E — Frontend Extensions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimal UI for the experiment workflow: Narrative → Analyse → Wirkgefüge-Vorschlag → CausalModel.

**Architecture:** 2 new React pages (`NarrativeAnalyse`, `WirkgefuegeVorschlag`) + extensions to 2 existing pages (`NarrativeEditor`, `CausalModelEditor`). Navigation state passes analysis results between screens. No sidebar, no graph — lists only, as per `ui_experiment_scope.md`.

**Tech Stack:** React 18, TypeScript, React Router v6, Vitest + Testing Library. Backend: FastAPI (already implemented). Run tests: `cd /Users/thormar/klartext/frontend && npm test`. Run typecheck: `cd /Users/thormar/klartext/frontend && npm run typecheck`. Run backend tests: `cd /Users/thormar/klartext && klartext test`.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `api/schemas/narratives.py` | Modify | Add `causal_model_id` to `NarrativeSummaryResponse` |
| `api/routers/narratives.py` | Modify | Include `causal_model_id` in `list_narratives` response |
| `api/tests/test_narratives_router.py` | Modify | Add test for `causal_model_id` in list response |
| `frontend/src/lib/api.ts` | Modify | New TS types + API calls for all new endpoints |
| `frontend/src/App.tsx` | Modify | Add routes for 2 new screens |
| `frontend/src/pages/NarrativeEditor.tsx` | Modify | Add "Analysieren →" button (Screen 1) |
| `frontend/src/pages/NarrativeAnalyse.tsx` | Create | Screen 2: Actor + Claim cards with confirm/reject |
| `frontend/src/pages/WirkgefuegeVorschlag.tsx` | Create | Screen 3: Slot/Relation cards + save flow |
| `frontend/src/pages/CausalModelEditor.tsx` | Modify | Screen 4: Slots table + Relations table + linked narratives |

---

## Colour Reference (from ui_experiment_scope.md)

```
confirmed/linked:  bg=#EAF3DE text=#3B6D11
draft/incomplete:  bg=#FAEEDA text=#854F0B
rejected/error:    bg=#FCEBEB text=#A32D2D
entity-suggestion: bg=#E1F5EE text=#0F6E56
confidence ≥80%:   bg=#EAF3DE text=#3B6D11
confidence 60–79%: bg=#FAEEDA text=#854F0B
confidence <60%:   bg=#FCEBEB text=#A32D2D
confirmed border:  3px solid #1D9E75
```

---

## Task 1: Backend — causal_model_id in NarrativeSummaryResponse

Screen 4 needs to list narratives linked to a CausalModel. Currently the `GET /narratives` list omits `causal_model_id`. This task adds it.

**Files:**
- Modify: `api/schemas/narratives.py` (lines 137–141)
- Modify: `api/routers/narratives.py` (lines 194–203)
- Modify: `api/tests/test_narratives_router.py`

- [ ] **Step 1: Write failing test**

In `api/tests/test_narratives_router.py`, add this test after `test_narratives_list_response_contains_narrative_summary`:

```python
@pytest.mark.asyncio
async def test_narratives_list_response_includes_causal_model_id() -> None:
    """Expects each list item to include a causal_model_id field (null by default)."""
    override_with(FakeNarrativeService())
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/narratives")
    finally:
        clear_overrides()

    item = response.json()[0]
    assert "causal_model_id" in item
    assert item["causal_model_id"] is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/thormar/klartext && python -m pytest api/tests/test_narratives_router.py::test_narratives_list_response_includes_causal_model_id -v
```

Expected: FAIL — `AssertionError: assert "causal_model_id" in {...}`

- [ ] **Step 3: Add field to schema**

In `api/schemas/narratives.py`, update `NarrativeSummaryResponse` (currently lines 137–141):

```python
class NarrativeSummaryResponse(BaseModel):
    """A Narrative without scenes or actors, used for list views."""

    id: str
    title: str
    causal_model_id: str | None = None
```

- [ ] **Step 4: Update router handler**

In `api/routers/narratives.py`, update `list_narratives` (currently lines 194–203):

```python
@router.get("", response_model=list[NarrativeSummaryResponse])
async def list_narratives(
    service: NarrativeService = Depends(get_narrative_service),
) -> list[NarrativeSummaryResponse]:
    """Returns all persisted Narratives as a flat list without their scenes."""
    narratives = await service.list_all()
    return [
        NarrativeSummaryResponse(id=n.id, title=n.title, causal_model_id=n.causal_model_id)  # type: ignore[arg-type]
        for n in narratives
    ]
```

- [ ] **Step 5: Run tests to verify**

```bash
cd /Users/thormar/klartext && klartext test
```

Expected: PASS — all existing tests still green, new test green.

- [ ] **Step 6: Commit**

```bash
git add api/schemas/narratives.py api/routers/narratives.py api/tests/test_narratives_router.py
git commit -m "feat: include causal_model_id in NarrativeSummaryResponse list endpoint"
```

---

## Task 2: api.ts — New Types and API Calls

Adds TypeScript interfaces and API functions for all new backend endpoints. No test file — `npm run typecheck` is the verification.

**Files:**
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Add new TypeScript interfaces**

In `frontend/src/lib/api.ts`, after the existing `ConsistencyResult` interface, add:

```typescript
// ---------------------------------------------------------------------------
// Wirkgefüge suggestion in a ClaimSuggestion (from /analyse)
// ---------------------------------------------------------------------------

export interface WirkgefuegeSuggestionInClaim {
  suggestion_type: string;
  slot: string | null;
  zustand: string | null;
  source_slot: string | null;
  source_condition: string | null;
  target_slot: string | null;
  target_effect: string | null;
  mechanism: string | null;
}

export interface ActorSuggestion {
  label: string;
  actor_type: string;
  occurrences: string[];
  entity_suggestion: string | null;
}

export interface ClaimSuggestion {
  label: string;
  text: string;
  claim_type: string;
  confidence: number;
  wirkgefuege_suggestion: WirkgefuegeSuggestionInClaim | null;
}

export interface AnalyseNarrativeResponse {
  actors: ActorSuggestion[];
  claims: ClaimSuggestion[];
}

// ---------------------------------------------------------------------------
// Wirkgefüge suggestion (from /suggest-wirkgefuege)
// ---------------------------------------------------------------------------

export interface SuggestedSlot {
  identifier: string;
  slot_type: string;
}

export interface SuggestedRelation {
  source: string;
  target: string;
  source_condition: string | null;
  target_effect: string | null;
  mechanism: string | null;
  epistemic_status: string;
}

export interface SuggestWirkgefuegeResponse {
  suggested_slots: SuggestedSlot[];
  suggested_relations: SuggestedRelation[];
  from_claims: string[];
}

// ---------------------------------------------------------------------------
// Slot and Relation (from /causal-models/{id})
// ---------------------------------------------------------------------------

export interface Slot {
  id: string;
  identifier: string;
  slot_type: string;
  epistemic_status: string;
}

export interface Relation {
  id: string;
  identifier: string;
  source_slot_id: string;
  target_slot_id: string;
  mechanism: string | null;
  polarity: string | null;
  epistemic_status: string;
}
```

- [ ] **Step 2: Update CausalModel and NarrativeSummary interfaces**

Replace the existing `CausalModel` interface:

```typescript
export interface CausalModel {
  id: string;
  title: string;
  status: string;
  axioms: Axiom[];
  slots: Slot[];
  relations: Relation[];
}
```

Replace the existing `NarrativeSummary` interface:

```typescript
export interface NarrativeSummary {
  id: string;
  title: string;
  causal_model_id: string | null;
}
```

- [ ] **Step 3: Add new API calls**

In the `api` object, extend `causalModels` with slot and relation calls, add a `claims` namespace, and extend `narratives` with the three new calls. Replace the entire `export const api = { ... }` block with:

```typescript
export const api = {
  causalModels: {
    list: () => request<CausalModel[]>("/causal-models"),
    get: (id: string) => request<CausalModel>(`/causal-models/${id}`),
    create: (title: string) =>
      request<CausalModel>("/causal-models", {
        method: "POST",
        body: JSON.stringify({ title }),
      }),
    addAxiom: (id: string, label: string, description: string) =>
      request<Axiom>(`/causal-models/${id}/axioms`, {
        method: "POST",
        body: JSON.stringify({ label, description }),
      }),
    checkConsistency: (id: string, scene_text: string) =>
      request<ConsistencyResult>(`/causal-models/${id}/check-consistency`, {
        method: "POST",
        body: JSON.stringify({ scene_text }),
      }),
    addSlot: (id: string, identifier: string, slot_type: string) =>
      request<Slot>(`/causal-models/${id}/slots`, {
        method: "POST",
        body: JSON.stringify({ identifier, slot_type, epistemic_status: "incomplete" }),
      }),
    addRelation: (
      id: string,
      identifier: string,
      source_slot_id: string,
      target_slot_id: string,
      mechanism: string | null,
    ) =>
      request<Relation>(`/causal-models/${id}/relations`, {
        method: "POST",
        body: JSON.stringify({ identifier, source_slot_id, target_slot_id, mechanism }),
      }),
    updateRelation: (
      causal_model_id: string,
      relation_id: string,
      mechanism: string | null,
      polarity: string | null,
      epistemic_status: string,
    ) =>
      request<Relation>(`/causal-models/${causal_model_id}/relations/${relation_id}`, {
        method: "PUT",
        body: JSON.stringify({ mechanism, polarity, epistemic_status }),
      }),
  },
  narratives: {
    list: () => request<NarrativeSummary[]>("/narratives"),
    get: (id: string) => request<Narrative>(`/narratives/${id}`),
    create: (title: string) =>
      request<Narrative>("/narratives", {
        method: "POST",
        body: JSON.stringify({ title }),
      }),
    importFromPath: (path: string) =>
      request<Narrative>("/narratives/import", {
        method: "POST",
        body: JSON.stringify({ path }),
      }),
    addScene: (narrativeId: string, title: string, text: string) =>
      request<Scene>(`/narratives/${narrativeId}/scenes`, {
        method: "POST",
        body: JSON.stringify({ title, text }),
      }),
    extractClaims: (narrativeId: string, sceneId: string) =>
      request<{ claims: Claim[] }>(
        `/narratives/${narrativeId}/scenes/${sceneId}/extract-claims`,
        { method: "POST" }
      ),
    getSceneClaims: (narrativeId: string, sceneId: string) =>
      request<Claim[]>(`/narratives/${narrativeId}/scenes/${sceneId}/claims`),
    addActor: (
      narrativeId: string,
      label: string,
      actor_type: string,
      notes: string | null,
      entity_ref?: string | null,
    ) =>
      request<Actor>(`/narratives/${narrativeId}/actors`, {
        method: "POST",
        body: JSON.stringify({ label, actor_type, notes, entity_ref: entity_ref ?? null }),
      }),
    updateActor: (
      narrativeId: string,
      actorId: string,
      label: string,
      actor_type: string,
      notes: string | null,
    ) =>
      request<Actor>(`/narratives/${narrativeId}/actors/${actorId}`, {
        method: "PUT",
        body: JSON.stringify({ label, actor_type, notes }),
      }),
    removeActor: (narrativeId: string, actorId: string) =>
      requestVoid(`/narratives/${narrativeId}/actors/${actorId}`, { method: "DELETE" }),
    analyse: (id: string) =>
      request<AnalyseNarrativeResponse>(`/narratives/${id}/analyse`, { method: "POST" }),
    suggestWirkgefuege: (id: string) =>
      request<SuggestWirkgefuegeResponse>(`/narratives/${id}/suggest-wirkgefuege`, {
        method: "POST",
      }),
    linkToCausalModel: (narrativeId: string, causalModelId: string) =>
      request<Narrative>(`/narratives/${narrativeId}/causal-model`, {
        method: "PUT",
        body: JSON.stringify({ causal_model_id: causalModelId }),
      }),
  },
  claims: {
    linkToWirkgefuege: (claimId: string, wirkgefuege_ref: string) =>
      requestVoid(`/claims/${claimId}/link-to-wirkgefuege`, {
        method: "POST",
        body: JSON.stringify({ wirkgefuege_ref }),
      }),
  },
};
```

- [ ] **Step 4: Run TypeScript check**

```bash
cd /Users/thormar/klartext/frontend && npm run typecheck
```

Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add new types and API calls for analyse and wirkgefuege workflow"
```

---

## Task 3: App.tsx — New Routes

Wires the two new screen components into the router.

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create the new page files (empty stubs) for the test to import**

Create `frontend/src/pages/NarrativeAnalyse.tsx` with minimal content:

```tsx
export default function NarrativeAnalyse() {
  return <p>Bitte Analyse vom Narrativ-Editor starten.</p>;
}
```

Create `frontend/src/pages/WirkgefuegeVorschlag.tsx` with minimal content:

```tsx
export default function WirkgefuegeVorschlag() {
  return <p>Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten.</p>;
}
```

- [ ] **Step 2: Write failing test in App.test.tsx**

Add to `frontend/src/App.test.tsx`:

```typescript
import { MemoryRouter } from "react-router-dom";

describe("App routing — new screens", () => {
  it("renders NarrativeAnalyse for /narrative/:id/analyse route", () => {
    render(
      <MemoryRouter initialEntries={["/narrative/test-id/analyse"]}>
        <Routes>
          <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
        </Routes>
      </MemoryRouter>
    );
    expect(
      screen.getByText(/Bitte Analyse vom Narrativ-Editor starten/i)
    ).toBeInTheDocument();
  });

  it("renders WirkgefuegeVorschlag for /narrative/:id/wirkgefuege-vorschlag route", () => {
    render(
      <MemoryRouter initialEntries={["/narrative/test-id/wirkgefuege-vorschlag"]}>
        <Routes>
          <Route
            path="/narrative/:narrativeId/wirkgefuege-vorschlag"
            element={<WirkgefuegeVorschlag />}
          />
        </Routes>
      </MemoryRouter>
    );
    expect(
      screen.getByText(/Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten/i)
    ).toBeInTheDocument();
  });
});
```

Add the missing imports at the top of `App.test.tsx`:

```typescript
import { Routes, Route } from "react-router-dom";
import NarrativeAnalyse from "./pages/NarrativeAnalyse";
import WirkgefuegeVorschlag from "./pages/WirkgefuegeVorschlag";
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/thormar/klartext/frontend && npm test
```

Expected: The two new tests fail with "Cannot find module" or import errors (because the stub files don't exist yet at the import path — once stubs are created in Step 1 they should already pass, so the tests may actually pass here if stubs were created. If they already pass, continue.)

Actually: with the stubs from Step 1 in place, the routing tests should pass immediately — that's fine. The TDD cycle here is: the stubs make the route render tests green, and then the full implementation (Tasks 4–7) fills them in.

- [ ] **Step 4: Update App.tsx with new routes**

Replace the entire content of `frontend/src/App.tsx`:

```tsx
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Login from "./pages/Login";
import CausalModelEditor from "./pages/CausalModelEditor";
import NarrativeEditor from "./pages/NarrativeEditor";
import NarrativeAnalyse from "./pages/NarrativeAnalyse";
import WirkgefuegeVorschlag from "./pages/WirkgefuegeVorschlag";
import ReadingView from "./pages/ReadingView";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #eee", display: "flex", gap: "1rem" }}>
        <NavLink to="/">Login</NavLink>
        <NavLink to="/causal-model">Wirkmodell</NavLink>
        <NavLink to="/narrative">Narrativ</NavLink>
        <NavLink to="/reading">Lesen</NavLink>
      </nav>
      <main style={{ padding: "2rem" }}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/causal-model" element={<CausalModelEditor />} />
          <Route path="/narrative" element={<NarrativeEditor />} />
          <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
          <Route
            path="/narrative/:narrativeId/wirkgefuege-vorschlag"
            element={<WirkgefuegeVorschlag />}
          />
          <Route path="/reading" element={<ReadingView />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
```

- [ ] **Step 5: Run tests**

```bash
cd /Users/thormar/klartext/frontend && npm test
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/App.tsx frontend/src/pages/NarrativeAnalyse.tsx frontend/src/pages/WirkgefuegeVorschlag.tsx frontend/src/App.test.tsx
git commit -m "feat: add routes for NarrativeAnalyse and WirkgefuegeVorschlag screens"
```

---

## Task 4: Screen 1 — "Analysieren →" Button in NarrativeEditor

Adds an "Analysieren →" button at the bottom of the selected-narrative view. Calls `POST /narratives/{id}/analyse` and navigates to Screen 2 on success.

**Files:**
- Modify: `frontend/src/pages/NarrativeEditor.tsx`

- [ ] **Step 1: Write failing test**

Create `frontend/src/pages/NarrativeEditor.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import NarrativeEditor from "./NarrativeEditor";

// Mock the entire api module
vi.mock("../lib/api", () => ({
  api: {
    narratives: {
      list: vi.fn().mockResolvedValue([
        { id: "n1", title: "Test Narrativ", causal_model_id: null },
      ]),
      get: vi.fn().mockResolvedValue({
        id: "n1",
        title: "Test Narrativ",
        causal_model_id: null,
        scenes: [{ id: "s1", title: "Szene 1", text: "Text.", position: 1 }],
        actors: [],
      }),
      analyse: vi.fn().mockResolvedValue({
        actors: [],
        claims: [],
      }),
    },
    causalModels: {
      list: vi.fn().mockResolvedValue([]),
    },
  },
}));

// Mock react-router-dom's useNavigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderEditor() {
  return render(
    <MemoryRouter>
      <NarrativeEditor />
    </MemoryRouter>
  );
}

describe("NarrativeEditor — Analysieren button", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("shows Analysieren button when a narrative is selected", async () => {
    renderEditor();

    // Wait for narrative list to load and click it
    const btn = await screen.findByText("Test Narrativ");
    fireEvent.click(btn);

    // Button should appear
    expect(await screen.findByText(/Analysieren/i)).toBeInTheDocument();
  });

  it("navigates to analyse screen after successful analysis", async () => {
    renderEditor();

    const narrativeBtn = await screen.findByText("Test Narrativ");
    fireEvent.click(narrativeBtn);

    const analyseBtn = await screen.findByText(/Analysieren/i);
    fireEvent.click(analyseBtn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        "/narrative/n1/analyse",
        expect.objectContaining({ state: expect.objectContaining({ narrative: { id: "n1", title: "Test Narrativ" } }) })
      );
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/thormar/klartext/frontend && npm test -- NarrativeEditor.test
```

Expected: FAIL — "Analysieren" button not found.

- [ ] **Step 3: Add analyse state and button to NarrativeEditor**

In `frontend/src/pages/NarrativeEditor.tsx`:

**3a.** Add `useNavigate` to the react-router-dom import:

```typescript
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Actor,
  api,
  AnalyseNarrativeResponse,
  CausalModel,
  Claim,
  ConsistencyResult,
  Narrative,
  NarrativeSummary,
  Scene,
} from "../lib/api";
```

**3b.** Add at the top of the `NarrativeEditor` function body, after the existing `const [loading, setLoading] = useState(false);`:

```typescript
const navigate = useNavigate();

// Analyse narrative
const [analysing, setAnalysing] = useState(false);
const [analyseError, setAnalyseError] = useState<string | null>(null);
```

**3c.** Add the `analyseNarrative` function after `removeActor`:

```typescript
async function analyseNarrative() {
  if (!selected) return;
  setAnalysing(true);
  setAnalyseError(null);
  try {
    const analysis: AnalyseNarrativeResponse = await api.narratives.analyse(selected.id);
    navigate(`/narrative/${selected.id}/analyse`, {
      state: { analysis, narrative: { id: selected.id, title: selected.title } },
    });
  } catch {
    setAnalyseError("Analyse fehlgeschlagen. Bitte erneut versuchen.");
    setAnalysing(false);
  }
}
```

**3d.** In the JSX, find the closing `</main>` tag of the third column. Before it (after the last `</>` inside `{selectedScene && (...)}` and the actor form block), add the analyse button section. The button should appear whenever a narrative is selected, at the bottom of the main column, after the `{selectedScene && ...}` block and the actor form block:

```tsx
{/* ---------------------------------------------------------------- */}
{/* Analyse button                                                     */}
{/* ---------------------------------------------------------------- */}
{selected && !showAddScene && !showAddActor && !selectedActorId && (
  <div
    style={{
      borderTop: "1px solid #eee",
      paddingTop: "1.5rem",
      marginTop: "2rem",
    }}
  >
    <button
      onClick={analyseNarrative}
      disabled={analysing}
      style={{
        padding: "0.75rem 1.5rem",
        fontSize: "1rem",
        background: analysing ? "#e0e0e0" : "#4a7aff",
        color: analysing ? "#999" : "#fff",
        border: "none",
        borderRadius: 4,
        cursor: analysing ? "not-allowed" : "pointer",
        width: "100%",
      }}
    >
      {analysing ? "⏳ Analyse läuft…" : "Analysieren →"}
    </button>
    {analyseError && (
      <p style={{ color: "#A32D2D", fontSize: "0.85rem", marginTop: "0.5rem" }}>
        {analyseError}
      </p>
    )}
  </div>
)}
```

**Important:** This block must go inside `<main>` but outside the `{selectedScene && ...}` and `{(showAddActor || selectedActorId) && ...}` blocks — at the same nesting level as those, right before `</main>`.

- [ ] **Step 4: Run tests**

```bash
cd /Users/thormar/klartext/frontend && npm test -- NarrativeEditor.test
```

Expected: PASS.

- [ ] **Step 5: Run typecheck**

```bash
cd /Users/thormar/klartext/frontend && npm run typecheck
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/NarrativeEditor.tsx frontend/src/pages/NarrativeEditor.test.tsx
git commit -m "feat: add Analysieren button to NarrativeEditor (Screen 1)"
```

---

## Task 5: Screen 2 — NarrativeAnalyse Page

Actor cards and Claim cards with confirm/reject. At least one confirmed claim enables "Wirkgefüge-Vorschläge generieren →".

**Files:**
- Modify (replace stub): `frontend/src/pages/NarrativeAnalyse.tsx`

- [ ] **Step 1: Write failing test**

Create `frontend/src/pages/NarrativeAnalyse.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import NarrativeAnalyse from "./NarrativeAnalyse";
import type { AnalyseNarrativeResponse } from "../lib/api";

vi.mock("../lib/api", () => ({
  api: {
    narratives: {
      suggestWirkgefuege: vi.fn().mockResolvedValue({
        suggested_slots: [],
        suggested_relations: [],
        from_claims: [],
      }),
    },
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockAnalysis: AnalyseNarrativeResponse = {
  actors: [
    {
      label: "EZB",
      actor_type: "institution",
      occurrences: ["Szene 1"],
      entity_suggestion: "ecb",
    },
  ],
  claims: [
    {
      label: "Inflation steigt",
      text: "Die Inflation stieg auf 8%.",
      claim_type: "empirical",
      confidence: 0.9,
      wirkgefuege_suggestion: null,
    },
  ],
};

function renderWithState(analysis: AnalyseNarrativeResponse | null) {
  return render(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/narrative/test-id/analyse",
          state: analysis
            ? { analysis, narrative: { id: "test-id", title: "Test Narrativ" } }
            : null,
        },
      ]}
    >
      <Routes>
        <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("NarrativeAnalyse", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("shows error state when analysis is not in location state", () => {
    renderWithState(null);
    expect(
      screen.getByText(/Bitte Analyse vom Narrativ-Editor starten/i)
    ).toBeInTheDocument();
  });

  it("renders actor label and claim label from analysis", () => {
    renderWithState(mockAnalysis);
    expect(screen.getByText("EZB")).toBeInTheDocument();
    expect(screen.getByText("Inflation steigt")).toBeInTheDocument();
  });

  it("Wirkgefüge button is disabled until a claim is accepted", () => {
    renderWithState(mockAnalysis);
    const btn = screen.getByText(/Wirkgefüge-Vorschläge generieren/i);
    expect(btn).toBeDisabled();
  });

  it("Wirkgefüge button becomes enabled after accepting a claim", async () => {
    renderWithState(mockAnalysis);
    // Accept the claim (✓ button for claims section)
    const acceptButtons = screen.getAllByText("✓");
    fireEvent.click(acceptButtons[acceptButtons.length - 1]); // last ✓ = claim
    const btn = screen.getByText(/Wirkgefüge-Vorschläge generieren/i);
    expect(btn).not.toBeDisabled();
  });

  it("navigates to wirkgefuege screen after generating suggestions", async () => {
    renderWithState(mockAnalysis);
    const acceptButtons = screen.getAllByText("✓");
    fireEvent.click(acceptButtons[acceptButtons.length - 1]);
    const btn = screen.getByText(/Wirkgefüge-Vorschläge generieren/i);
    fireEvent.click(btn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        "/narrative/test-id/wirkgefuege-vorschlag",
        expect.anything()
      );
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/thormar/klartext/frontend && npm test -- NarrativeAnalyse.test
```

Expected: FAIL — mostly because the stub component doesn't render cards.

- [ ] **Step 3: Implement NarrativeAnalyse.tsx**

Replace `frontend/src/pages/NarrativeAnalyse.tsx` with the full implementation:

```tsx
import { useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import {
  api,
  AnalyseNarrativeResponse,
  ActorSuggestion,
  ClaimSuggestion,
} from "../lib/api";

// ---------------------------------------------------------------------------
// Colour constants from ui_experiment_scope.md
// ---------------------------------------------------------------------------
const C = {
  confirmed: { bg: "#EAF3DE", text: "#3B6D11" },
  draft: { bg: "#FAEEDA", text: "#854F0B" },
  rejected: { bg: "#FCEBEB", text: "#A32D2D" },
  entity: { bg: "#E1F5EE", text: "#0F6E56" },
} as const;

const BORDER_OK = "3px solid #1D9E75";
const BORDER_NO = "3px solid #A32D2D";

type ConfirmState = "pending" | "accepted" | "rejected";

const ACTOR_TYPE_LABELS: Record<string, string> = {
  individual: "Figur",
  organisation: "Organisation",
  group: "Gruppe",
  institution: "Institution",
  abstract_entity: "Abstrakte Entität",
};

const CLAIM_TYPE_LABELS: Record<string, string> = {
  empirical: "Empirisch",
  causal: "Kausal",
  definitional: "Definitorisch",
  normative: "Normativ",
  prognostic: "Prognostisch",
  counterfactual: "Kontrafaktisch",
  methodological: "Methodisch",
  uncertainty: "Unsicherheit",
};

// ---------------------------------------------------------------------------
// NarrativeAnalyse — Screen 2
// ---------------------------------------------------------------------------

export default function NarrativeAnalyse() {
  const navigate = useNavigate();
  const location = useLocation();
  const { narrativeId } = useParams<{ narrativeId: string }>();

  const state = location.state as {
    analysis: AnalyseNarrativeResponse;
    narrative: { id: string; title: string };
  } | null;

  const analysis = state?.analysis ?? null;
  const narrative = state?.narrative ?? null;

  const [actorStates, setActorStates] = useState<ConfirmState[]>(
    () => (analysis?.actors ?? []).map(() => "pending" as ConfirmState)
  );
  const [claimStates, setClaimStates] = useState<ConfirmState[]>(
    () => (analysis?.claims ?? []).map(() => "pending" as ConfirmState)
  );
  const [suggesting, setSuggesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!analysis || !narrative) {
    return (
      <p style={{ color: "#888" }}>
        Bitte Analyse vom Narrativ-Editor starten.
      </p>
    );
  }

  const anyClaimAccepted = claimStates.some((s) => s === "accepted");

  async function generateSuggestions() {
    setSuggesting(true);
    setError(null);
    try {
      const suggestion = await api.narratives.suggestWirkgefuege(narrativeId!);
      navigate(`/narrative/${narrativeId}/wirkgefuege-vorschlag`, {
        state: { suggestion, narrative },
      });
    } catch {
      setError("Wirkgefüge-Vorschläge konnten nicht generiert werden.");
      setSuggesting(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      {/* Header */}
      <button
        onClick={() => navigate(-1)}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "#4a7aff",
          marginBottom: "1rem",
          padding: 0,
          fontSize: "0.9rem",
        }}
      >
        ← Zurück zu Narrativ
      </button>

      <h2 style={{ marginTop: 0 }}>Analyse: {narrative.title}</h2>
      <p style={{ color: "#888", fontSize: "0.85rem", marginBottom: "2rem" }}>
        {analysis.actors.length} Akteure gefunden · {analysis.claims.length} Claims gefunden
      </p>

      {/* Actors */}
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}>
        <SectionHeader
          label="Akteure"
          onAcceptAll={() => setActorStates(analysis.actors.map(() => "accepted"))}
        />
        {analysis.actors.map((actor, i) => (
          <ActorCard
            key={i}
            actor={actor}
            state={actorStates[i]}
            onAccept={() =>
              setActorStates((prev) => prev.map((s, j) => (j === i ? "accepted" : s)))
            }
            onReject={() =>
              setActorStates((prev) => prev.map((s, j) => (j === i ? "rejected" : s)))
            }
          />
        ))}
      </div>

      {/* Claims */}
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}>
        <SectionHeader
          label="Claims"
          onAcceptAll={() => setClaimStates(analysis.claims.map(() => "accepted"))}
        />
        {analysis.claims.map((claim, i) => (
          <ClaimCard
            key={i}
            claim={claim}
            state={claimStates[i]}
            onAccept={() =>
              setClaimStates((prev) => prev.map((s, j) => (j === i ? "accepted" : s)))
            }
            onReject={() =>
              setClaimStates((prev) => prev.map((s, j) => (j === i ? "rejected" : s)))
            }
          />
        ))}
      </div>

      {/* Generate button */}
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem" }}>
        {error && (
          <p style={{ color: C.rejected.text, marginBottom: "0.5rem", fontSize: "0.85rem" }}>
            {error}
          </p>
        )}
        <button
          onClick={generateSuggestions}
          disabled={!anyClaimAccepted || suggesting}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            background: anyClaimAccepted ? "#1D9E75" : "#e0e0e0",
            color: anyClaimAccepted ? "#fff" : "#999",
            border: "none",
            borderRadius: 4,
            cursor: anyClaimAccepted ? "pointer" : "not-allowed",
            width: "100%",
          }}
        >
          {suggesting ? "Generiere…" : "Wirkgefüge-Vorschläge generieren →"}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SectionHeader({
  label,
  onAcceptAll,
}: {
  label: string;
  onAcceptAll: () => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "1rem",
      }}
    >
      <h3
        style={{
          margin: 0,
          textTransform: "uppercase",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          color: "#888",
        }}
      >
        {label}
      </h3>
      <button onClick={onAcceptAll} style={{ fontSize: "0.8rem" }}>
        Alle bestätigen
      </button>
    </div>
  );
}

function borderForState(state: ConfirmState): string {
  if (state === "accepted") return BORDER_OK;
  if (state === "rejected") return BORDER_NO;
  return "1px solid #e0e0e0";
}

function ConfirmButtons({
  state,
  onAccept,
  onReject,
}: {
  state: ConfirmState;
  onAccept: () => void;
  onReject: () => void;
}) {
  return (
    <div style={{ display: "flex", gap: "0.5rem", flexShrink: 0 }}>
      <button
        onClick={onAccept}
        style={{
          background: state === "accepted" ? C.confirmed.bg : "none",
          border: "1px solid #ddd",
          borderRadius: 3,
          padding: "0.25rem 0.5rem",
          cursor: "pointer",
          fontSize: "0.85rem",
          color: state === "accepted" ? C.confirmed.text : "inherit",
        }}
      >
        ✓
      </button>
      <button
        onClick={onReject}
        style={{
          background: state === "rejected" ? C.rejected.bg : "none",
          border: "1px solid #ddd",
          borderRadius: 3,
          padding: "0.25rem 0.5rem",
          cursor: "pointer",
          fontSize: "0.85rem",
          color: state === "rejected" ? C.rejected.text : "inherit",
        }}
      >
        ✗
      </button>
    </div>
  );
}

function ActorCard({
  actor,
  state,
  onAccept,
  onReject,
}: {
  actor: ActorSuggestion;
  state: ConfirmState;
  onAccept: () => void;
  onReject: () => void;
}) {
  return (
    <div
      style={{
        border: borderForState(state),
        borderRadius: 4,
        padding: "0.75rem",
        marginBottom: "0.75rem",
        opacity: state === "rejected" ? 0.5 : 1,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
      }}
    >
      <div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            marginBottom: "0.25rem",
          }}
        >
          <span>👤</span>
          <strong
            style={{ textDecoration: state === "rejected" ? "line-through" : "none" }}
          >
            {actor.label}
          </strong>
          <span style={{ fontSize: "0.75rem", color: "#888" }}>
            {ACTOR_TYPE_LABELS[actor.actor_type] ?? actor.actor_type}
          </span>
        </div>
        {actor.occurrences.length > 0 && (
          <p style={{ margin: "0 0 0.25rem", fontSize: "0.8rem", color: "#888" }}>
            {actor.occurrences.join(", ")}
          </p>
        )}
        {actor.entity_suggestion && (
          <span
            style={{
              fontSize: "0.75rem",
              background: C.entity.bg,
              color: C.entity.text,
              padding: "0.1rem 0.4rem",
              borderRadius: 3,
            }}
          >
            → Entity-Vorschlag: "{actor.entity_suggestion}"
          </span>
        )}
      </div>
      <ConfirmButtons state={state} onAccept={onAccept} onReject={onReject} />
    </div>
  );
}

function confidenceStyle(conf: number) {
  if (conf >= 0.8) return C.confirmed;
  if (conf >= 0.6) return C.draft;
  return C.rejected;
}

function ClaimCard({
  claim,
  state,
  onAccept,
  onReject,
}: {
  claim: ClaimSuggestion;
  state: ConfirmState;
  onAccept: () => void;
  onReject: () => void;
}) {
  const confStyle = confidenceStyle(claim.confidence);
  const ws = claim.wirkgefuege_suggestion;

  return (
    <div
      style={{
        border: borderForState(state),
        borderRadius: 4,
        padding: "0.75rem",
        marginBottom: "0.75rem",
        opacity: state === "rejected" ? 0.5 : 1,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "0.25rem",
        }}
      >
        <strong
          style={{
            textDecoration: state === "rejected" ? "line-through" : "none",
            fontSize: "0.9rem",
          }}
        >
          {claim.label}
        </strong>
        <span
          style={{
            fontSize: "0.75rem",
            background: confStyle.bg,
            color: confStyle.text,
            padding: "0.1rem 0.4rem",
            borderRadius: 3,
            flexShrink: 0,
            marginLeft: "0.5rem",
          }}
        >
          {Math.round(claim.confidence * 100)}%
        </span>
      </div>

      <p
        style={{
          margin: "0 0 0.25rem",
          fontSize: "0.85rem",
          color: "#555",
          fontStyle: "italic",
        }}
      >
        "{claim.text}"
      </p>

      <div style={{ marginBottom: "0.25rem" }}>
        <span
          style={{
            fontSize: "0.75rem",
            background: "#e8f0fe",
            color: "#3c5bb5",
            padding: "0.1rem 0.4rem",
            borderRadius: 3,
          }}
        >
          {CLAIM_TYPE_LABELS[claim.claim_type] ?? claim.claim_type}
        </span>
      </div>

      {ws && (
        <p
          style={{
            margin: "0 0 0.25rem",
            fontSize: "0.8rem",
            color: "#888",
            fontStyle: "italic",
          }}
        >
          {ws.suggestion_type === "slot_zustand"
            ? `→ Slot: ${ws.slot ?? "?"} / ${ws.zustand ?? "?"}`
            : `→ ${ws.source_slot ?? "?"} → ${ws.target_slot ?? "?"}`}
        </p>
      )}

      <div
        style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", marginTop: "0.5rem" }}
      >
        <ConfirmButtons state={state} onAccept={onAccept} onReject={onReject} />
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/thormar/klartext/frontend && npm test -- NarrativeAnalyse.test
```

Expected: All 5 tests pass.

- [ ] **Step 5: Run typecheck**

```bash
cd /Users/thormar/klartext/frontend && npm run typecheck
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/NarrativeAnalyse.tsx frontend/src/pages/NarrativeAnalyse.test.tsx
git commit -m "feat: implement NarrativeAnalyse screen with actor and claim cards"
```

---

## Task 6: Screen 3 — WirkgefuegeVorschlag Page

Editable slot and relation cards. Model name input. Save flow creates CausalModel, slots, relations, links narrative and claims.

**Files:**
- Modify (replace stub): `frontend/src/pages/WirkgefuegeVorschlag.tsx`

- [ ] **Step 1: Write failing test**

Create `frontend/src/pages/WirkgefuegeVorschlag.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import WirkgefuegeVorschlag from "./WirkgefuegeVorschlag";
import type { SuggestWirkgefuegeResponse } from "../lib/api";

vi.mock("../lib/api", () => ({
  api: {
    causalModels: {
      create: vi.fn().mockResolvedValue({ id: "cm1", title: "Test Modell", status: "draft", axioms: [], slots: [], relations: [] }),
      addSlot: vi.fn().mockResolvedValue({ id: "s1", identifier: "co2", slot_type: "physical_quantity", epistemic_status: "incomplete" }),
      addRelation: vi.fn().mockResolvedValue({ id: "r1", identifier: "co2_to_temp", source_slot_id: "s1", target_slot_id: "s2", mechanism: null, polarity: null, epistemic_status: "incomplete" }),
      updateRelation: vi.fn().mockResolvedValue({}),
    },
    narratives: {
      linkToCausalModel: vi.fn().mockResolvedValue({}),
    },
    claims: {
      linkToWirkgefuege: vi.fn().mockResolvedValue(undefined),
    },
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockSuggestion: SuggestWirkgefuegeResponse = {
  suggested_slots: [
    { identifier: "co2_emissionen", slot_type: "physical_quantity" },
    { identifier: "global_temperatur", slot_type: "physical_quantity" },
  ],
  suggested_relations: [
    {
      source: "co2_emissionen",
      target: "global_temperatur",
      source_condition: "hoch",
      target_effect: "steigend",
      mechanism: "Treibhauseffekt",
      epistemic_status: "incomplete",
    },
  ],
  from_claims: ["claim-1"],
};

function renderWithState(suggestion: SuggestWirkgefuegeResponse | null) {
  return render(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/narrative/test-id/wirkgefuege-vorschlag",
          state: suggestion
            ? { suggestion, narrative: { id: "test-id", title: "Test Narrativ" } }
            : null,
        },
      ]}
    >
      <Routes>
        <Route
          path="/narrative/:narrativeId/wirkgefuege-vorschlag"
          element={<WirkgefuegeVorschlag />}
        />
      </Routes>
    </MemoryRouter>
  );
}

describe("WirkgefuegeVorschlag", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("shows error state when suggestion is not in location state", () => {
    renderWithState(null);
    expect(
      screen.getByText(/Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten/i)
    ).toBeInTheDocument();
  });

  it("renders slot identifiers from suggestion", () => {
    renderWithState(mockSuggestion);
    expect(screen.getByDisplayValue("co2_emissionen")).toBeInTheDocument();
    expect(screen.getByDisplayValue("global_temperatur")).toBeInTheDocument();
  });

  it("renders relation source → target", () => {
    renderWithState(mockSuggestion);
    expect(screen.getByText(/co2_emissionen → global_temperatur/i)).toBeInTheDocument();
  });

  it("save button is disabled when model name is empty", () => {
    renderWithState(mockSuggestion);
    const btn = screen.getByText(/CausalModel anlegen und speichern/i);
    expect(btn).toBeDisabled();
  });

  it("navigates to /causal-model after successful save", async () => {
    renderWithState(mockSuggestion);
    const input = screen.getByPlaceholderText(/Modellname eingeben/i);
    fireEvent.change(input, { target: { value: "Mein Modell" } });
    const btn = screen.getByText(/CausalModel anlegen und speichern/i);
    fireEvent.click(btn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        "/causal-model",
        expect.objectContaining({ state: { selectedModelId: "cm1" } })
      );
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/thormar/klartext/frontend && npm test -- WirkgefuegeVorschlag.test
```

Expected: FAIL.

- [ ] **Step 3: Implement WirkgefuegeVorschlag.tsx**

Replace `frontend/src/pages/WirkgefuegeVorschlag.tsx` with:

```tsx
import { useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { api, SuggestWirkgefuegeResponse } from "../lib/api";

// ---------------------------------------------------------------------------
// Colour constants from ui_experiment_scope.md
// ---------------------------------------------------------------------------
const C = {
  confirmed: { bg: "#EAF3DE", text: "#3B6D11" },
  rejected: { bg: "#FCEBEB", text: "#A32D2D" },
} as const;

const SLOT_TYPES = [
  "physical_quantity",
  "social_quantity",
  "entity_state",
  "trend",
  "process",
];

const EPISTEMIC_STATUS_OPTIONS = ["incomplete", "axiomatic"];

type SlotEdit = {
  identifier: string;
  slot_type: string;
  rejected: boolean;
};

type RelationEdit = {
  source: string;
  target: string;
  mechanism: string;
  epistemic_status: string;
  rejected: boolean;
};

// ---------------------------------------------------------------------------
// WirkgefuegeVorschlag — Screen 3
// ---------------------------------------------------------------------------

export default function WirkgefuegeVorschlag() {
  const navigate = useNavigate();
  const location = useLocation();
  const { narrativeId } = useParams<{ narrativeId: string }>();

  const state = location.state as {
    suggestion: SuggestWirkgefuegeResponse;
    narrative: { id: string; title: string };
  } | null;

  const suggestion = state?.suggestion ?? null;
  const narrative = state?.narrative ?? null;

  const [slots, setSlots] = useState<SlotEdit[]>(
    () =>
      (suggestion?.suggested_slots ?? []).map((s) => ({
        identifier: s.identifier,
        slot_type: s.slot_type,
        rejected: false,
      }))
  );

  const [relations, setRelations] = useState<RelationEdit[]>(
    () =>
      (suggestion?.suggested_relations ?? []).map((r) => ({
        source: r.source,
        target: r.target,
        mechanism: r.mechanism ?? "",
        epistemic_status: r.epistemic_status,
        rejected: false,
      }))
  );

  const [modelName, setModelName] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!suggestion || !narrative) {
    return (
      <p style={{ color: "#888" }}>
        Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten.
      </p>
    );
  }

  const fromClaims = suggestion.from_claims;
  const acceptedSlotCount = slots.filter((s) => !s.rejected).length;
  const acceptedRelationCount = relations.filter((r) => !r.rejected).length;

  async function save() {
    if (!modelName.trim()) return;
    setSaving(true);
    setError(null);
    try {
      // 1. Create CausalModel
      const newModel = await api.causalModels.create(modelName.trim());

      // 2. Create accepted slots — build identifier → id map
      const slotIdMap: Record<string, string> = {};
      for (const slot of slots) {
        if (!slot.rejected) {
          const created = await api.causalModels.addSlot(
            newModel.id,
            slot.identifier,
            slot.slot_type,
          );
          slotIdMap[slot.identifier] = created.id;
        }
      }

      // 3. Create accepted relations
      for (const rel of relations) {
        if (rel.rejected) continue;
        const sourceId = slotIdMap[rel.source];
        const targetId = slotIdMap[rel.target];
        if (!sourceId || !targetId) continue; // skip if referenced slot was rejected
        const identifier = `${rel.source}_to_${rel.target}`;
        const created = await api.causalModels.addRelation(
          newModel.id,
          identifier,
          sourceId,
          targetId,
          rel.mechanism.trim() || null,
        );
        if (rel.epistemic_status !== "incomplete") {
          await api.causalModels.updateRelation(
            newModel.id,
            created.id,
            rel.mechanism.trim() || null,
            null,
            rel.epistemic_status,
          );
        }
      }

      // 4. Link narrative to causal model
      await api.narratives.linkToCausalModel(narrativeId!, newModel.id);

      // 5. Link DRAFT claims to this causal model (sets status → LINKED)
      for (const claimId of fromClaims) {
        await api.claims.linkToWirkgefuege(claimId, newModel.id);
      }

      // 6. Navigate to CausalModelEditor
      navigate("/causal-model", { state: { selectedModelId: newModel.id } });
    } catch {
      setError("Speichern fehlgeschlagen. Bitte erneut versuchen.");
      setSaving(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      <button
        onClick={() => navigate(-1)}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "#4a7aff",
          marginBottom: "1rem",
          padding: 0,
          fontSize: "0.9rem",
        }}
      >
        ← Zurück zur Analyse
      </button>

      <h2 style={{ marginTop: 0 }}>Wirkgefüge-Vorschlag für: {narrative.title}</h2>

      {/* Slots */}
      <div
        style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}
      >
        <h3
          style={{
            textTransform: "uppercase",
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            color: "#888",
            marginTop: 0,
          }}
        >
          Slots ({acceptedSlotCount})
        </h3>

        {slots.map((slot, i) => (
          <div
            key={i}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 4,
              padding: "0.75rem",
              marginBottom: "0.75rem",
              opacity: slot.rejected ? 0.4 : 1,
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
            }}
          >
            <div style={{ flex: 1 }}>
              <input
                value={slot.identifier}
                onChange={(e) =>
                  setSlots((prev) =>
                    prev.map((s, j) => (j === i ? { ...s, identifier: e.target.value } : s))
                  )
                }
                disabled={slot.rejected}
                style={{
                  fontFamily: "monospace",
                  border: "1px solid #ddd",
                  borderRadius: 3,
                  padding: "0.2rem 0.4rem",
                  fontSize: "0.9rem",
                  width: "100%",
                  boxSizing: "border-box",
                  marginBottom: "0.25rem",
                }}
              />
              <select
                value={slot.slot_type}
                onChange={(e) =>
                  setSlots((prev) =>
                    prev.map((s, j) => (j === i ? { ...s, slot_type: e.target.value } : s))
                  )
                }
                disabled={slot.rejected}
                style={{ fontSize: "0.8rem", padding: "0.2rem" }}
              >
                {SLOT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={() =>
                setSlots((prev) =>
                  prev.map((s, j) => (j === i ? { ...s, rejected: !s.rejected } : s))
                )
              }
              style={{
                background: slot.rejected ? C.rejected.bg : "none",
                border: "1px solid #ddd",
                borderRadius: 3,
                padding: "0.25rem 0.5rem",
                cursor: "pointer",
                fontSize: "0.85rem",
                color: slot.rejected ? C.rejected.text : "inherit",
                flexShrink: 0,
              }}
            >
              ✗
            </button>
          </div>
        ))}
      </div>

      {/* Relations */}
      <div
        style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}
      >
        <h3
          style={{
            textTransform: "uppercase",
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            color: "#888",
            marginTop: 0,
          }}
        >
          Kausalrelationen ({acceptedRelationCount})
        </h3>

        {relations.map((rel, i) => (
          <div
            key={i}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 4,
              padding: "0.75rem",
              marginBottom: "0.75rem",
              opacity: rel.rejected ? 0.4 : 1,
            }}
          >
            <p
              style={{
                margin: "0 0 0.5rem",
                fontFamily: "monospace",
                fontSize: "0.85rem",
              }}
            >
              {rel.source} → {rel.target}
            </p>

            <div
              style={{
                display: "flex",
                gap: "0.75rem",
                alignItems: "center",
                marginBottom: "0.25rem",
              }}
            >
              <label style={{ fontSize: "0.8rem", color: "#888", flexShrink: 0 }}>
                Mechanismus:
              </label>
              <input
                value={rel.mechanism}
                onChange={(e) =>
                  setRelations((prev) =>
                    prev.map((r, j) => (j === i ? { ...r, mechanism: e.target.value } : r))
                  )
                }
                disabled={rel.rejected}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: 3,
                  padding: "0.2rem 0.4rem",
                  fontSize: "0.8rem",
                  flex: 1,
                }}
              />
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <label style={{ fontSize: "0.8rem", color: "#888" }}>EpistemicStatus:</label>
                <select
                  value={rel.epistemic_status}
                  onChange={(e) =>
                    setRelations((prev) =>
                      prev.map((r, j) =>
                        j === i ? { ...r, epistemic_status: e.target.value } : r
                      )
                    )
                  }
                  disabled={rel.rejected}
                  style={{ fontSize: "0.8rem", padding: "0.2rem" }}
                >
                  {EPISTEMIC_STATUS_OPTIONS.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={() =>
                  setRelations((prev) =>
                    prev.map((r, j) => (j === i ? { ...r, rejected: !r.rejected } : r))
                  )
                }
                style={{
                  background: rel.rejected ? C.rejected.bg : "none",
                  border: "1px solid #ddd",
                  borderRadius: 3,
                  padding: "0.25rem 0.5rem",
                  cursor: "pointer",
                  fontSize: "0.85rem",
                  color: rel.rejected ? C.rejected.text : "inherit",
                }}
              >
                ✗
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Model name + save */}
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem" }}>
        <label
          style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.25rem" }}
        >
          Modellname
        </label>
        <input
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          placeholder="Modellname eingeben…"
          style={{
            width: "100%",
            padding: "0.4rem",
            marginBottom: "1rem",
            boxSizing: "border-box",
            fontSize: "0.9rem",
          }}
        />
        {error && (
          <p style={{ color: C.rejected.text, marginBottom: "0.5rem", fontSize: "0.85rem" }}>
            {error}
          </p>
        )}
        <button
          onClick={save}
          disabled={saving || !modelName.trim()}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            background: modelName.trim() ? "#1D9E75" : "#e0e0e0",
            color: modelName.trim() ? "#fff" : "#999",
            border: "none",
            borderRadius: 4,
            cursor: modelName.trim() ? "pointer" : "not-allowed",
            width: "100%",
          }}
        >
          {saving ? "Speichere…" : "CausalModel anlegen und speichern →"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/thormar/klartext/frontend && npm test -- WirkgefuegeVorschlag.test
```

Expected: All 5 tests pass.

- [ ] **Step 5: Run typecheck**

```bash
cd /Users/thormar/klartext/frontend && npm run typecheck
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/WirkgefuegeVorschlag.tsx frontend/src/pages/WirkgefuegeVorschlag.test.tsx
git commit -m "feat: implement WirkgefuegeVorschlag screen with slot/relation cards and save flow"
```

---

## Task 7: Screen 4 — CausalModelEditor Extensions

Adds Slots table, Relations table, and Verknüpfte Narrative to the existing CausalModelEditor. Also handles `location.state.selectedModelId` for auto-selection after Screen 3 save.

**Files:**
- Modify: `frontend/src/pages/CausalModelEditor.tsx`

- [ ] **Step 1: Write failing test**

Create `frontend/src/pages/CausalModelEditor.test.tsx`:

```typescript
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import CausalModelEditor from "./CausalModelEditor";

vi.mock("../lib/api", () => ({
  api: {
    causalModels: {
      list: vi.fn().mockResolvedValue([
        { id: "cm1", title: "Test Modell", status: "draft", axioms: [], slots: [], relations: [] },
      ]),
      get: vi.fn().mockResolvedValue({
        id: "cm1",
        title: "Test Modell",
        status: "draft",
        axioms: [],
        slots: [
          { id: "s1", identifier: "co2_emissionen", slot_type: "physical_quantity", epistemic_status: "incomplete" },
        ],
        relations: [
          {
            id: "r1",
            identifier: "co2_to_temp",
            source_slot_id: "s1",
            target_slot_id: "s2",
            mechanism: "Treibhauseffekt",
            polarity: null,
            epistemic_status: "incomplete",
          },
        ],
      }),
    },
    narratives: {
      list: vi.fn().mockResolvedValue([
        { id: "n1", title: "Klartext Narrativ", causal_model_id: "cm1" },
        { id: "n2", title: "Anderes Narrativ", causal_model_id: null },
      ]),
    },
  },
}));

function renderWithSelectedModel(selectedModelId?: string) {
  return render(
    <MemoryRouter
      initialEntries={[
        { pathname: "/causal-model", state: selectedModelId ? { selectedModelId } : null },
      ]}
    >
      <Routes>
        <Route path="/causal-model" element={<CausalModelEditor />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("CausalModelEditor — extensions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("auto-selects model from location state and shows its title as heading", async () => {
    renderWithSelectedModel("cm1");
    // Model should be auto-selected and its title appear as h2 heading
    expect(await screen.findByRole("heading", { name: "Test Modell" })).toBeInTheDocument();
  });

  it("shows Slots section with slot identifier", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("co2_emissionen")).toBeInTheDocument();
    });
  });

  it("shows Kausalrelationen section with relation identifier", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("co2_to_temp")).toBeInTheDocument();
    });
  });

  it("shows Verknüpfte Narrative section with linked narrative", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("Klartext Narrativ")).toBeInTheDocument();
    });
  });

  it("does not show unlinked narratives in Verknüpfte Narrative", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.queryByText("Anderes Narrativ")).not.toBeInTheDocument();
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/thormar/klartext/frontend && npm test -- CausalModelEditor.test
```

Expected: FAIL — no Slots section, no Relations section, no linked narratives.

- [ ] **Step 3: Implement CausalModelEditor extensions**

Replace the entire `frontend/src/pages/CausalModelEditor.tsx` with:

```tsx
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api, CausalModel, NarrativeSummary } from "../lib/api";

// ---------------------------------------------------------------------------
// Colour constants from ui_experiment_scope.md
// ---------------------------------------------------------------------------
const BADGE = {
  incomplete: { bg: "#FAEEDA", text: "#854F0B" },
  axiomatic: { bg: "#EAF3DE", text: "#3B6D11" },
} as const;

function EpistemicBadge({ status }: { status: string }) {
  const style = status === "axiomatic" ? BADGE.axiomatic : BADGE.incomplete;
  return (
    <span
      style={{
        fontSize: "11px",
        background: style.bg,
        color: style.text,
        padding: "0.1rem 0.4rem",
        borderRadius: 3,
      }}
    >
      {status}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Table styles
// ---------------------------------------------------------------------------
const TABLE: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: "12px",
};

const TH: React.CSSProperties = {
  textAlign: "left",
  color: "#aaa",
  fontWeight: "normal",
  borderBottom: "1px solid #e0e0e0",
  paddingBottom: "0.4rem",
  paddingRight: "1rem",
};

const TD: React.CSSProperties = {
  padding: "0.4rem 1rem 0.4rem 0",
  borderBottom: "1px solid #f0f0f0",
  verticalAlign: "top",
};

// ---------------------------------------------------------------------------
// CausalModelEditor — Screen 4
// ---------------------------------------------------------------------------

export default function CausalModelEditor() {
  const location = useLocation();
  const navigate = useNavigate();
  const locationState = location.state as { selectedModelId?: string } | null;

  const [models, setModels] = useState<CausalModel[]>([]);
  const [selected, setSelected] = useState<CausalModel | null>(null);
  const [narratives, setNarratives] = useState<NarrativeSummary[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [axiomLabel, setAxiomLabel] = useState("");
  const [axiomDescription, setAxiomDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.causalModels.list(), api.narratives.list()])
      .then(([cms, narrs]) => {
        setModels(cms);
        setNarratives(narrs);
        // Auto-select model if navigated from Screen 3
        const targetId = locationState?.selectedModelId;
        if (targetId) {
          const match = cms.find((m) => m.id === targetId);
          if (match) {
            loadModel(targetId);
          }
        }
      })
      .catch(() => setError("API nicht erreichbar"));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function loadModel(id: string) {
    try {
      const model = await api.causalModels.get(id);
      setSelected(model);
    } catch {
      setError("Modell konnte nicht geladen werden.");
    }
  }

  async function createModel() {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      const model = await api.causalModels.create(newTitle.trim());
      setModels((prev) => [...prev, model]);
      setSelected(model);
      setNewTitle("");
    } catch {
      setError("Modell konnte nicht erstellt werden.");
    } finally {
      setLoading(false);
    }
  }

  async function addAxiom() {
    if (!selected || !axiomLabel.trim() || !axiomDescription.trim()) return;
    setLoading(true);
    try {
      await api.causalModels.addAxiom(selected.id, axiomLabel.trim(), axiomDescription.trim());
      const updated = await api.causalModels.get(selected.id);
      setSelected(updated);
      setAxiomLabel("");
      setAxiomDescription("");
    } catch {
      setError("Axiom konnte nicht hinzugefügt werden.");
    } finally {
      setLoading(false);
    }
  }

  const linkedNarratives = narratives.filter((n) => n.causal_model_id === selected?.id);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "2rem" }}>
      <aside>
        <h2 style={{ marginTop: 0 }}>Wirkmodelle</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <ul style={{ listStyle: "none", padding: 0 }}>
          {models.map((m) => (
            <li key={m.id}>
              <button
                onClick={() => loadModel(m.id)}
                style={{
                  background: selected?.id === m.id ? "#e8f0fe" : "none",
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  padding: "0.5rem 0.75rem",
                  marginBottom: "0.5rem",
                  cursor: "pointer",
                  width: "100%",
                  textAlign: "left",
                }}
              >
                {m.title}
              </button>
            </li>
          ))}
        </ul>

        <div style={{ marginTop: "1rem", borderTop: "1px solid #eee", paddingTop: "1rem" }}>
          <h3 style={{ marginTop: 0, fontSize: "0.9rem" }}>Neues Wirkmodell</h3>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Titel"
            style={{
              width: "100%",
              padding: "0.4rem",
              marginBottom: "0.5rem",
              boxSizing: "border-box",
            }}
            onKeyDown={(e) => e.key === "Enter" && createModel()}
          />
          <button onClick={createModel} disabled={loading || !newTitle.trim()}>
            Anlegen
          </button>
        </div>
      </aside>

      <main>
        {!selected ? (
          <p style={{ color: "#888" }}>Wirkmodell auswählen oder neu anlegen.</p>
        ) : (
          <>
            <h2 style={{ marginTop: 0 }}>{selected.title}</h2>
            <p style={{ color: "#888", fontSize: "0.85rem" }}>Status: {selected.status}</p>

            {/* Slots -------------------------------------------------------- */}
            <h3 style={{ marginBottom: "0.5rem" }}>Slots ({selected.slots.length})</h3>
            {selected.slots.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.85rem" }}>Keine Slots.</p>
            ) : (
              <table style={TABLE}>
                <thead>
                  <tr>
                    <th style={TH}>identifier</th>
                    <th style={TH}>slot_type</th>
                    <th style={TH}>epistemic_status</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.slots.map((s) => (
                    <tr key={s.id}>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{s.identifier}</td>
                      <td style={TD}>{s.slot_type}</td>
                      <td style={TD}>
                        <EpistemicBadge status={s.epistemic_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Relations ---------------------------------------------------- */}
            <h3 style={{ marginBottom: "0.5rem", marginTop: "2rem" }}>
              Kausalrelationen ({selected.relations.length})
            </h3>
            {selected.relations.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.85rem" }}>Keine Relationen.</p>
            ) : (
              <table style={TABLE}>
                <thead>
                  <tr>
                    <th style={TH}>Identifier</th>
                    <th style={TH}>Quelle</th>
                    <th style={TH}>Ziel</th>
                    <th style={TH}>Mechanismus</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.relations.map((r) => (
                    <tr key={r.id}>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{r.identifier}</td>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{r.source_slot_id}</td>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{r.target_slot_id}</td>
                      <td style={TD}>{r.mechanism ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Axiome ------------------------------------------------------- */}
            <h3 style={{ marginTop: "2rem" }}>Axiome ({selected.axioms.length})</h3>
            {selected.axioms.length === 0 ? (
              <p style={{ color: "#888" }}>Noch keine Axiome.</p>
            ) : (
              <ul style={{ paddingLeft: "1.2rem" }}>
                {selected.axioms.map((a) => (
                  <li key={a.id} style={{ marginBottom: "1rem" }}>
                    <strong>{a.label}</strong>
                    <p style={{ margin: "0.25rem 0 0", color: "#444" }}>{a.description}</p>
                  </li>
                ))}
              </ul>
            )}

            {/* Add axiom form ----------------------------------------------- */}
            <div
              style={{
                marginTop: "2rem",
                padding: "1rem",
                border: "1px solid #ddd",
                borderRadius: 4,
                background: "#fafafa",
              }}
            >
              <h3 style={{ marginTop: 0 }}>Axiom hinzufügen</h3>
              <input
                value={axiomLabel}
                onChange={(e) => setAxiomLabel(e.target.value)}
                placeholder="Bezeichnung"
                style={{
                  width: "100%",
                  padding: "0.4rem",
                  marginBottom: "0.5rem",
                  boxSizing: "border-box",
                }}
              />
              <textarea
                value={axiomDescription}
                onChange={(e) => setAxiomDescription(e.target.value)}
                placeholder="Beschreibung"
                rows={3}
                style={{
                  width: "100%",
                  padding: "0.4rem",
                  marginBottom: "0.5rem",
                  boxSizing: "border-box",
                }}
              />
              <button
                onClick={addAxiom}
                disabled={loading || !axiomLabel.trim() || !axiomDescription.trim()}
              >
                Axiom speichern
              </button>
            </div>

            {/* Verknüpfte Narrative ----------------------------------------- */}
            <h3 style={{ marginTop: "2rem" }}>
              Verknüpfte Narrative ({linkedNarratives.length})
            </h3>
            {linkedNarratives.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.85rem" }}>Keine verknüpften Narrative.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0 }}>
                {linkedNarratives.map((n) => (
                  <li key={n.id} style={{ marginBottom: "0.4rem" }}>
                    <button
                      onClick={() => navigate("/narrative")}
                      style={{
                        background: "none",
                        border: "1px solid #ddd",
                        borderRadius: 4,
                        padding: "0.4rem 0.75rem",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.4rem",
                      }}
                    >
                      📖 {n.title} →
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </main>
    </div>
  );
}
```

**Note about the Relations table:** The backend returns `source_slot_id` and `target_slot_id` as UUIDs, not human-readable identifiers. For the experiment scope, we show the UUIDs (or an abbreviated form). A full implementation would resolve them to slot identifiers via the `slots` array — that optimisation is out of scope here.

- [ ] **Step 4: Run tests**

```bash
cd /Users/thormar/klartext/frontend && npm test -- CausalModelEditor.test
```

Expected: All 5 tests pass.

- [ ] **Step 5: Run full frontend test suite**

```bash
cd /Users/thormar/klartext/frontend && npm test
```

Expected: All tests pass (App.test.tsx + all new test files).

- [ ] **Step 6: Run typecheck**

```bash
cd /Users/thormar/klartext/frontend && npm run typecheck
```

Expected: No errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/CausalModelEditor.tsx frontend/src/pages/CausalModelEditor.test.tsx
git commit -m "feat: extend CausalModelEditor with slots, relations, and linked narratives"
```

---

## Task 8: Full Regression Run

Verifies that Plan E hasn't broken anything.

**Files:** None

- [ ] **Step 1: Run backend unit + integration tests**

```bash
cd /Users/thormar/klartext && klartext test
```

Expected: All 449 unit tests pass.

- [ ] **Step 2: Run all frontend tests**

```bash
cd /Users/thormar/klartext/frontend && npm test
```

Expected: All frontend tests pass.

- [ ] **Step 3: Run frontend typecheck**

```bash
cd /Users/thormar/klartext/frontend && npm run typecheck
```

Expected: No TypeScript errors.

- [ ] **Step 4: Mark Plan E complete in PENDING.md**

In `docs/superpowers/plans/PENDING.md`, update the Plan E entry:

```markdown
## Plan E — Frontend Extensions

**Status:** DONE (2026-06-04)
**Plan:** `docs/superpowers/plans/2026-06-04-frontend-extensions.md`
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/PENDING.md
git commit -m "docs: mark Plan E complete"
```
