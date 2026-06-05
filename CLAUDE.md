# Coding Standards

## Language
- All code in English: variable names, function names, classes, comments, commit messages, API endpoints
- Communication with the team in German
- User-facing strings are externalized via i18n (`t('key')`) — never hardcoded in any language.
  See `design/i18n.md` for rules. Backend error messages that reach the API response: German.

## Test-Driven Development
Use the `tdd` skill. It extends the `superpowers:test-driven-development` skill with project-specific standards.

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
- Exception handlers registered centrally via `@app.exception_handler`
- **In development**: handlers inactive — errors propagate with full stack trace
- **In production**: handlers active — controlled error responses for users

```python
if settings.environment == "production":
    @app.exception_handler(RecordNotFoundError)
    def handle_not_found(request: Request, exc: RecordNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})
```

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
