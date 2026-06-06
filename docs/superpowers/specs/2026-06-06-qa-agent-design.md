# QA Agent Design

**Date:** 2026-06-06  
**Status:** Approved — ready for implementation planning  
**Topic:** Structured QA oversight agent for klartext development workflow

---

## Problem Statement

Implementation agents consistently miss tests in four recurring ways:

1. Incomplete test coverage — not all layers (Domain/Service/Repository/Router) covered
2. Missing edge and error cases — only happy paths tested
3. Infrastructure tests forgotten — /health endpoints, @pytest.mark.integration markers
4. Fake contract gaps — silent constants that hide missing behavior

Additionally, complex domain object networks (Wirkgefüge, Scope, CausalModel composition)
require composition tests that test emergent behavior — and these are the hardest for agents
to recognize as missing.

The existing `tdd` skill describes how to write tests, but no mechanism verifies whether
an agent actually did it. The TDD skill's checklist is self-administered by the same agent
that produced the gaps.

---

## Architecture Overview

```
Implementation Agent
    │
    ├─ invokes tdd skill (as today)
    │       │
    │       └─ MANDATORY final step → invokes qa-review skill
    │
qa-review Skill
    │
    ├─ dispatches fresh QA Sub-Agent (no implementation context)
    │       │
    │       ├─ reads git diff
    │       ├─ checks 5 categories (see below)
    │       ├─ writes missing RED tests
    │       └─ delivers structured report
    │
    └─ blocks until sub-agent complete
           → implementation agent makes RED tests green

CI (qa.yml — new GitHub Actions workflow)
    │
    ├─ Semgrep: router without /health test
    ├─ Semgrep: fake class with silent constants
    ├─ Semgrep: SupabaseRepository method without @integration marker
    └─ scripts/check_test_coverage.py: every source file has a test file
```

**Core principle:** LLM analysis (semantic, writes tests) runs locally only. CI checks only
what is deterministically verifiable — no LLM in CI, no API costs in CI.

---

## Local QA: The qa-review Skill

### Skill location

```
~/.claude/skills/qa-review/
    SKILL.md                        ← main skill (trigger description + sub-agent dispatch)
    qa-categories.md                ← the 5 check categories in detail
    domain-composition-rules.md     ← Wirkgefüge/Scope composition-specific rules
    report-format.md                ← output format specification
```

### Trigger

The skill's description: *"Use after every implementation session, before marking work
complete. Dispatches a QA sub-agent that checks test coverage, edge cases, infrastructure
tests, fake contract completeness, and domain composition tests."*

### Sub-agent behavior

The sub-agent receives only `git diff HEAD` (or `--staged`) as input — no session context.
This is intentional: fresh perspective without the implementation agent's blind spots.

It works through five categories sequentially, then produces a structured report.

---

## The Five Check Categories

### 1 — Test Completeness

For every new class/method in `models/`, `services/`, `repositories/`, `routers/`:
- Does a corresponding test file exist?
- Does every public method have at least one test?
- Are all four layers present (Domain → Service → Repository → Router)?

### 2 — Edge and Error Cases

Checks for typical missing coverage:
- `XNotFoundError` raised and tested?
- Invalid input → 422/400 tested at the router?
- Empty lists, None values, empty strings as input?
- Error paths (exceptions thrown) tested alongside happy path?

### 3 — Infrastructure Tests

- Does every new/modified router have a `/health` test?
- Does every new `SupabaseXRepository` method have a `@pytest.mark.integration` test?
- Are JOIN queries and PostgREST embedded counts covered by integration tests?

### 4 — Fake Contract Completeness

- Does every fake class implement the full interface?
- Are there `NotImplementedError` methods that are never called (silent gaps)?
- Silent constants (`count=0`, `return []`) that mask missing behavior?
- For computed fields (e.g. counts): is there a test helper like `set_claim_count()`?

### 5 — Domain Composition Tests *(applies when Wirkgefüge objects are in the diff)*

Triggered when `models/causal_model*.py`, `models/slot*.py`, `models/relation*.py`,
or `models/scope*.py` appear in the diff. Also triggered when `CausalModel` methods
are changed, not only when Slot/Relation are changed.

Checks:
- Are there tests that assemble multiple domain objects and verify their interaction?
- Is scope behavior tested under different object combinations?
- Are composition edge cases covered: empty model, circular references, scope boundaries,
  components that appear in multiple containers simultaneously?

---

## Sub-Agent Output Format

```
## QA Review Report

### ✅ Complete
- Domain tests: UserDomain — all 3 methods covered

### ⚠️ Gaps found — RED tests written

**test_user_service.py** — missing error cases:
→ test_get_by_id_raises_for_inactive_user [WRITTEN]
→ test_change_email_raises_for_duplicate [WRITTEN]

**test_users_router.py** — missing infrastructure test:
→ test_users_health_returns_200 [WRITTEN]

### ❌ Requires manual decision
- Integration test for find_by_email missing — Supabase query worth checking
  Reason: contains PostgREST filter, fake does not cover this
```

**RED tests are complete, runnable tests** — correct structure, correct method names,
correct `pytest.raises(...)`. They fail intentionally because the implementation is
missing or incomplete. The implementation agent makes them green before declaring done.

---

## TDD Skill Extension

The existing `~/.claude/skills/tdd/SKILL.md` receives a new final section:

```markdown
## Step 3: QA Review

Before marking work complete, invoke the `qa-review` skill.

The QA agent reviews the diff with fresh eyes:
- Test completeness (all layers)
- Edge and error cases
- Infrastructure tests (/health, @integration)
- Fake contract completeness
- Domain composition tests (for Wirkgefüge changes)

If it finds gaps, it writes RED tests. These tests must be green
before the work is considered done.
```

---

## CI: qa.yml

New GitHub Actions workflow, runs on every push and pull request.

### New Semgrep rules (to be written)

| Rule ID | What it checks |
|---|---|
| `klartext/router-health-test` | Every router in `routers/` has a `test_*_health*` test |
| `klartext/fake-not-implemented` | Fake classes must not use silent placeholders (`return 0`, `return []`) |
| `klartext/supabase-needs-integration` | Every `SupabaseX*` method has a `@pytest.mark.integration` test |

### Structural test coverage check

A small Python script (`scripts/check_test_coverage.py`, ~40 lines) that checks:
for every file in `models/`, `services/`, `repositories/`, `routers/` — does
`tests/test_<name>.py` exist? If not → exit code 1.

This is the deterministic safety line: no new source file ships without a test file.

### Full CI pipeline after this change

```
qa.yml (new)          Semgrep QA rules + check_test_coverage.py
test.yml              pytest -m "not integration"
integration.yml       pytest -m "integration and not claude"
lint.yml              ruff + mypy + tach + existing Semgrep rules
setup-smoke-test.yml  fresh environment bootstrap
```

---

## Feedback Loop: QA Retrospective

### The problem

When a bug reaches manual testing despite all checks passing, the QA agent has a
systematic blind spot. This must be made visible and fed back into the system.

### Two automatic entry points — no manual trigger needed

**Entry point 1 — systematic-debugging skill (already exists)**

The final step of the debugging skill is "root cause found, write test." A qa-retro
step is appended there: *"If this bug should have been caught by the QA agent,
write a qa-learnings entry."* The retrospective happens automatically at the end of
every structured debugging session.

**Entry point 2 — tdd skill, bug-fix path**

The TDD skill already says: *"Never fix a bug without a test."* A qa-retro step
is added: *"Write a qa-learnings entry if this bug should have been caught by
the QA agent."*

**Exception:** If a bug is discovered outside a structured session (observed in
production, reported by a user), `/qa-retro` can be invoked manually. This is
the rare case, not the default.

### The /qa-retro skill

Guides through a structured retrospective:

1. What happened? — brief description of the failure
2. Which test should have caught this? — sub-agent writes it now (RED)
3. Why did the QA agent not write it? — unknown category / known blind spot /
   failure within a known category?
4. What changes? — concrete consequence (sharper rule, new check category,
   new Semgrep rule)
5. Documentation → writes entry to `docs/superpowers/qa-learnings/YYYY-MM-DD-<what-broke>.md`

### Learning entry format

```markdown
# QA Gap: 2026-06-07 — Scope behavior with empty CausalModel

## What happened
CausalModelScope.resolve() returned None instead of []
when the model was empty — frontend crashed.

## Missing test
test_scope_resolve_returns_empty_list_for_empty_model()
→ Category: Domain Composition Tests

## Why did qa-review miss this?
The QA agent only checks composition tests when Slot/Relation
appear in the diff — not when CausalModel methods alone change.

## Consequence
→ domain-composition-rules.md: also trigger composition tests
  when CausalModel methods change, not only Slot/Relation
→ Semgrep not possible (semantic pattern)
```

### Pattern recognition

The `qa-learnings/` entries are not just archive. When starting a new session,
checking `qa-learnings/` is the first step when a test problem is reported.

After 3+ entries in the same category:
- Sharper rule in `qa-categories.md` or `domain-composition-rules.md`
- New Semgrep rule if the pattern is statically checkable
- ADR if it represents a fundamental architectural decision

### Full feedback loop

```
Bug in production / manual testing
      │
      ▼
/qa-retro (via systematic-debugging or tdd bug-fix — automatic)
      │
      ├─ writes missing test (RED)
      ├─ identifies blind spot category
      └─ docs/superpowers/qa-learnings/*.md
                │
                ▼ (on pattern: 3+ same category)
         qa-categories.md updated
         or new Semgrep rule
         or ADR
                │
                ▼
         QA agent learns on next invocation
         (reads qa-categories.md as part of its context)
```

---

## Defense Layers Summary

```
During development (local)
  └─ tdd skill → qa-review skill → QA sub-agent writes RED tests

Pre-Commit
  └─ Semgrep (existing + new QA rules)

CI Push/PR
  └─ qa.yml: Semgrep QA rules + check_test_coverage.py

CI (existing)
  └─ test.yml, integration.yml, lint.yml

When bugs slip through
  └─ systematic-debugging / tdd bug-fix → /qa-retro → qa-learnings/
  └─ learnings feed back into qa-categories.md and Semgrep rules
```

---

## Files to Create / Modify

### New files
- `~/.claude/skills/qa-review/SKILL.md`
- `~/.claude/skills/qa-review/qa-categories.md`
- `~/.claude/skills/qa-review/domain-composition-rules.md`
- `~/.claude/skills/qa-review/report-format.md`
- `~/.claude/skills/qa-retro/SKILL.md`
- `.github/workflows/qa.yml`
- `scripts/check_test_coverage.py`
- `.semgrep/rules/klartext-router-health-test.yaml`
- `.semgrep/rules/klartext-fake-not-implemented.yaml`
- `.semgrep/rules/klartext-supabase-needs-integration.yaml`
- `docs/superpowers/qa-learnings/` *(folder, starts empty)*

### Modified files
- `~/.claude/skills/tdd/SKILL.md` — add Step 3 (qa-review call)
- `~/.claude/skills/systematic-debugging/SKILL.md` — new wrapper skill (same pattern
  as tdd wraps superpowers:test-driven-development): loads superpowers:systematic-debugging,
  adds qa-retro step at end. The superpowers plugin skill cannot be edited directly.

---

## Out of Scope

- Frontend test coverage (tracked separately in PENDING.md)
- E2E / Playwright tests (tracked in PENDING.md — after workflow is stable)
- LLM-based checks in CI (too expensive, non-deterministic)
- Automatic `/qa-retro` trigger via hook (friction outweighs benefit for rare case)
