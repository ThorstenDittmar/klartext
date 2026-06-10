# Practice: Retrospective

> **Scope.** This document defines the **Retrospective** practice — the periodic, evidence-based
> way-of-working retro, including the **Improvement** sub-alpha it tracks.
> **Out of scope.** The incident-triggered test-gap retro (`qa-retro` skill — the sibling practice); decisions
> and rationale (`continuous-improvement.md`); the Improvement Register itself (lives in
> `continuous-improvement.md` §3).
> **Anti-pattern guarded.** Decided-but-never-verified measures (RC2 — the "check effectiveness" gap);
> impressions instead of evidence as retro input.
> **Language.** English — documentation-language rule.
>
> **Status:** active (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working
> **Source:** composed from IJI *Agile Retrospective Essentials* (card content CC BY 4.0; deck in
> `assets-local/`) + the Essence Alpha State Cards (alpha-walk as inspection grid) + our RCA discipline.
> **Deliberately not adopted:** *Mad/Sad/Glad* — emotion-based and human-specific; our data basis is
> concrete incidents, not impressions (§3 rule).

## Goal

Make incremental improvements to the way of working through regular, evidence-based retrospectives —
where **no improvement counts as done until its results are evaluated**.

## Advances Alpha

**Way of Working** (*In Use* → *Working Well*). Defines and tracks the **Improvement sub-alpha**
(adopted from IJI):

> **Improvement** — a possible adaptation to improve the team's Way of Working.
> States: *Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use.*

An improvement that never reaches *Results Evaluated* stays visibly stuck — the register makes the
RC2 failure mode ("decided, never verified") detectable.

## Trigger

**Event-based, never wall-clock:** end of a sprint / work package (the Work alpha's *Closed* state requires
"Lessons learned"), a defined milestone, or on demand after a significant incident.

## Steps

1. **Evaluate previous actions** — walk the Improvement Register first: did each *Trialed* improvement
   produce results? Advance its state (*Results Evaluated* / *In Use*) or retire it. Nothing stays silently
   on *Action Agreed*.
2. **Collect evidence** — concrete incidents, CI status, compact-monitor digest, `PENDING.md` state.
   No impressions without an incident behind them.
3. **Alpha-walk** — inspect the relevant Alpha state checklists (`alpha-states.md`), at minimum
   **Way of Working**: which checkbox regressed? Which one blocks the next state?
4. **Root-cause mapping** — map findings to RC1–RC6 (`continuous-improvement.md` Phase 1). If none fits,
   that is a candidate **new** root cause — record it explicitly.
5. **Identify & prioritize improvements** — new Improvement instances enter the register
   (*Identified* / *Prioritized*).
6. **Agree actions** — per improvement: **owner + checkable DoD + enforcement level**
   (mechanical / ritual — never advisory-only). State → *Action Agreed*.
7. **Capture & route** — learnings to `learnings/` (one file per learning), register updated, affected
   practice cards / `method.md` updated **in the same step**; briefings routed via `knowledge-routing`
   where other agents are affected.

## Work Products

- **Improvement Register** — `continuous-improvement.md` §3 (Improvement instances with alpha state).
- **Learning entries** — `docs/superpowers/improvement/learnings/` (one file per learning).
- Updates to practice cards / `method.md`.

## Completion Checklist (Done)

- [ ] Every previously *Trialed* improvement was evaluated — advanced or retired.
- [ ] Evidence basis was concrete (incidents / signals), not impressions.
- [ ] The Way-of-Working checklist was walked; regressions named.
- [ ] Each new improvement has owner + checkable DoD + enforcement level.
- [ ] Learnings captured at their home; register updated.
- [ ] Briefings routed where other agents are affected.

## Enforcement

Currently a **ritual** (level 2). Skill promotion after the first real runs. Relation: `qa-retro` is the
**incident-triggered sibling** for test gaps — both feed Improvement instances into the same register.
