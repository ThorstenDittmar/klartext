# Pending Implementation Plans

Plans that are next in line. Tests may already be written (RED).

---

## Plan B — Actor + Claim Evolution

**Status:** DONE (2026-06-03)  
**Plan:** `docs/superpowers/plans/2026-06-03-actor-claim-evolution.md`

**What:** Breaking changes to existing Actor and Claim domain objects, propagated
through all layers (repository, schemas, router, frontend, DB migration).

Actor changes:
- `name` → `label`
- `typ` → `actor_type`
- `description` → `notes`
- New field: `entity_ref: str | None` (ID of linked causal model entity)

Claim changes:
- New field: `label: str`
- New field: `status: ClaimStatus` (DRAFT / LINKED / UNRESOLVED)
- New field: `wirkgefuege_ref: str | None`
- New method: `link_to_wirkgefuege(ref_id)`
- New method: `mark_unresolved()`

Files affected: `models/narrative.py`, `models/claim.py`, `schemas/narratives.py`,
`routers/narratives.py`, `repositories/supabase_narrative_repository.py`,
`seeddata.py`, `frontend/src/pages/NarrativeEditor.tsx`,
`frontend/src/lib/api.ts`, DB migration for `narrative_actors`.

---

## Plan C — Wirkgefüge Persistence

**Status:** DONE (2026-06-04)  
**Plan:** `docs/superpowers/plans/2026-06-04-wirkgefuege-persistence.md`

**What:** Persist Slot and CausalRelation to the database.

New DB tables: `slots`, `causal_relations`
New repositories: `SupabaseSlotRepository`, `SupabaseCausalRelationRepository`
New schemas + routers:
- `POST /causal-models/{id}/slots`
- `POST /causal-models/{id}/relations`
- `PUT  /causal-models/{id}/relations/{id}`
- `POST /claims/{id}/link-to-wirkgefuege`

---

## Plan D — Analysis Workflow

**Status:** DONE (2026-06-04)
**Plan:** `docs/superpowers/plans/2026-06-04-analysis-workflow.md`

**What:** End-to-end workflow from narrative to minimal Wirkgefüge.

Steps 2–6 from `experiment_scope.md`:
- `POST /narratives/{id}/analyse` → NarrativeAnalysisService + provider port
- `POST /narratives/{id}/suggest-wirkgefuege` → WirkgefuegeSuggestionService
- Frontend extensions for the analysis workflow

---

## Plan E — Frontend Extensions

**Status:** DONE (2026-06-04)
**Spec:** `docs/superpowers/specs/ui_experiment_scope.md`
**Plan:** `docs/superpowers/plans/2026-06-04-frontend-extensions.md`

**What:** 4 Screens für den Experiment-Workflow — Narrativ → Analyse → Wirkgefüge-Vorschlag → CausalModel.
- Task 1: Backend: `causal_model_id` in `NarrativeSummaryResponse`
- Task 2: `api.ts` — neue TypeScript-Typen + API-Calls
- Task 3: `App.tsx` — neue Routes
- Task 4: Screen 1 (`NarrativeEditor`) — "Analysieren →" Button
- Task 5: Screen 2 (`NarrativeAnalyse`) — Actor/Claim-Karten mit Bestätigen/Verwerfen
- Task 6: Screen 3 (`WirkgefuegeVorschlag`) — Slot/Relation-Karten + Speicherfluss
- Task 7: Screen 4 (`CausalModelEditor`) — Slots + Relationen + Verknüpfte Narrative
- Task 8: Full Regression Run

---

## Other open items

- ~~**Migration 20260603000001 anwenden**~~ — DONE. `supabase migration up --local` bestätigt: Local database is up to date.
- ~~**Integration-Tests narrative_repository reparieren**~~ — DONE (2026-06-04). Alle 6 Tests grün.
- **N-01** (`clean_up.md`): `precondition-postcondition.md.rtf` als Markdown neu speichern
- **N-04** (`clean_up.md`): CausalModelFederation vollständig spezifizieren
- **N-06** (`clean_up.md`): Community Model Specs anlegen
- **Fragment aus narrative_units.typ entfernen** — erst bei Phase-2-Migration zu `document_nodes`

---

## Frontend-Infrastruktur — Offene Punkte (2026-06-05)

### Sofort (beim nächsten Backend-Schema-Refactoring miterledigen)

- **Backend → Frontend Workflow-Regel in CLAUDE.md ergänzen:**
  Wer ein Pydantic-Response-Schema ändert, aktualisiert `frontend/src/lib/api.ts`
  im selben Commit. `tsc --noEmit` lokal prüfen bevor committed wird.

### Mittelfristig

- **Vitest + React Testing Library einrichten**
  Frontend hat aktuell null Tests. Minimaler Einstieg: Smoke-Tests die prüfen ob
  Komponenten ohne Crash rendern. Angehen nachdem der Frontend-Skill getestet und
  die erste isolierte Komponente gebaut wurde.
  Analogie zum Backend: Domain → Service → Repository → Router;
  Frontend-Entsprechung: Utils → Komponenten → Screens → E2E.

- **OpenAPI → TypeScript-Generierung (Option B)**
  FastAPI generiert `/openapi.json`. Das Tool `openapi-typescript` erzeugt daraus
  TypeScript-Interfaces und eliminiert den manuellen Sync zwischen Pydantic-Schemas
  und `api.ts`. Verhindert stillen API-Contract-Drift.
  Aufwand: mittel. Priorität: hoch sobald das Interface größer wird.

### Später (kein konkreter Termin)

- **Style Dictionary einrichten**
  JSON-Tokens in `design/tokens/*.json` automatisch nach `frontend/src/index.css`
  und optional nach TypeScript-Konstanten generieren. Eliminiert den manuellen
  Sync zwischen Token-JSON und CSS Custom Properties.

- **Playwright für kritische User-Flows**
  E2E-Tests für den Experiment-Workflow (NarrativeEditor → Analyse →
  WirkgefügeVorschlag → CausalModelEditor). Erst sinnvoll wenn Workflow stabil ist.

- **Design-System → Code Workflow (Workflow 3) vollständig definieren**
  Wenn ein Token in `design/tokens/*.json` geändert wird: wer prüft welche
  Komponenten betroffen sind, und wie wird sichergestellt dass `index.css` aktualisiert
  wird? Aktuell: CHANGELOG.md-Eintrag + manuelles Pending Task — kein automatischer Guard.

## Lessons Learned — Refactoring-Scope

Bei Actor/Claim-Refactorings (Plan B) wurde `api/cli.py` zunächst vergessen —
es enthält Seeddata-Code der dieselben Domain-Felder referenziert wie Service/Router.
**Regel für künftige Pläne:** Bei Domain-Feld-Umbenennungen immer `api/cli.py` in die
Dateiliste aufnehmen.

Bei Claim-API-Änderungen (Plan B) wurden drei weitere Dateien übersehen, die erst beim
nächsten Test-Run auffielen:
- `api/routers/claims.py` — baut `ClaimResponse` direkt aus Domain-Objekten
- `api/tests/fakes/fake_claim_repository.py` — konstruiert `Claim(...)` direkt im Fake
- `api/tests/test_claims_router.py` — erstellt `Claim`-Objekte in der Fake-Service-Klasse

**Regel für künftige Pläne:** Bei Änderungen an `Claim` oder `Actor` immer auch diese
Dateien in die Scope-Liste aufnehmen.
