# Coding Standards

## Language
- All code in English: variable names, function names, classes, comments, commit messages, API endpoints
- Communication with the team in German
- User-facing strings (UI text, error messages) in German

## Test-Driven Development
- Always write tests before implementation (TDD)
- TDD cycle: Domain → Service → Repository → Router

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

## Testing Strategy
Four levels, always from inside out:

1. **Domain objects** — pure unit tests, no mocks, no external systems
2. **Services** — unit tests with fake repositories (in-memory, no Supabase)
3. **Repositories** — integration tests against real test database
4. **Router** — API tests via FastAPI `TestClient`

**Infrastructure tests** — separate category, runs independently:
- Is the database reachable?
- Is Supabase Storage available?
- Are external services responding?

**Health check endpoint** — `/health` returns infrastructure status for monitoring and deployments.

**Test naming**: methods read as specifications:
```python
def test_create_user_rejects_duplicate_email(): ...
def test_change_email_raises_error_for_invalid_format(): ...
```

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
- Tests describe the expectation
- Trivial getters or simple pass-throughs do not need a comment

```python
# method
def create_user(self, request: CreateUserRequest) -> User:
    """Creates a new user and persists it. Raises EmailAlreadyExistsError if the email is taken."""
    ...

# test
def test_create_user_rejects_duplicate_email():
    """Expects an EmailAlreadyExistsError when a user with the same email already exists."""
    ...

# trivial — no comment needed
@property
def email(self) -> str:
    return self._email
```

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
