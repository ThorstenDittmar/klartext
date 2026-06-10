# Coding Standards

## Language
- All code in English: variable names, function names, classes, comments, commit messages, API endpoints
- Communication with the team in German
- User-facing strings are externalized via i18n (`t('key')`) — never hardcoded in any language.
  See `design/i18n.md` for rules. Backend error messages that reach the API response: German.
- Documentation (technical/process/method docs): English — ADRs, skills, method docs under `docs/superpowers/`.
  Scope: development and method documentation only. Product-facing content (e.g. *Wirkgefüge*, domain terms) keeps German.
  Convention for now; candidate for future lint enforcement.

## Test-Driven Development
Use the `tdd` skill. It extends the `superpowers:test-driven-development` skill with project-specific standards.

## Architectural Linting
Every pattern documented here or in a skill file must have a corresponding automated check.
See ADR 0006 and `docs/superpowers/plans/PENDING.md` for the rule set and implementation plan.

**Rule:** When establishing a new pattern, add the Semgrep/eslint rule in the same commit.
Patterns without automated enforcement are documentation, not standards.

## Frontend Development
Use the `frontend` skill. It loads the project-level style guide and agent instructions from
`docs/superpowers/skills/frontend.md`.

### API Contract Rule
When modifying a Pydantic response schema (`api/schemas/`), update the corresponding
TypeScript interface in `frontend/src/lib/api.ts` in the same commit.
Run `tsc --noEmit` in `frontend/` locally before committing to catch type drift early.

## Architecture

### Layer Structure
```
api/
  routers/      ← Controller: HTTP routing only, delegates immediately to service
  services/     ← Business logic as OOP classes
  repositories/ ← Data access (Supabase) as OOP classes
  schemas/      ← Pydantic: request/response shapes
  models/       ← Domain objects (pure Python classes)
  exceptions/   ← Exception classes per layer
```

### Responsibilities
- **Router**: receive request, call service, return response — nothing else
- **Service**: business logic, orchestrates repositories, no database knowledge
- **Repository**: data access only, no business logic
- **Schema**: defines what goes in and out (Pydantic)
- **Domain object**: knows its own invariants and how to change itself

### Layer Boundary: routers → providers forbidden

`api.routers` may NOT import from `api.providers` — tach enforces this boundary.
Router helper functions that convert provider result types to Pydantic schemas must
use `Any` for the provider-typed parameters instead of importing the concrete type.
This is architecturally correct, not a type shortcut — the conversion helper lives
in the router, but the provider type does not belong there.

```python
# correct — Any because routers cannot import from providers
def _to_analyse_response(result: Any) -> AnalyseNarrativeResponse: ...

# wrong — violates tach boundary
from api.providers.narrative_analysis_provider import NarrativeAnalysisResult
def _to_analyse_response(result: NarrativeAnalysisResult) -> AnalyseNarrativeResponse: ...
```

### Health Subendpoints

Every new service router gets a `GET /<resource>/health` endpoint:
- Returns HTTP 200 with at least `{"status": "ok"}`
- No authentication required (publicly accessible)
- Checked in infrastructure tests
- Add it first when creating a new router, before any other endpoints

## Object-Oriented Programming
- Backend code is consistently object-oriented
- Business logic lives in classes, not loose functions
- Changes to domain objects are implemented as explicit methods (`user.change_email(...)`)
- Never set properties directly from outside the object

### Factory Methods
Every domain class has two factory methods:
```python
@classmethod
def create(cls, request: CreateXRequest) -> "X": ...   # new object from user input

@classmethod
def from_record(cls, record: dict) -> "X": ...          # reconstruct from database record
```

### Properties
- Getters via `@property`
- Setters (`@x.setter`) only when no business context — prefer explicit methods

## Persistence
- No automatic dirty tracking
- Always save explicitly via repository: `find → change → save`
- The repository does not know how to construct domain objects — that belongs to the domain class

## Repository Logging

Every repository method logs as its **first action**, before any database call:

```python
class UserRepository:
    logger = logging.getLogger(__name__)

    def find_by_id(self, user_id: str) -> User | None:
        """Find user by ID."""
        self.logger.debug("UserRepository.find_by_id: user_id=%s", user_id)
        # ... database call

    def save(self, user: User) -> None:
        """Persist a user."""
        self.logger.info("UserRepository.save: user_id=%s", user.id)
        # ... database call
```

- `debug` for reads, `info` for writes (create, update, delete)
- Log message format: `ClassName.method_name: param=value`
- Log sensitive fields never (no passwords, tokens, PII)
- Fake repositories log too — it helps debug service-layer tests

## Dependency Injection
- Wire dependencies in `dependencies.py` via FastAPI `Depends()`
- Chain: `get_supabase_client` → `get_x_repository` → `get_x_service`
- Routers receive services via `Depends()` — never instantiate directly
- In tests: override via `app.dependency_overrides`

## Error Handling
```
Domain object  → DomainError   (InvalidEmailError, UserInactiveError)
Service        → ServiceError  (EmailAlreadyExistsError, PermissionError)
Repository     → RepositoryError (RecordNotFoundError, DatabaseError)
Router         → no try/except — central exception handlers translate to HTTP status codes
```

### Grundregel: Kein Fehler darf still verschwinden

**Fachliche Exceptions** (NarrativeNotFoundError, SceneNotFoundError, etc.) werden **immer** behandelt
und dem User als sinnvolle Fehlermeldung angezeigt — kein generisches „Etwas ist schiefgelaufen".

```python
@app.exception_handler(NarrativeNotFoundError)
async def handle_narrative_not_found(request: Request, exc: NarrativeNotFoundError) -> JSONResponse:
    """Returns 404 with a human-readable message — always active."""
    return JSONResponse(status_code=404, content={"error": str(exc)})
```

Frontend: API-Fehler werden abgefangen und als sinnvolle deutsche Meldung dargestellt.
Ein 404 zeigt „Narrativ nicht gefunden", kein leeres UI oder endloser Spinner.

**Infrastruktur-/unerwartete Exceptions** (DatabaseError, connection errors, unhandled exceptions):
- In **Development**: kein Handler — voller Stack Trace schlägt durch, ist im Terminal sichtbar
- In **Production**: erst wenn nötig einen generischen 500-Handler hinzufügen
- Niemals still schlucken (leeres `except: pass`, `catch (e) {}` ohne Reaktion)

```python
# WRONG — silently swallows infrastructure errors
try:
    result = await db.query(...)
except Exception:
    pass  # developer sees nothing, user sees nothing

# CORRECT — let it propagate; developer sees full stack trace in development
result = await db.query(...)
```

**Regel:** Kein catch-all Handler. Kein stilles Schlucken. Fachliche Fehler → sinnvolle Meldung
für den User. Infrastruktur-Fehler → in Development sichtbar durchschlagen.

## Type Hints
- Mandatory everywhere: parameters, return values, class attributes
- Optional values: `X | None` (not `Optional[X]`)
- Lists: `list[X]`, dicts: `dict[str, X]`
- All methods fully annotated including `-> None`

## Naming Conventions
| What | Convention | Example |
|---|---|---|
| Classes | PascalCase | `UserService` |
| Methods/Variables | snake_case | `create_user` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private attributes | `_` prefix | `self._email` |
| Files | snake_case | `user_service.py` |
| Services | `Service` suffix | `UserService` |
| Repositories | `Repository` suffix | `UserRepository` |
| Pydantic input | `Request` suffix | `CreateUserRequest` |
| Pydantic output | `Response` suffix | `UserResponse` |
| Exceptions | `Error` suffix | `InvalidEmailError` |
| Fakes (tests) | `Fake` prefix | `FakeUserRepository` |

## Infrastructure as Code
All essential operations are scripted — no manual steps in terminals, dashboards, or GUIs.

**CLI (typer):**
- All essential infrastructure commands are encapsulated: `klartext start`, `klartext clean`, `klartext testdata`, etc.
- Initial bootstrap only via `setup.sh` (before Python is available)
- New developers get a fully working environment with a single command

**Synchronized updates:**
- Every installation or framework update must update both the CLI scripts AND the health checks
- Never update one without the other

**Version control:**
- All scripts and health checks live in GitHub
- Commit messages explain the *why*, not the *what*

**Principles:**
- Database schema via migration files — never manual SQL in the Supabase dashboard
- Environment variables via `.env.example` as template
- Deployment via scripts or CI/CD pipeline
- Supabase configuration (RLS, Storage, Edge Functions) as code

### Anthropic-Client auf macOS

Der Standard-httpx-Client des Anthropic SDK verwendet certifi's CA-Bundle,
das auf macOS möglicherweise nicht alle nötigen Zertifikate enthält.

**Lösung:** `_make_anthropic_client()` in `api/dependencies.py` übergibt
`http_client=httpx.AsyncClient(verify=ssl.create_default_context())`.
Dieselbe Lösung gilt für `check_anthropic()` in `api/services/health_service.py`.

**Symptom:** `APIConnectionError: Connection error.` beim ersten Analyse- oder
Konsistenz-Aufruf, obwohl das Netzwerk erreichbar ist.

**Ursache:** certifi bündelt ein eigenes CA-Bundle das nicht mit dem macOS-System
synchronisiert wird. `ssl.create_default_context()` liest dagegen direkt aus
`/private/etc/ssl/cert.pem`.

### Definition of Done — Infrastructure tasks

Before closing any infrastructure-related task, verify each item:

- [ ] `bash setup.sh` completes without errors on a simulated fresh environment (no manually pre-installed extras)
- [ ] The developer documentation describes exactly what the scripts do — no more, no less
- [ ] Every new environment variable is added to `.env.example` AND documented in `developer-guide.md`
- [ ] `klartext health` reflects the current infrastructure state (new dependencies → new health check)
- [ ] The CI smoke-test workflow passes (`setup-smoke-test.yml`)
- [ ] Infrastructure tests for the change exist in `api/tests/infrastructure/` and QA has reviewed them via `qa-review`

### Definition of Done — Database migrations

Every new migration file must pass these checks before committing:

- [ ] `klartext db reset` completes without errors — this is the only test that counts; an incremental apply on an existing DB is not sufficient
- [ ] All table and column names in the migration match the **current** schema state (check against the most recent migration, not the initial schema)
- [ ] The migration is idempotent where possible (`IF NOT EXISTS`, `IF EXISTS`, `ALTER TABLE … ADD COLUMN IF NOT EXISTS`)
- [ ] The corresponding infrastructure test in `api/tests/infrastructure/` verifies the expected schema shape (e.g. new column exists, FK resolved by PostgREST)

**Why `klartext db reset` and not incremental apply:**
Incremental apply runs the new migration on top of an existing schema that already has all prior renames and additions. This hides references to old names. `db reset` replays every migration from scratch — the only way to catch stale references.

## Testing Standards

### Router test completeness

Every router endpoint must have at least one router test. No endpoint ships without a test.

**Checklist — when adding a new endpoint:**
- [ ] Happy path: correct HTTP status and response body
- [ ] Error path: 404 or 422 for invalid input (where applicable)
- [ ] Health endpoint: `GET /<resource>/health` returns 200 with `{"status": "ok"}`

**Why:** Router tests are the only layer that verifies the HTTP contract (status codes, JSON shape, dependency wiring). A missing router test means the endpoint has never been called programmatically — the first caller is the user.

### Supabase integration tests for complex queries

Every repository method that uses JOINs, embedded PostgREST counts, or multiple tables must have a `@pytest.mark.integration` test against the real database.

Simple CRUD (single table, no aggregation) is covered by the fake. Complex queries are not.

**Signals that a test is needed:**
- Query uses PostgREST embedded counts (`table(count)`)
- Query joins across multiple tables
- Query relies on FK relationships in the PostgREST schema cache

Add the test to `api/tests/test_<resource>_repository.py` and mark it `@pytest.mark.integration`.

**Why:** PostgREST embedded counts fail silently at the fake layer — the fake returns `0` always. The only way to verify the query works is to run it against the real database.

### Fake contract completeness

Fake repositories must implement the full interface contract. Silent constants that mask missing functionality are not allowed.

**Allowed:**
```python
claim_count=self._claim_counts.get(narrative.id, 0)  # test-controllable via set_claim_count()
```

**Not allowed:**
```python
claim_count=0  # silent constant — tests can never verify this is wrong
```

If a fake cannot implement a method meaningfully, it must raise `NotImplementedError` explicitly — never silently return a default that hides the gap.

For computed fields (e.g. counts derived from related objects), provide a test helper to set the expected value:
```python
def set_claim_count(self, narrative_id: str, count: int) -> None:
    """Sets the claim count for a narrative. Used in tests to simulate saved claims."""
    self._claim_counts[narrative_id] = count
```

**Why:** A fake that always returns `claim_count=0` lets tests pass even when the service ignores the count entirely. The gap is only caught when the real database returns a wrong value.

### Health endpoint enforcement

The health endpoint rule (`GET /<resource>/health` on every router) is enforced by test, not by review comment.

Every router test file must include:
```python
async def test_<resource>_health_returns_200() -> None:
    """Expects GET /<resource>/health to return HTTP 200 with status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/<resource>/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**Why:** A review comment is forgotten under time pressure. A failing test is not.

## Comments
- Every non-trivial method gets a docstring
- Methods describe what they do
- Trivial getters or simple pass-throughs do not need a comment

```python
def create_user(self, request: CreateUserRequest) -> User:
    """Creates a new user and persists it. Raises EmailAlreadyExistsError if the email is taken."""
    ...

# trivial — no comment needed
@property
def email(self) -> str:
    return self._email
```

## Git Workflow

### Before switching between local and Codespace
Always verify that all commits are pushed before switching environments:

```bash
git log --oneline origin/main..HEAD
```

If any commits are listed: push first, then switch.

### Case-only renames on macOS
macOS uses a case-insensitive filesystem. Renaming `NarrativEditor.tsx` to `NarrativeEditor.tsx`
with plain `mv` is a no-op — the file never actually moves. Git may stage it correctly locally,
but the rename never reaches the remote.

Always use a temporary name as an intermediate step:

```bash
git mv OldName.tsx _temp.tsx
git mv _temp.tsx NewName.tsx
```

This produces two real renames that work reliably on all platforms.

## Wirkgefüge Design Principles

These principles govern all causal model (Wirkgefüge) code and architecture decisions.

**No truth machine.** The platform does not evaluate whether content is empirically true.
It checks only internal consistency, completeness and transparency of models.
`EpistemicStatus` describes the transparency status of an element, not its external truth.
Counterfactual, speculative or marginal models are valid as long as their assumptions are explicit.

**All semantic operations run top-down.** CausalComponents are context-free — they do not
know their container. All semantic operations (namespace resolution, scope checking,
completeness verification, validation procedures) always start at the container and
traverse downward. No `_container` attribute on CausalComponent. A component can live
in multiple containers simultaneously (e.g. CausalMixin). `resolve(identifier)` is always
called on CausalModel, never on a component.

**Explicitness over implicitness.** Interpretive decisions may be made during modelling
but must not remain as unresolved ambiguity in the finished model. Ambiguities must be
explicitly marked as variants, conflicts, gaps or open questions.

## Agent Roles & Boundaries

The klartext project uses specialized Claude Code agents. Each agent has a defined domain —
files outside that domain require a DevOps Briefing or explicit coordination.

**Jeder Agent liest beim Session-Start seine Hoheitswissen-Datei:**
`agents/<name>/claude.md` — enthält Domain, Write-Access, domänenspezifische Regeln, Skills.

Each agent has its own directory: `agents/<name>/`
- `agents/<name>/start.sh` — startet die Session mit den richtigen Permissions
- `agents/<name>/claude.md` — Hoheitswissen und domänenspezifische Regeln

Project-level baseline permissions (all agents): `.claude/settings.json`

| Agent | Domain |
|---|---|
| OE | Multi-Agent-Struktur, Onboarding, Zusammenarbeit (`agents/` vollständig, cross-agent Skills in `docs/superpowers/skills/`) |
| Hannibal | Projektleitung, Planung, Koordination großer Arbeitspakete (`docs/superpowers/plans/`) |
| DevOps | Infrastructure, CI/CD, Tooling — Gatekeeper |
| System Architect | Architecture decisions, Coding Standards (`CLAUDE.md`, `docs/adr/`, `.semgrep/rules/arch/`) |
| UX/UI | React components, frontend (`frontend/src/`) — führt `verify`-Skill aus (QA-owned) |
| QA | Tests, coverage (`api/tests/`, `.semgrep/rules/qa/`), Frontend-Kriterien (`docs/superpowers/skills/verify.md`, `frontend-testing.md`) |
| Narrative Expert | Narrative domain backend (`api/*/narrative*`) |
| Causal Model Expert | Wirkgefüge backend (`api/*/causal_model*`) |
| Audit Expert | Verification procedures, claim extraction (`api/providers/`) |
| Community Expert | User/community backend (`api/*/user*`) |

### Way of Working — our method (SEMAT/Essence)

Our way of working is being forged as an explicit, evolving **method**, using **Essence/SEMAT** as the
meta-language. Before proposing changes to how we work, read the method document set under
`docs/superpowers/improvement/`:

- `semat-definition.md` — self-contained reference for the meta-language (Kernel, Alphas, Practices, Methods)
- `alpha-states.md` — the kernel Alpha state checklists (the checkable lifecycle)
- `semat-glossary.md` — our process/method vocabulary (the terms to use)
- `practices/` — our Practices (composable how-tos; e.g. `improvement-step.md`, `document-scoping.md`)
- `continuous-improvement.md` — our decisions, rationale, RCA and plan

Having read these, communicate with OE about the way of working **using this vocabulary** (Alphas, states,
Practices, Methods) and propose changes that slot into the Kernel rather than reinventing it.
Owner of the method: OE.

### Domain-Respekt — gilt für alle Agents

Kein Agent bietet an, Aufgaben außerhalb seines Domains zu erledigen —
auch wenn er die technische Fähigkeit dazu hätte.

**Stattdessen:** Briefing an den zuständigen Agent formulieren und dem User übergeben.

```
Briefing an <Agent>
Aufgabe:   [Was erledigt werden sollte]
Kontext:   [Warum es gerade aufgefallen ist]
Vorschlag: [Optionaler Ansatz]
```

Der User entscheidet ob und wann er das Briefing weiterleitet.
Domain-fremde Arbeit anzubieten ist kein Gefallen — es untergräbt die Klarheit des Systems.

---

### Infrastructure Perimeter — DevOps exclusive

No other agent may modify these without a DevOps Briefing:

```
.github/workflows/
setup.sh
.pre-commit-config.yaml
tach.toml
api/pyproject.toml
frontend/package.json
frontend/package-lock.json
frontend/vite.config.ts
frontend/tsconfig*.json
frontend/eslint.config.js
api/cli.py
.claude/settings.json
```

### DevOps Briefing Protocol

When any agent needs an infrastructure change, they send a briefing — DevOps decides how:

```
Need:      [What is needed]
Why:       [Technical or business reason]
Domain:    [Dependencies / CI/CD / Config / CLI / Database / Other]
Approach:  [Optional suggestion]
Impact:    [Which agents/environments affected]
```

### System Architect ↔ DevOps Collaboration

SA defines rules (Semgrep, tach, ruff, layer boundaries) → DevOps enforces technically (CI steps, hooks).
Neither acts alone: a rule without enforcement is documentation, not a standard.

### Adding a new agent

Use the `agent-onboarding` skill (OE-Domain). OE defines the domain, creates the start script and the knowledge file — no DevOps Briefing needed.

## Ports & Adapters
Isolate technical components (e.g. verification procedures) via abstract interfaces:

```python
from abc import ABC, abstractmethod

class ReadabilityChecker(ABC):       # Port — defines the contract
    @abstractmethod
    def check(self, text: str) -> ReadabilityResult: ...

class FleschReadabilityChecker(ReadabilityChecker):   # Adapter — local implementation
    ...

class ExternalReadabilityChecker(ReadabilityChecker): # Adapter — external service
    ...
```

- Services know only the port, never the adapter
- Each verification procedure: own folder, own abstract class, own tests
- For tests: `FakeXChecker` that returns deterministic results
- Implementations can be swapped without touching the service
