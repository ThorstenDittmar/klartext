# Classification Gate (`rolling` | `breaking`) — Design

**Date:** 2026-06-15
**Author:** DevOps
**Status:** Approved (design); implementation pending
**Related:** ADR-0012 (worktree convergence / two-mode consistency for breaking method changes)

## Purpose

When a pull request touches a **Way-of-Working (WoW) surface** — method docs, agent
Hoheitswissen, or infrastructure config — it must carry exactly one classification
label, `rolling` or `breaking`, that answers ADR-0012's two-mode-consistency question
**explicitly**:

- **`rolling`** — additive / backward-compatible change. Worktrees can adopt it lazily
  via `klartext converge`; no coordinated cutover needed.
- **`breaking`** — changes the meaning of an existing rule, hook, path, or contract.
  Requires coordinated rollout (all worktrees must converge before the change is relied
  upon).

CI **fails** when a trigger-path PR carries neither label (or both). The gate is
**default-free**: it never guesses the classification. Authors resolve uncertainty
toward `breaking` (documented in the PR template).

Most PRs touch no WoW surface and are unaffected — the gate adds zero friction to
ordinary code/test PRs.

## Scope decision

The trigger-path list is **OE's literal list** plus `agents/**/claude.md` (Hoheitswissen
is WoW). The broader method docs under `docs/superpowers/improvement/**` are
**deliberately excluded for now** (user decision 2026-06-15). A note has been sent to OE
to re-evaluate broadening the scope after a few weeks of practice; the path list lives in
one place (`scripts/classify_gate.py`), so broadening is a one-line + one-test change.

## Trigger-path list

A PR is **in scope** for the gate if any changed file matches:

```
CLAUDE.md
docs/superpowers/skills/**
agents/**/claude.md
.claude/settings.json
scripts/**
api/cli.py
```

Rationale per entry:
- `CLAUDE.md` — the coding standards / shared method baseline.
- `docs/superpowers/skills/**` — the team's ritual skills (the executable how-tos).
- `agents/**/claude.md` — agent Hoheitswissen IS the way of working (OE).
- `.claude/settings.json` — baseline permissions and hooks for all agents.
- `scripts/**` — hook scripts and tooling (session_health, converge, inbox, …).
- `api/cli.py` — the `klartext` CLI (infrastructure entry point).

## Components

### 1. Repo labels

Two labels created idempotently (`gh label create … || true`), documented in the
developer guide:

- `rolling` — additive / backward-compatible WoW change.
- `breaking` — meaning-changing WoW change; needs coordinated rollout.

### 2. `scripts/classify_gate.py` — the testable core

The classification logic lives in a small Python module, **not** inline YAML, following
the existing `scripts/` + `api/tests/infrastructure/` pattern (`converge`,
`session_health`). This makes the path-matching and label logic unit-testable.

Public function (signature illustrative; finalized in the plan):

```python
def evaluate(changed_paths: list[str], labels: set[str]) -> GateResult:
    """Decide whether the classification gate passes for a PR.

    - No changed path matches a trigger pattern  -> PASS (gate not applicable).
    - A trigger path is touched and exactly one of {rolling, breaking} is present -> PASS.
    - A trigger path is touched and neither / both labels present -> FAIL.
    Never infers the label.
    """
```

- Path matching uses the trigger-path list above (glob semantics, defined as a module
  constant `TRIGGER_PATTERNS`).
- Returns a result object carrying `passed: bool` and a human-readable `message`.
- A thin `main()` reads changed paths and labels from argv / stdin / env (exact wiring
  decided in the plan), prints the message, and exits 0/1.

### 3. `.github/workflows/classify-gate.yml`

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

- **`labeled` / `unlabeled` types**: adding the label re-runs the check and turns it
  green **without a new commit**.
- **No workflow-level `paths:` filter** — the job always runs and always reports a
  status. This avoids the "required check that gets skipped blocks the merge forever"
  GitHub footgun. Applicability is decided inside `classify_gate.py`, not by the trigger.
- **`pull_request` only** (no `push`) — no double-trigger; the gate is inherently a
  PR concern.

The single job: checkout, collect changed files (`git diff --name-only
origin/${{ github.base_ref }}...HEAD`) and the PR's labels (from the event payload),
run `python3 scripts/classify_gate.py`, and let its exit code pass/fail the check.

### 4. `.github/pull_request_template.md`

A new template with a **Classification** section:

- Explains `rolling` vs `breaking`.
- Instructs: if this PR touches a WoW surface (method docs, Hoheitswissen, infra config),
  add the matching label.
- States the default-free rule: **uncertainty → `breaking`**.
- Links ADR-0012.

## Data flow

```
PR opened/updated/(un)labeled
        │
        ▼
classify-gate.yml  ──(always runs)──►  job
        │
        ├─ changed paths  = git diff --name-only base...HEAD
        ├─ labels         = github.event.pull_request.labels
        ▼
scripts/classify_gate.py :: evaluate(changed_paths, labels)
        │
        ├─ no trigger path touched              → exit 0 (PASS, not applicable)
        ├─ trigger path + exactly one label     → exit 0 (PASS)
        └─ trigger path + zero / both labels    → exit 1 (FAIL, clear message)
```

## Error handling

- The script fails **loud and clear**: the failure message names which trigger paths were
  touched and that exactly one of `rolling` / `breaking` is required. No silent pass.
- If the diff or label collection itself errors (infrastructure failure), the job fails
  (visible), it does not swallow the error — consistent with the project's
  "kein Fehler verschwindet still" rule.

## Testing (TDD)

`api/tests/infrastructure/test_classify_gate.py`:

| Case | Expectation |
|---|---|
| non-trigger paths only, no label | PASS (not applicable) |
| `CLAUDE.md` changed + `rolling` | PASS |
| `CLAUDE.md` changed + `breaking` | PASS |
| trigger path changed + no label | FAIL |
| trigger path changed + both labels | FAIL |
| each trigger pattern matches a representative path | matched |
| near-miss `docs/adr/0012-...md` | NOT a trigger |
| near-miss `docs/superpowers/improvement/practices/x.md` | NOT a trigger (scope decision) |

`qa-review` is run before completion (DevOps DoD: QA frees infrastructure tests via the
four-eyes principle).

## Out of scope (flagged, not done here)

- **Branch-protection "required" toggle.** The gate only *binds* once it is marked a
  required status check in branch protection — a repo-admin setting. Flagged to the
  user / OE; not silently changed.
- **Broadening the trigger paths** beyond OE's list. Two candidates noticed during design,
  both deferred to the post-practice review (note sent to OE 2026-06-15):
  - `docs/superpowers/improvement/**` — the method docs proper (practices, kernel).
  - `.github/workflows/**` — CI changes can themselves be breaking (e.g. removing a
    required check). Not in OE's list; left out for now to match the approved scope.

## Definition of Done

- [ ] `scripts/classify_gate.py` with `TRIGGER_PATTERNS` + `evaluate()`.
- [ ] `.github/workflows/classify-gate.yml` (pull_request, labeled/unlabeled, no path filter).
- [ ] `.github/pull_request_template.md` with the Classification section.
- [ ] `rolling` / `breaking` labels created + documented in `developer-guide.md`.
- [ ] `api/tests/infrastructure/test_classify_gate.py` covers the matrix above.
- [ ] `qa-review` passed.
- [ ] The gate's own PR is labelled `rolling` (it touches `scripts/**` and `.github/`).
