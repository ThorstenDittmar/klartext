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

**Status:** Not started. Depends on Plan B.

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

**Status:** Not started. Depends on Plans B + C.

**What:** End-to-end workflow from narrative to minimal Wirkgefüge.

Steps 2–6 from `experiment_scope.md`:
- `POST /narratives/{id}/analyse` → NarrativeAnalysisService + provider port
- `POST /narratives/{id}/suggest-wirkgefuege` → WirkgefuegeSuggestionService
- Frontend extensions for the analysis workflow

---

## Other open items

- **N-01** (`clean_up.md`): `precondition-postcondition.md.rtf` als Markdown neu speichern
- **N-04** (`clean_up.md`): CausalModelFederation vollständig spezifizieren
- **N-06** (`clean_up.md`): Community Model Specs anlegen
- **Fragment aus narrative_units.typ entfernen** — erst bei Phase-2-Migration zu `document_nodes`
