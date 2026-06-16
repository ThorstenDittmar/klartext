# Pending Implementation Plans

Plans that are next in line. Tests may already be written (RED).

---

## H01-422 Walking Skeleton — Status (2026-06-10, Hannibal)

**Work-Alpha: CLOSED** (Retro 2, 2026-06-10). Record:
`docs/method/enactment/learnings/2026-06-10-h01-422-retrospective.md`.
*Foundation Established* danach 5/6 — letzte Box („non-negotiables per practice") bei OE.

Erster realer Lauf der Methode am H01-422-Wund („+ Absatz hinzufügen" → 422 → kein Tippen möglich).
Alle Schritte mit `task-readiness`-Gate dispatcht; Sign-off an der Naht VOR den Builder-Dispatches.

| Schritt | Ergebnis |
|---|---|
| Kontrakt surfaced (RC6) + SA-Sign-off: Variante R1 Lazy-create, Seam-Owner = Narrative | ✅ |
| PR #53 Kontrakt-Doku `docs/contracts/narrative-units-fragment.md` (Narrative) | ✅ gemergt |
| PR #54 Contract-Tests, 17/17 (QA) — schließt die fehlende Contract-Test-Schicht | ✅ gemergt |
| PR #55 Lazy-create ManuscriptView, 93/93 + tsc clean (UX/UI) | ✅ gemergt |
| PR #56/#57 stash-gerettete Tree-Edits separat · PR #58 PostCompact-Hook-Promotion | ✅ gemergt |
| End-to-End-Verifikation via Claude_Preview VOR Merge: Tippen → 201, kein 422 | ✅ bestanden |
| Wissens-Captures aller Beteiligten (+ 2 Nicht-Beteiligte) inkl. Friction-Reports | ✅ |
| Retrospective (OE; DELETE-Befund → Produkt-Task, Friction → Register/Aktionen) | ✅ 2026-06-10 |

Verwahr-Depot der Retro-Inputs: Hannibal-Memory `project_h01422_retro_inputs.md` (nach Retro verorten + löschen).

---

## Offene Delegationen (aktiv)

> Die historische Delegations-Tabelle aus H01 liegt auf `salvage/h01-working-tree` (Commit e73a461,
> PENDING.md dort §„Offene Delegationen") und kommt mit dem geplanten Teardown. Hier nur AKTIVE Einträge.
> Befund Audit O4 (2026-06-10): Dieser Abschnitt fehlte auf `main` — Tracking-Lücke, hiermit geschlossen.

| Agent | Aufgabe | Delegiert von | Datum |
|---|---|---|---|
| SA (via Hannibal-Task) | Semgrep-Regel Ports & Adapters: „Service importiert nie direkt einen Adapter" — dokumentiert, nicht enforced | Audit Expert | 2026-06-10 |
| OE | Fake-Ownership in `api/tests/fakes/` klären (`fake_narrative_repository.py`: NE-Interface, kein Owner) | Audit Expert | 2026-06-10 |
| ~~OE (Register)~~ | ~~Improvement-Kandidat: Semgrep-Gate gegen `# type: ignore`~~ — **erledigt 2026-06-10**, Register-Zeile in §3 (Owner SA+DevOps) | Causal Model Expert | 2026-06-10 |
| ~~UX/UI~~ | ~~A1–A3 aus Hannibals Verwahr-Depot in `agents/ux/claude.md` eintragen~~ — **erledigt 2026-06-12** (PR #84, `f7cc1c7`, OE-Sign-off als Review-Kommentar, artefakt-verifiziert auf main); Depot-Freigabe an Hannibal erteilt | OE (pre-compact 2026-06-10) | 2026-06-10 |
| ~~DevOps~~ | ~~Mini-Inkrement landen~~ — **erledigt 2026-06-10** (`c20a79d`, artefakt-verifiziert: Permissions in den Skripten) | OE (pre-compact 2026-06-10) | 2026-06-10 |
| SA | CLAUDE.md § Agent Roles & Boundaries auf das neue Startmodell aktualisieren (Terminal-Launcher statt App, `allowed-tools.txt`, Worktrees, Generationswechsel) — passt zum ADR-0010-Auftrag, gleiche Quelle (Register-Zeile Strukturumbau) | OE | 2026-06-11 |
| OE (Nachfolge-Session) | Merge-Methoden-Policy in `practices/merge-protocol.md` eintragen, sobald Hannibal ratifiziert hat (DevOps-Vorschlag: squash default / `--method merge` für Stacks / kein rebase — Anfrage liegt in Hannibals Postfach seit 2026-06-12); danach DevOps Bescheid geben („ratifizierung ausstehend" aus der Spec streichen) | OE (Pre-Restart 2026-06-12) | 2026-06-12 |
| OE (Nachfolge-Session) | Record-Review-Addenda DELETE-404 einsammeln: Community ✅ (kein Befund), CME + Audit ausstehend (Record-Auftrag lag in ihren Postfächern vor der Migration — bei den Nachfolge-Sessions nachhaken); danach Einzeiler im Register | OE (Pre-Restart 2026-06-12) | 2026-06-12 |
| DevOps | ADR-0014 Agent-Provenance: commit-msg-Hook + CI-Check für Trailer `Agent: <slug>` (spawn-aware) bauen — Briefing liegt in DevOps' Inbox, unblocked seit #129 auf main | System Architect | 2026-06-16 |
| SA → DevOps | S3-Vendoring-Lint (`.semgrep/rules/arch/`): Regel, die fehlschlägt, wenn eine Wrapper-Karte Upstream-Resource-Inhalt nacherzählt statt zu deklarieren (RC4-Schutz) — neben den ADR-0014-Hook in die SA→DevOps-Pipeline | System Architect (F0.2-#148-Ratifikation) | 2026-06-16 |
| UX (+ QA-Kriterien) | `verify`-Skill-Drift nachziehen (`docs/superpowers/skills/verify.md`) + L2-Karte synchronisieren: (a) 5-Screen-URLs veraltet ggü. App.tsx (`/reading` nicht gemountet; `/causal-model`+`/narrative` brauchen IDs; `NarrativeEditor`→`NarrativeDetail`); (b) Browser-MCP-Reihenfolge — Claude_Preview primär, Claude_in_Chrome Fallback (localhost-Sperre) | OE (F0.2-P-D, UX-geflaggt #150) | 2026-06-16 |
| DevOps | Stale Agent-Spawn-Worktrees aufräumen: nach den F0.1/F0.2-Spawns liegen ~7 Worktrees unter `~/klartext/.claude/worktrees/agent-*` (Branches bereits gemerged+gelöscht auf origin) — `git worktree prune` / `remove` | OE (F0.2-Anchor 2026-06-16) | 2026-06-16 |

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
- **[CLOSED (Backend) 2026-06-12 · Frontend vertagt — Produkt-Task, aus Retro 2 via Hannibal] DELETE-on-unknown-id Kontrakt** — `SupabaseNarrativeUnitRepository.remove()` ist idempotent (kein 404), `update()` ist strikt (404). Inkonsistenz. Gleiches Muster wie der 422 (RC6 ungeborener Kontrakt × RC3 API-Konsistenz). Von QA per qa-review gefunden (2026-06-09, gesichert als Investigation-Task). Entscheid nötig: Option A idempotent→204 (Test umbauen) vs. Option B strikt→404 (`remove()` strikt machen, Frontend behandelt 404). Braucht Narrative-Semantik × SA-Konsistenz. Retro-2-Entscheid: als Produkt-Task via Hannibal an Narrative (Seam-Owner, Semantik + Kontrakt-Doku) mit SA-Sign-off (API-Konsistenz) routen; bei Option B zusätzlich UX/UI-Briefing (404-Handling). **Erster Build-Run im neuen Betriebsmodell (ADR 0010).**
  - **Requirements-Alpha: Bounded.** Beleg: QA-Reachability-Analyse (2026-06-09/10, `remove()` vs. `update()` Verhalten dokumentiert), explizite A/B-Frage, Seam-SoT `docs/contracts/narrative-units-fragment.md` existiert. Dieses Paket bewegt es nach **Coherent/Acceptable** (Seam-Owner-Entscheid + SA-Sign-off, dokumentiert in `docs/contracts/`) und **Addressed** (Contract-Test kodiert den Entscheid, Implementierung erfüllt ihn). `task-readiness` prüft beim Dispatch gegen diese Zeile.
  - **Software-System-Alpha: Usable** (seit #55, E2E-verifiziert) **→ Ready erreicht (Backend-Vertrag)**: konsistentes, regressions-gesichertes API-Vertragsverhalten — Contract-Test (#82) grün, kodiert die strikte 404-Semantik; Backend ist canonical SoT. Die ursprüngliche Close-Klausel „verifiziertes 404-Handling im Frontend" ist **gegenstandslos**: es existiert kein Frontend-Lösch-Flow (kein Aufrufer von `deleteNarrativeUnit`, keine Lösch-UI — artefakt-verifiziert 2026-06-12), also kein Konsument des 404. Frontend-Handling vertagt an das künftige Lösch-UI-Feature (siehe neue Zeile unten).
  - **Run-Record (2026-06-12, Hannibal, Merge-Owner):**
    - Entscheid: **Option B (strikt → 404)**, Narrative (Seam-Owner) + SA-Sign-off 2026-06-12.
    - PRs: **#81** Narrative (Kontrakt + strikte `remove()`, 630 Unit-Tests) · **#82** QA (komplementäre Contract-Tests: double-delete, PATCH/DELETE-Symmetrie, verbatim Error-Body; 634 passed). #82 main-basiert, enthält #81 vollständig.
    - QA-Nebenbefund: pre-existing Fake-Contract-Lücke (`FakeNarrativeUnitRepository.update()` lenient, echtes Repo strikt) — Fake strikt gemacht, Guard-Tests (Service + Integration) ergänzt.
    - **Kontrakt-Divergenz (Flag OE, user-approved) — AUFGELÖST:** SAs signierte Kontrakt-Fassung lag uncommitted im Haupt-Tree, #81 enthielt Narratives eigene Fassung (Worktree-Blindheit), #82 testete Narratives Error-Body verbatim. SA-Review 2026-06-12: **Branch-Fassung ist canonical**, SAs Hauptbaum-Fassung verworfen; Error-Body englisch + ID korrekt → QAs verbatim-Test konsistent, kein Korrektur-Dispatch. SA hat zudem CLAUDE.md auf englische API-Error-Bodies korrigiert (SA-Domäne).
    - **Merge (Flag OE):** DevOps als Gatekeeper, Reihenfolge #81 → #82, SHA-erhaltend via Merge-Commit. Artefakt-verifiziert (Hannibal): main-Log 9fcaf00 (#81) → 9d47f03 (#82), alle 4 SHAs auf main, beide PRs MERGED, Branches gelöscht. Merge-Protocol-Checklist erfüllt.
    - **Abweichung benannt (Flag OE):** QA arbeitete aus der App-Session (Roster: app), Dispatch-Plan sah Migration vor — stille Abweichung, Ergebnis korrekt. Migration zu QAs nächstem natürlichen Start (nach laufender qa-retro), getaktet vom User, Roster-Eigentum OE. Keine Re-Migration für fertige Arbeit erzwungen.
    - **Frontend-Welle vertagt (Befund task-readiness, User-Entscheid 2026-06-12):** UX/UI-task-readiness fand vor dem Coden: kein Produktiv-Aufrufer von `deleteNarrativeUnit`, keine Unit-Lösch-UI (ManuscriptView: create/read/update, kein delete) — artefakt-verifiziert (grep). Damit kein Konsument des 404 → Frontend-Handling wäre totes Handling. Product-Owner-Entscheid: vertagen, kein Scope-Creep. Strukturell derselbe Fehlertyp wie 422/DELETE selbst (nicht-verifizierte Annahme über einen Flow); diesmal vom Gate **vor** dem Build gefangen. → Retro-Input an OE.
- **[VERTAGT — Produkt-Feature, aus DELETE-404-Befund 2026-06-12] Unit-/Fragment-Lösch-UI** — Es gibt im Frontend keinen Weg, eine Narrative-Unit zu löschen (`deleteNarrativeUnit` in `api.ts` ohne Aufrufer). Eigenes Feature, kein API-Fix: Lösch-Button + Bestätigungsdialog (ja/nein?) + Tree-Removal + welche Tree-Ebene löschbar. Braucht Product-Owner-Scope (User) und ggf. SA-Interaktionsmuster. **Bringt das 404-Handling mit** (DELETE auf bereits gelöschte/unbekannte ID → deutsche Meldung im bestehenden `setError(...)`-Pattern, kein Ghost, kein Retry, Tree-Refresh — Consumer-Guidance steht bereits in `docs/contracts/narrative-units-fragment.md`). i18n der Meldung fällt in den generellen Frontend-i18n-Scope (noch kein i18n-Setup im Frontend, alle user-facing Strings aktuell hardcoded-deutsch).

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

### Skills und Tooling

- **`verify`-Skill für das Backend anlegen**
  Gegenstück zu `docs/superpowers/skills/verify.md`. Protokoll: `klartext health`,
  relevante API-Endpoints aufrufen, `klartext test` für den geänderten Layer.
  Ablage: `docs/superpowers/skills/verify-backend.md` + Wrapper `~/.claude/skills/verify-backend/`.

---

## Architectural Linting — Plan (2026-06-05)

**Entscheidung:** ADR 0006 — alle Patterns aus CLAUDE.md und Skills werden automatisch geprüft.
**Primäres Tool:** Semgrep (strukturelle Muster, language-agnostic, YAML-Regeln)
**Ergänzend:** custom ruff rules (Python), custom eslint rules (TypeScript)
**Ablage:** `.semgrep/rules/` im Repo

### Phase 1 — Semgrep aufsetzen + höchste Priorität

Setup:
- `pip install semgrep` in dev dependencies
- `.semgrep/rules/` Ordner anlegen
- Semgrep in pre-commit + CI (`lint.yml`) einbinden

Erste Regeln (höchster Wert, sofort sichtbar):

**Backend:**
- `klartext/repo-logs-first` — jede Methode in `*Repository`-Klassen muss `self.logger` vor dem ersten nicht-logger Statement aufrufen
- `klartext/no-hex-in-style` (Python-seitig) — kein hardcoded Hex in Python-Code
- `klartext/exception-naming` — Exception-Klassen müssen auf `Error` enden
- `klartext/factory-methods` — Klassen in `models/` müssen `create()` und `from_record()` haben

**Frontend:**
- `klartext/no-hex-in-style` (TypeScript) — kein `"#XXXXXX"` in `style={{...}}`
- `klartext/async-finally` — jeder `async` Event-Handler muss `finally` enthalten

### Phase 2 — Weitere Regeln

- `klartext/repo-log-level` — `debug` für Reads, `info` für Writes
- `klartext/service-naming` — Service-Klassen enden auf `Service`
- `klartext/repository-naming` — Repository-Klassen enden auf `Repository`
- `klartext/no-db-in-service` — kein `supabase`-Import in `services/`
- `klartext/router-health` — jeder Router hat mindestens eine `/health`-Route
- `klartext/no-jsx-strings` — keine String-Literale im JSX (außer technische Werte)

### Neue Pattern-Regel

Ab jetzt gilt: Wenn ein neues Pattern in CLAUDE.md oder einem Skill etabliert wird,
wird im selben Commit eine entsprechende Semgrep-Regel angelegt. Kein Pattern ohne Regel.

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
