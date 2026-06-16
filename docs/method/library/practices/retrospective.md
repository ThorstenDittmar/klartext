# Retrospective

> **Essence type:** Practice
> **Advances Alpha:** Way of Working (defines and tracks the **Improvement** sub-alpha)  ·  **Work Products:** the Improvement Register (Improvement instances with state); learning entries (one per learning); updates to affected practice cards / the method register
> **Activity / Activity Space:** Stop the Work → periodic, evidence-based inspect-and-adapt of the method
> **External dependencies (referenced Resources):** IJI *Agile Retrospective Essentials* (card content, CC BY 4.0 — the practice is composed from it, not vendored); Essence Kernel/Language (the Alpha State Cards used as the inspection grid)
> **Enforcement:** ritual  ·  **NN:** ✓ (Work cannot reach *Closed* without it)
> **Status:** living  ·  **Owner:** OE (Method Keeper hosts)
> **Enacted as:** — (ritual; the incident-triggered sibling for test gaps is a separate skill, see Related)

## Purpose

Make incremental improvements to the way of working through regular, **evidence-based** retrospectives —
where **no improvement counts as done until its results are evaluated**. Guards two failure modes:
decided-but-never-verified measures (the "check effectiveness" gap), and impressions instead of evidence as
retro input.

## Definition / delta

This practice is **composed** from the IJI *Agile Retrospective Essentials* deck (the referenced Resource) +
the Essence Alpha State Cards (used as an inspection grid) + a root-cause discipline. It is **not** restated
here — the Resource is referenced; only the composition delta is described. *Deliberately not adopted:*
*Mad/Sad/Glad* — emotion-based and human-specific; the data basis is concrete incidents, not impressions.

**The Improvement sub-alpha** (adopted from IJI) — a possible adaptation to improve the team's Way of
Working. States: *Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use.* An
improvement that never reaches *Results Evaluated* stays visibly stuck — the register makes the
"decided, never verified" failure mode detectable.

**Trigger.** Event-based, never wall-clock: end of a sprint / work package (the Work alpha's *Closed* state
requires "Lessons learned"), a defined milestone, or on demand after a significant incident.

**Who triggers vs. who hosts.** The work-package coordinator **triggers** the retro by wanting to close the
Work alpha — they cannot reach *Closed* without it. The **Method Keeper hosts** (invites participants, leads
the run). The coordinator must not host — the retro evaluates how well their coordination worked;
self-evaluation without a counterpart would break the four-eyes pattern.

**Entry criteria.** A named, event-based trigger (recorded) · the Improvement Register exists and is current
· the Alpha state checklists are available for the alpha-walk · a leader with the required competency.

**Participants — whole team by default.** Limiting a retro to those who worked on the inspected package would
blind it to a failure mode it must detect: *someone should have been involved and was not*. Two tiers:
- **Active input — mandatory** from everyone who worked on the package (their experience is evidence that
  exists in no artifact).
- **Record review — everyone else:** the record is routed to all members with two questions: *Should you have
  been involved?* and *Does any finding touch your domain?* Responses — or silence — are noted.
- **Involvement check (explicit step):** every retro asks *"who was not involved that should have been?"* —
  the answer is evidence even when it is "nobody".

**Steps.** 1) **Evaluate previous actions** (walk the register; advance or retire each *Trialed* improvement
— nothing stays silently on *Action Agreed*). 2) **Collect evidence** (concrete incidents/signals, not
impressions). 3) **Alpha-walk** (inspect the relevant Alpha checklists, at minimum Way of Working: which
checkbox regressed? which blocks the next state?). 4) **Root-cause mapping** (map findings to the team's root
causes; if none fits, record a candidate new root cause). 5) **Element sweep** (walk the run's
artifacts/activities/patterns/competencies: which did this run use or produce? each one registered? if not →
register or record as an Improvement candidate — reconciling the *described* method against the *enacted*
one). 6) **Identify & prioritize improvements.** 7) **Agree actions** (per improvement: owner + checkable DoD
+ enforcement level — never advisory-only). 8) **Capture & route** (learnings to their home, register
updated, affected cards updated in the same step, briefings routed).

**Completion (Done):** trigger named in the record · involvement check run and recorded; record routed to the
whole team · every previously *Trialed* improvement evaluated · evidence basis concrete · Way-of-Working
checklist walked, regressions named · element sweep ran · **deviation clause** (any missing mandatory input
or bent rule is named and justified, missing input carried as a verified addendum — otherwise not Done) ·
each new improvement has owner + DoD + enforcement level · learnings captured, register updated · briefings
routed where others are affected.

**Enforcement note (generic).** Ritual. The retro practice has an **incident-triggered sibling** for test
gaps — both feed Improvement instances into the same register.

## Related

- klartext enactment: [`../../enactment/practices/retrospective.md`](../../enactment/practices/retrospective.md)
- The incident-triggered test-gap sibling (the `qa-retro` skill).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
