---
name: qa-review
description: Use after every implementation session, before marking work complete. Dispatches a QA sub-agent that checks test coverage, edge cases, infrastructure tests, fake contract completeness, and domain composition tests. The tdd skill calls this automatically as Step 3.
---

# QA Review

After every implementation, dispatch a fresh QA sub-agent to review the diff with clean eyes.
The sub-agent has no context from the implementation session — this is intentional.

## When to Use

Mandatory after every implementation session:
- After completing a feature via the `tdd` skill (called automatically as Step 3)
- After any bug fix
- Before declaring work done and switching context

## Step 1: Collect the diff

```bash
git diff HEAD
```

If changes are staged but not committed yet:
```bash
git diff --staged
```

## Step 2: Read the support files

Read these files to understand your review criteria:
- `~/.claude/skills/qa-review/qa-categories.md` — the 5 check categories
- `~/.claude/skills/qa-review/domain-composition-rules.md` — applies when Wirkgefüge objects are in the diff
- `~/.claude/skills/qa-review/report-format.md` — required output format

## Step 3: Dispatch the QA sub-agent

Use the Agent tool to dispatch a fresh sub-agent with this prompt (fill in the diff):

---
You are a QA reviewer for the klartext project. Your only job is to find missing tests
in the diff below and write them.

You have no context about how this code was written. Review it fresh.

**Project:** FastAPI + Supabase, Python 3.12  
**Test layers:**
1. Domain — pure unit tests, no mocks, no external systems
2. Service — unit tests with FakeRepository (no Supabase)
3. Repository — `@pytest.mark.integration` against real database
4. Router — via `TestClient` or `AsyncClient`

**Your task:**
1. Read the diff
2. Check all 5 categories from the QA categories doc (provided below)
3. If Wirkgefüge objects are in the diff: apply domain composition rules (provided below)
4. Write missing tests as RED (failing) tests directly into the test files
5. Produce a report in the required format (provided below)

**Key rules:**
- Never mark a test as [WRITTEN] without actually writing the code
- Tests must fail when run — confirm RED before reporting
- If a test file does not exist yet, create it with correct imports
- Fake repositories: `FakeUserRepository` pattern, in `api/tests/fakes/`
- Router tests: use `AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`
- Integration tests: mark with `@pytest.mark.integration` and `@pytest.mark.asyncio`

[QA CATEGORIES]
<paste contents of qa-categories.md here>

[DOMAIN COMPOSITION RULES]
<paste contents of domain-composition-rules.md here — only if relevant>

[REPORT FORMAT]
<paste contents of report-format.md here>

[DIFF]
<paste git diff output here>
---

## Step 4: Act on the report

- If RED tests were written: run `pytest api/tests/ -m "not integration" -v` to confirm they fail
- Make all RED tests GREEN before declaring work done
- If [NEEDS MANUAL ACTION] items remain: resolve them or document why they are deferred

## What good looks like

Every implementation session ends with:
- All 5 categories checked
- No unresolved [NEEDS MANUAL ACTION] items (or documented reason for deferral)
- All tests GREEN

---

## Infrastructure Test Review

When DevOps requests a QA review of infrastructure tests (as required by the DevOps
Definition of Done), apply these checks against `api/tests/infrastructure/`:

### What to check

**1. Does a test exist for this change?**
Every infrastructure change that can break in production must have a test.
Examples:
- New migration → test that the schema shape is correct after `db reset`
- New FK relationship → test that PostgREST resolves the embedded count
- New dependency → health check covers it

**2. Does the test catch the actual failure mode?**
A test that passes even when the thing breaks is worse than no test.
Ask: *what exact error would occur in production if this breaks?*
The test must reproduce that error, not just test the happy path.

**3. Is the test marked correctly?**
Infrastructure tests that require a real database or external system:
`@pytest.mark.integration` + `@pytest.mark.asyncio`

**4. Is the failure message informative?**
`assert response.data is not None, "claims.narrative_id column does not exist"`
A bare `assert x` with no message makes debugging harder.

### What QA does NOT need to assess

- Whether the PostgREST query syntax is correct — that is DevOps domain knowledge
- Whether the migration SQL is valid — DevOps owns that
- Whether the CI pipeline config is correct — DevOps owns that

QA's role here: *Is there a test? Does it cover the failure mode? Is the assertion meaningful?*

### Shared ownership note

`api/tests/infrastructure/` is written by DevOps, reviewed and improvable by QA.
If QA identifies a gap, they may add assertions directly — no DevOps Briefing needed for test additions in this directory.

---

## QA Domain Boundaries

### What QA owns (write access)

- `api/tests/` — all test files, fakes, fixtures
- `api/tests/fakes/` — shared fake repository implementations
- `.semgrep/rules/qa/` — QA Semgrep rules (`qa-*.yaml`)
- `scripts/check_test_coverage.py` — structural coverage checker
- `docs/superpowers/qa-learnings/` — retrospective learning entries
- `~/.claude/skills/qa-*/` — QA skill files (this file and its siblings)

### What QA reads but does not change

All source files in `api/models/`, `api/services/`, `api/repositories/`, `api/routers/`,
`api/schemas/`, `api/exceptions/`, `api/providers/` — QA reads these to write tests.
Domain experts own them.

### Infrastructure changes → DevOps Briefing required

QA must **never** directly change files in the Infrastructure Perimeter:

    .github/workflows/      CI/CD Pipelines (including qa.yml)
    api/pyproject.toml      Python dependencies + tool config
    .pre-commit-config.yaml Git hooks
    tach.toml               Layer boundary enforcement
    setup.sh                Bootstrap script
    frontend/package.json   JS dependencies

If QA needs an infrastructure change (e.g. a new test dependency, a new CI step),
send a DevOps Briefing instead of making the change directly:

    DevOps Briefing
    Need:      [What is needed — concrete and actionable]
    Why:       [Technical or functional reason]
    Domain:    [Dependencies / CI/CD / Config / Other]
    Approach:  [Optional — what QA thinks might work]
    Impact:    [Which agents or environments are affected]

### Architectural Semgrep rules → brief System Architect

If a statically checkable pattern is an **architectural rule** (layer boundaries,
error handling, naming conventions), it belongs in `.semgrep/rules/arch/` and is
owned by System Architect + DevOps. QA does not write arch rules.

Heuristic:
- "This fake returns a silent constant" → QA rule → `.semgrep/rules/qa/`
- "This router has a try/except" → arch rule → brief System Architect
