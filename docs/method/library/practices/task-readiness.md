# Task Readiness

> **Essence type:** Practice
> **Advances Alpha:** Work  ·  **Work Products:** a recorded readiness verdict (proceed / clarify / escalate) · clarification requests to the dispatcher · escalations to the architecture authority where a boundary is crossed
> **Activity / Activity Space:** Prepare to do the Work → confirm a dispatched task is ready before any implementation begins
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (before starting a dispatched task)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** the `task-readiness` skill

## Purpose

Before a single line is written on a **dispatched** task, confirm every precondition is met — so a misread
scope, an unverifiable definition-of-done, a stale dependency contract, or an unflagged boundary crossing is
caught **up front** rather than after the work is built and has to be unwound. Five minutes of clarification
beats a rollback.

## Definition / delta

A readiness gate that runs **after a task is dispatched and before implementation**, in four checks then a
go-step:

1. **Information complete?** Is the scope clear (in *and* out)? Are all paths to touch named? Is there a
   concrete check-command as the definition-of-done? Are dependencies on other tasks settled? — *If not: ask
   the dispatcher before starting.*
2. **Quality checkpoint.** Are the DoDs **checkable** (a runnable command, not "tests are green")? Is the
   dependency/test-double contract for what this task depends on **current**? Which test layers does the
   quality owner expect for new source? — *If a contract is stale/unclear: brief the quality owner and wait.*
3. **Coordination need?** Do I need another member's input to start? Does my change affect another member
   (→ a briefing)? Does a path overlap a task running in parallel? — *If overlap: tell the dispatcher; do not
   just start.*
4. **Escalation need?** Does the task introduce a new layer crossing, cross a domain boundary, or create an
   interface to another domain? — *If yes: escalate to the architecture authority via the dispatcher — do not
   decide alone. No cross-domain interface without that authority's agreement.*

5. **Go.** All checks clear → tests first, branch, implement, open a change request (no direct push to the
   mainline), rebase on others' merges as they land, report completion to the dispatcher.

**Completion (Done):** all four checks answered against the actual task description and contracts · scope and
DoDs confirmed checkable · stale dependency contracts resolved before start (not during) · overlaps and
affected members surfaced to the dispatcher · boundary crossings escalated to the architecture authority
(never decided solo) · only then implementation begins.

**Enforcement note (generic).** A readiness ritual that gates a dispatched task. Its non-negotiable core is
the **escalation check** — a boundary crossing must reach the architecture authority before code exists. The
gate itself is human-judged; the downstream DoD command and the mainline-protection are mechanizable.

## Related

- klartext enactment: [`../../enactment/practices/task-readiness.md`](../../enactment/practices/task-readiness.md)
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
