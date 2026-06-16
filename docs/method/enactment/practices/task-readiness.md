# Task Readiness — klartext enactment

> **Scope.** klartext's enactment of the **Task Readiness** practice: the concrete checklist bindings (the
> fake-contract check, Hannibal as dispatcher, the `qa-review`/`tdd` handoff, SA-escalation), the branch
> scheme, and our evidence.
> **Out of scope.** The generic gate (the four checks + go-step) — see the L3 card. The QA practices it hands
> off to (`qa-review`, `tdd`); coordination/roles (`CLAUDE.md`).
> **Anti-pattern guarded.** Starting a dispatched task on incomplete info / a stale fake contract / an
> unflagged boundary crossing, then unwinding it (RC2 / T6 — the advisory-gate hole, T-cluster).
> **Language.** English — documentation-language rule (the skill body is German).
>
> **L3 definition:** [`../../library/practices/task-readiness.md`](../../library/practices/task-readiness.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Work · **NN:** ✓ (before a dispatched task)

## klartext bindings

| Generic check | klartext binding |
|---|---|
| **Dispatcher** | **Hannibal** dispatches tasks from the implementation plan; clarifications and overlap reports go to Hannibal. |
| **Checkable DoD** | "Tests green" is not a DoD — `klartext test` runs green is. The DoD must be a runnable `klartext …` command. |
| **Dependency contract** | The **fake-contract** for the task's dependencies must be current: if this task changes a repository interface, send a **QA briefing before starting** and wait until the fake is up to date (fakes must implement the full interface — no silent-constant masking). |
| **Test layers** | QA fixes the expected layers (Domain / Service / Repository / Router) for new source files in the coordination round; confirm them here. |
| **Escalation** | A new layer crossing or cross-domain interface escalates to **System Architect via Hannibal** — never decided solo (the model-boundary rule). |
| **Go-step** | tests first via the `tdd` skill → branch `task/<H-id>/<slug>` → implement → PR (no direct push to `main`) → `git rebase main` on others' merges → report to Hannibal. |
| **Roundup** | When the PR is merged, inform Hannibal; "done" is when **QA gives the green light** (Hannibal coordinates the `qa-review` gate). |

## Enforcement (klartext)

A **ritual** (Enforcement Hierarchy level 2). **The open enforcement hole:** `task-readiness` is currently
**advisory** — the last H01-grade gate not yet mechanically enforced (T6 / RC2; see `../method.md` Known
gaps). Promotion target: a dispatch-time check that the gate ran.

## Evidence / learnings

- **H01-422: invoked 3/3 dispatches** (drained to `main` in PR #52) — validated that the gate is actually run
  when dispatched, even while still advisory.
