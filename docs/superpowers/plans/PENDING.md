# Pending Implementation Plans

## Post-Mortem H01 — Coverage-Tracker

Konsolidierte Befunde aus dem H01-Post-Mortem (7 Gewerke + Hannibal + OE), thematisch
geschnitten. Wir arbeiten in drei Achsen ab: **organisatorisch zuerst**, dann qualitativ,
dann fachlich. Nach allen Achsen gegen diese Liste abgleichen — kein Punkt darf offen bleiben.

Status je Punkt: ☐ offen · ◐ in Arbeit · ☑ abgedeckt

**Thema 1 — Naht ohne Vertrag** *(quer: org + qual + fachlich)*
- ☐ Kein verbindlicher Schnittstellen-/Kontrakt-Abschnitt im Plan vor Dispatch
- ☐ Architektur-Sign-off erfolgte getrennt pro Plan, nie an der Grenze
- ☐ Cross-Domain-Repository-Zugriff nie als Port eskaliert/freigegeben
- ☐ Zwei widersprüchliche Wahrheiten über leeren `content` schon im Backend selbst

**Thema 2 — Niemand besaß die End-to-End-Verifikation** *(qual)*
- ☐ „tested manually"-DOD unerfüllbar zugewiesen (CLI-Agent ohne Browser)
- ☐ Tests strukturell blind für den API-Vertrag (Mocks + Fakes, Naht ungetestet)
- ☐ Kein Integrations-/Contract-Gate vor Merge; keine Browser-Verifikations-Ownership

**Thema 3 — Qualität als Nachgang statt Entwurf** *(qual + org)*
- ☐ Kriterien-Eigentümer (QA) sah Pläne erst beim Roundup-Gate
- ☐ DODs entstanden ohne Kriterien-Eigentümer
- ☐ Prüfkriterien werden nicht vor Implementierungsstart vereinbart/unterschrieben

**Thema 4 — Plan als Dokument unzuverlässig** *(qual)*
- ☐ Zeitlich veraltet (vor Komponenten-Bau geschrieben, Props/Beispiele stale)
- ☐ Faktische Fehler (falscher CLI-Befehl, venv-Pfad, sich selbst widersprechender Test, nicht-existente Fixture, Seed angenommen)
- ☐ Constraints nur in Schema/Memory, nicht inline im Plan

**Thema 5 — Koordination und Parallelität** *(org)*
- ☐ Parallel-Dispatch ohne Dependency-/Pfad-Überlappungs-Gate
- ☐ Doppelarbeit (Fake zweimal gebaut, 5 identische Fix-Commits via Cherry-Pick)
- ☐ Kein Merge-Owner, kein Merge-Protokoll, keine Reihenfolge
- ☐ Cross-Domain-Berührung ohne Koordinationspunkt (fremde Testdatei auf fremdem Branch)

**Thema 6 — Grenzen dokumentiert, aber nicht spürbar** *(org)*
- ☐ Domain-Grenzübertritte als durchgängiges Muster (mehrere Agents inkl. Hannibal + OE)
- ☐ `task-readiness` von keinem Agent aufgerufen — Schutz-Skill wirkungslos
- ☐ SA-Eskalations-Trigger nie in Hannibals claude.md verankert
- ☐ Negative Constraints nur in Memory, nicht erzwungen
- ☐ Hannibal ging zu tief in die Implementierung statt zu koordinieren

**Offene Strukturfragen aus dem Sprint** *(org)*
- ☐ Verwaiste Dateien ohne Domain-Owner (`debug.py`)
- ☐ Commit-Ownership-Graubereich (`.storybook/`)
- ☐ DevOps↔UX/UI Direktkanal
- ☐ Technical Writer ja/nein

---

## Inventur-Befund — "Der Code kam in git an, die Prozess-Schicht nicht"

Ergebnis der Ablage-Inventur (8 Gewerke + Hannibal + OE, jeder hat real nachgeprüft).
Zentrale Diagnose: Der **produktive Code** ging via PR #41/#42 auf `main` (versioniert).
Die **Prozess-/Koordinations-Schicht** (Pläne, ADRs, Agent-Definitionen, Kontrakte,
Sign-offs, Skills) ist nie committed worden — sie lebt im Working Tree oder in `~/.claude`.
Ausgerechnet die Schicht, deren Fehlen H01 kippte, war technisch nirgends.

**Sechs Kategorien von „nicht sauber abgelegt":**

- **A — Auf Platte, nie committed (Verlustrisiko):** ADR 0007+0008 · CLAUDE.md (uncommitted changes) · `frontend-testing.md` (untracked, QA stark erweitert) · `agents/qa/claude.md` (uncommitted) · **die 2 H01-Pläne** · **`agents/hannibal/` komplett** · PENDING.md (uncommitted) · viele `agents/*/claude.md`, Design-Specs, neue Frontend-Komponenten
- **B — Außerhalb Repo (`~/.claude`, nicht teamweit, kein Backup):** OE User-Skills + Memory · SA 21 Memory-Dateien · QA `qa-review`+`qa-retro` Skills · Hannibal Auto-Memory + `launch.json` (von falscher Rolle erzeugt)
- **C — Hat keinen Ort (ephemer = H01-Wurzel):** Architektur-Sign-offs (nur Chat) · Schnittstellen-Kontrakte (Dokumenttyp existiert nicht)
- **D — Falscher Ort vs. dokumentierte Konvention:** `.semgrep/rules/` flach statt `qa/`+`arch/` (3 Agents melden es) · `api/providers/` gemeinsamer Mischbereich statt domain-isoliert
- **E — Laufender Zustand / Drift (System, nicht git):** Supabase Cloud-DB vs. Migrations · **Branch Protection auf `main` nicht aktiv** (mechanischer Grund für ungeprüfte Merges) · `ANTHROPIC_API_KEY` fehlt als GitHub-Secret · Token→`index.css`-Sync nur Konvention
- **F — Fehlende Artefakte:** Causal-Model Health-Infra-Test · `qa-learnings/` leer · keine Audit-Semgrep-Rules (Ports & Adapters) · Branch-Switching-Kollateral (fremde Dateien auf NE-Branch)

**Strukturelle Konsequenz:** Jeder Ergebnis-Typ braucht einen definierten, versionierten
Ort, bevor Guards (Thema 6) greifen können. A/B/C/D sind dieselbe Aufgabe: „gib jedem
Output ein Zuhause in git".

---

## Offene Delegationen

Aufgaben die in Agent-Sessions delegiert wurden und noch nicht erledigt sind.
Pre-compact Schritt 1.5 trägt sie automatisch ein — via Sub-Agent-Dispatch, kein User-Briefing.
Nach Erledigung: Zeile löschen oder als ~~durchgestrichen~~ markieren.

| Agent | Aufgabe | Delegiert von | Datum |
|---|---|---|---|
| OE | Prozess-Absicherung: QA-Briefing-Pflicht bei neuen UX/UI-Komponenten — Frontend-Skill Checklist + Pre-compact-Check; Lösung mit QA abstimmen | UX/UI Expert | 2026-06-08 |
| OE | DevOps ↔ UX/UI Direktkanal klären: DevOps hat vorgeschlagen direkt auf UX/UI-Briefings zu antworten (kein User-Relay). Prüfen ob "User ist immer der Kanal" hier eine definierte Ausnahme bekommt; betrifft `agents/devops/claude.md` + `agents/ux/claude.md` | DevOps | 2026-06-08 |
| OE | Alle Agent-claude.md mit Hannibal-Koordinationsabschnitt ergänzen: task-readiness Skill bei Dispatch, Branch-Schema `task/<H-id>/<slug>`, QA ist immer in Hannibals Koordinationsrunde dabei (für QA-Agent), SA-Eskalation via Hannibal (für SA-Agent) | OE | 2026-06-08 |
| OE | Post-Mortem nach erstem Hannibal-Durchlauf: Hannibal geht zu tief in die Implementierung — soll auf fachlicher Ebene bleiben. Konkrete Regel für `agents/hannibal/claude.md` formulieren | User | 2026-06-08 |
| OE | Post-Mortem: Commit-Ownership bei Grenzfällen klären — gilt "commit = write access"? Oder darf ein Agent Dateien außerhalb seines Domains committen wenn er auf einem Branch arbeitet der diese Dateien berührt? Konkreter Anlass: DevOps fragte ob `frontend/.storybook/preview.ts` von DevOps committet werden darf (UX/UI-Domain). Regel für alle Agents formulieren. | DevOps | 2026-06-08 |
| OE | Post-Mortem: Narrative Expert hat Supabase-Client inline mit `os.environ` erstellt statt via Dependency Injection (`dependencies.py` + `Depends()`). Prüfen ob das bereits im Code ist, wenn ja: fixen. Klären warum NE vom DI-Muster abgewichen ist — fehlt die Regel im `agents/narrative/claude.md`? Ggf. NE briefen. | User | 2026-06-08 |
| OE | Post-Mortem: Brauchen wir einen Technical Writer Agent für Benutzerhandbuch und Produktdokumentation? Klären: wer schreibt heute Doku, fällt das durch die Raster, und ist das ein eigener Domain oder eine Rolle die bei einem bestehenden Agent angesiedelt werden kann. | User | 2026-06-08 |
| OE | Post-Mortem: Verwaiste Dateien ohne Domain-Eigentümer — `api/routers/debug.py` + `api/tests/test_debug_router.py` hatten CI-Fehler, kein Agent war zuständig (Code kam direkt von Thorsten). DevOps hat gefixt. Strukturfrage: Was passiert mit Code außerhalb aller Agent-Domains? Optionen: (1) DevOps als Auffangbecken, (2) SA für Crosscutting-Code (Debug, Health, CLI), (3) explizite shared-Domain, (4) Zuweisung bei Commit. OE bewertet + Regel formulieren. | DevOps | 2026-06-08 |
| ~~UX/UI~~ | ~~Token-Diskrepanz synchronisieren nach Merge H01-B1~~ | ~~UX/UI Expert~~ | ~~DONE PR #44~~ |

---

## Plan H01-A — Narrative Unit Domain Model

**Status:** ✅ GEMERGT (2026-06-08 13:30:51 UTC, PR #42)  
**Plan:** `docs/superpowers/plans/2026-06-08-narrative-unit-domain.md`  
**Agent:** Narrative Expert  
**Branch:** `task/H01-A/narrative-unit-domain` (gelöscht)

**What:** Vollständiges Python-Domänenmodell `NarrativeUnit` (Work / Part / Chapter / Scene / Fragment) auf der bestehenden `narrative_units` Tabelle. Neuer `/narrative-units` Router mit 5 Endpoints (health, tree, create, update, delete). DB-Migration für `ON DELETE CASCADE` auf `parent_id`.

---

## Plan H01-B — Manuskriptansicht

**Status Phase 1:** ✅ GEMERGT (2026-06-08 13:30:59 UTC, PR #41)  
**Status Phase 2:** ✅ GEMERGT (2026-06-08, PR #43)  
**Plan:** `docs/superpowers/plans/2026-06-08-manuskriptansicht.md`  
**Agent:** UX/UI Expert  
**Branch Phase 1:** `task/H01-B1/manuscript-components` (gelöscht)  
**Branch Phase 2:** `task/H01-B2/manuscript-view-page`

**What:** Design-Token-System in `index.css` + 5 neue Komponenten (Breadcrumb, WordCountLabel, SceneBreak, AutosaveIndicator, BottomBar) + `ManuscriptView` Seite mit einem `<textarea>` pro Fragment und Debounce-Autosave (1,5s).

---

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

- ~~**Migration 20260603000001 anwenden**~~ — DONE.
- ~~**Integration-Tests narrative_repository reparieren**~~ — DONE (2026-06-04).
- ~~**Backend → Frontend Workflow-Regel in CLAUDE.md**~~ — DONE. Steht in CLAUDE.md § API Contract Rule.
- **N-01** (`clean_up.md`): `precondition-postcondition.md.rtf` als Markdown neu speichern — **[Owner: DevOps]**
- **N-04** (`clean_up.md`): CausalModelFederation vollständig spezifizieren — **[Owner: Causal Model Expert]**
- **N-06** (`clean_up.md`): Community Model Specs anlegen — **[Owner: Community Expert]**
- **Fragment aus narrative_units.typ entfernen** — erst bei Phase-2-Migration zu `document_nodes` — **[Owner: Narrative Expert]** (Phase 2)

---

## Frontend-Infrastruktur — Offene Punkte (2026-06-05)

### Mittelfristig

- **Interaktives Storybook (KI-Chat in Storybook)** — **[Owner: UX/UI + DevOps + Backend]**
  User-Wunsch: Chat-Fenster unten links in Storybook um KI-Feedback direkt beim Betrachten
  von Komponenten zu bekommen. Technische Voraussetzungen: eigener `/chat`-Endpunkt im
  Backend (oder Proxy-Lösung), CORS-Config für Port 6006, und ein Storybook Global Decorator
  der das Chat-UI injiziert. UI-Teil (UX/UI) kann sofort gebaut werden — der Blocker ist
  der Backend-Endpunkt. Thema zurückstellen bis Component Library stabiler ist.

- **Vitest + React Testing Library einrichten** — **[Owner: UX/UI + DevOps]**
  Frontend hat aktuell null Tests. Minimaler Einstieg: Smoke-Tests die prüfen ob
  Komponenten ohne Crash rendern. Angehen nachdem der Frontend-Skill getestet und
  die erste isolierte Komponente gebaut wurde.
  Analogie zum Backend: Domain → Service → Repository → Router;
  Frontend-Entsprechung: Utils → Komponenten → Screens → E2E.

- **OpenAPI → TypeScript-Generierung (Option B)** — **[Owner: UX/UI + DevOps]**
  FastAPI generiert `/openapi.json`. Das Tool `openapi-typescript` erzeugt daraus
  TypeScript-Interfaces und eliminiert den manuellen Sync zwischen Pydantic-Schemas
  und `api.ts`. Verhindert stillen API-Contract-Drift.
  Aufwand: mittel. Priorität: hoch sobald das Interface größer wird.

### Skills und Tooling

- **`verify`-Skill für das Backend anlegen** — **[Owner: QA]**
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

Setup — **[Owner: DevOps]**:
- `pip install semgrep` in dev dependencies
- `.semgrep/rules/` Ordner anlegen
- Semgrep in pre-commit + CI (`lint.yml`) einbinden

Erste Regeln in `.semgrep/rules/arch/` — **[Owner: SA]**:

- `klartext/repo-logs-first` — jede Methode in `*Repository`-Klassen muss `self.logger` vor dem ersten nicht-logger Statement aufrufen
- `klartext/exception-naming` — Exception-Klassen müssen auf `Error` enden
- `klartext/factory-methods` — Klassen in `models/` müssen `create()` und `from_record()` haben

Erste Regeln in `.semgrep/rules/qa/` — **[Owner: QA]**:

- `klartext/no-hex-in-style` (TypeScript) — kein hardcoded Hex in `style={{...}}` (Design-Token-Enforcement, kein Arch-Pattern)
- `klartext/no-jsx-strings` — keine String-Literale im JSX (i18n-Enforcement, kein Arch-Pattern)

### Phase 2 — Weitere Regeln — **[Owner: SA + QA]**

SA (`.semgrep/rules/arch/`):
- `klartext/repo-log-level` — `debug` für Reads, `info` für Writes
- `klartext/service-naming` — Service-Klassen enden auf `Service`
- `klartext/repository-naming` — Repository-Klassen enden auf `Repository`
- `klartext/no-db-in-service` — kein `supabase`-Import in `services/`
- `klartext/router-health` — ⚠️ SA + QA abstimmen vor Umsetzung: CLAUDE.md sagt "enforced by test, not review comment" — Semgrep-Regel ggf. redundant zu bestehendem Test-Enforcement

QA (`.semgrep/rules/qa/`):
- Test-spezifische Regeln (QA definiert selbst welche, sobald Phase 1 läuft)

### Neue Pattern-Regel

Ab jetzt gilt: Wenn ein neues Pattern in CLAUDE.md oder einem Skill etabliert wird,
wird im selben Commit eine entsprechende Semgrep-Regel angelegt. Kein Pattern ohne Regel.

### Später (kein konkreter Termin)

- **Style Dictionary einrichten** — **[Owner: UX/UI + DevOps]**
  JSON-Tokens in `design/tokens/*.json` automatisch nach `frontend/src/index.css`
  und optional nach TypeScript-Konstanten generieren. Eliminiert den manuellen
  Sync zwischen Token-JSON und CSS Custom Properties.

- **Playwright für kritische User-Flows** — **[Owner: QA + DevOps]**
  E2E-Tests für den Experiment-Workflow (NarrativeEditor → Analyse →
  WirkgefügeVorschlag → CausalModelEditor). Erst sinnvoll wenn Workflow stabil ist.
  Rollentrennung beim Start: QA definiert welche Flows getestet werden + Assertions; DevOps richtet Infrastruktur ein (CI, package.json, Playwright-Config).

- **Design-System → Code Workflow (Workflow 3) vollständig definieren** — **[Owner: UX/UI + OE]**
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
