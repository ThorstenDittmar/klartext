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

**Way of Working** — advances it toward its *next* state, whichever currently applies; the steady-state
target is *In Use* → *Working Well*. Early runs legitimately operate further back in the lifecycle (e.g.
inspecting *Foundation Established* checkboxes) — running retrospectives is itself part of reaching
*In Use*, whose checklist includes "regularly inspected". Defines and tracks the **Improvement sub-alpha**
(adopted from IJI):

> **Improvement** — a possible adaptation to improve the team's Way of Working.
> States: *Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use.*

An improvement that never reaches *Results Evaluated* stays visibly stuck — the register makes the
RC2 failure mode ("decided, never verified") detectable.

## Trigger

**Event-based, never wall-clock:** end of a sprint / work package (the Work alpha's *Closed* state requires
"Lessons learned"), a defined milestone, or on demand after a significant incident.

**Who triggers vs. who hosts (clarified 2026-06-10):** the work-package owner (Hannibal — *Coordinate
Activity*) **triggers** the retro by wanting to close the Work alpha — he cannot reach *Closed* without it.
The **Method Keeper (OE) hosts**: invites the participants and leads the run. The coordinator must not
host — the retro evaluates (among other things) how well his coordination worked; self-evaluation without
a counterpart would break the four-eyes pattern. Precedent: `qa-retro` is led by its practice owner (QA).

## Entry Criteria

- A **named, event-based trigger** — recorded in the retro output (an unnamed trigger violates this card).
- The **Improvement Register** exists and reflects the current state.
- The **alpha state checklists** (`alpha-states.md`) are available for the alpha-walk.
- A **leader with the required competency** is present (see Competencies).

## Competencies

- **Leader** — Method Literacy ≥ 2 (*Applies*): runs the alpha-walk, RC mapping and register maintenance
  unaided. The lead attaches to the existing **Method Keeper** pattern (OE) — no separate role is imported
  (checked against the standard 2026-06-10: the existing pattern covers the function).
- **Participants** — Method Literacy ≥ 1 (*Assists*): follow the vocabulary, contribute evidence.
- *"Whole team inspects and adapts"* is an **In Place** checkbox of the Way-of-Working alpha — full active
  whole-team participation is the *target state*, not an entry requirement for early runs. Team-wide
  literacy ≥ 2 is batched at the *Foundation Established* milestone (team refresh).

## Participants

**Default reach: the whole team — always.** Limiting a retro to those who worked on the inspected work
package would blind it to a failure mode it must detect: *someone should have been involved and was not*
(RC3; precedent: the Community-Expert omission — the missing expert never got the chance to raise a hand).
To keep cost sane, participation has two tiers:

- **Active input — mandatory** from everyone who worked on the inspected work package (via the user as
  channel): their experience is evidence that exists in no artifact.
- **Record review — everyone else:** the retro record is routed to all agents (team roster) with two
  explicit questions: *Should you have been involved in this work package?* and *Does any finding touch
  your domain?* Responses — or silence — are noted in the record.

**Involvement check (explicit step):** every retro asks *"who was not involved that should have been?"* —
the answer is RC3 evidence, even when it is "nobody".

### How input is gathered (enactment)

The two tiers need different mechanisms, because they need different knowledge:

- **Record review** asks about *domain match* ("does a finding touch your domain? should you have been
  involved?") — answerable from **disk** (`agents/<name>/claude.md`, roster). → A **forked subagent** per
  agent is sufficient; cheap broadcast, no live sessions needed.
- **Active input** asks about *experience* — knowledge that may exist only in the participant's long-living
  session. Two variants:
  - **(a) Artifact-mediated (preferred, cheap):** a forked subagent represents the participant, reading
    their knowledge file + the work products. **Valid only if** that agent's session knowledge was captured
    to disk (anchor-style capture with a held completion checklist) **at or after work-package end**.
    Without that, the subagent is a simulation that misses exactly the evidence the retro exists to collect
    (precedent: the "simulated Hannibal", deliberately discarded).
  - **(b) Live session (fallback, expensive):** query the agent's long-living session via the user as
    channel. **Required** whenever (a)'s precondition is not confirmed — when in doubt, (b).
- **Entry criterion (per work-package participant):** capture confirmed → (a); otherwise → (b).

*Current state (2026-06-10; skill renamed to `anchor` 2026-06-13):* the capture practice (`anchor`, formerly
`pre-compact`) is German-only; a versioned repo copy was added 2026-06-13 (`docs/superpowers/skills/anchor.md`,
machine-local install pending DevOps), and it is validated only on OE sessions → (a) is **not yet trustworthy** for other agents;
active input therefore uses (b) until the capture practice is promoted (see the Improvement Register —
that improvement is the enabler of cheap retros).

*Activation note:* the record-review tier becomes meaningful only after the team refresh (team-wide Method
Literacy ≥ 1); until then OE + user run the involvement check manually against the roster.

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
5. **Element sweep** *(added 2026-06-10, user-prompted)* — walk the run's artifacts, activities, patterns
   and competencies: which elements did this run **use or produce**? Each one: registered in `method.md`?
   If not → register it (or record it as an Improvement candidate) **in this retro**. This reconciles the
   *described* method against the *enacted* one — RC4 medicine applied to the method itself; the
   maintenance ritual alone only catches deliberate changes, not elements that creep in through use.
6. **Identify & prioritize improvements** — new Improvement instances enter the register
   (*Identified* / *Prioritized*).
7. **Agree actions** — per improvement: **owner + checkable DoD + enforcement level**
   (mechanical / ritual — never advisory-only). State → *Action Agreed*.
8. **Capture & route** — learnings to `learnings/` (one file per learning), register updated, affected
   practice cards / `method.md` updated **in the same step**; briefings routed via `knowledge-routing`
   where other agents are affected.

## Work Products

- **Improvement Register** — `continuous-improvement.md` §3 (Improvement instances with alpha state).
- **Learning entries** — `docs/method/enactment/learnings/` (one file per learning).
- Updates to practice cards / `method.md`.

## Completion Checklist (Done)

- [ ] The trigger event is named in the retro record (entry criterion held).
- [ ] The involvement check was run ("who was missing?") and its answer recorded; the record was routed
      to the whole team (or the manual roster check was done — see activation note).
- [ ] Every previously *Trialed* improvement was evaluated — advanced or retired.
- [ ] Evidence basis was concrete (incidents / signals), not impressions.
- [ ] The Way-of-Working checklist was walked; regressions named.
- [ ] The element sweep ran — every element the run used/produced is registered in `method.md` or recorded
      as an Improvement candidate.
- [ ] **Deviation clause:** if any mandatory input was missing or an enactment rule was bent, the deviation
      is named and justified in the record, and missing input is carried as a *verified addendum* —
      otherwise this retro is not Done.
- [ ] Each new improvement has owner + checkable DoD + enforcement level.
- [ ] Learnings captured at their home; register updated.
- [ ] Briefings routed where other agents are affected.

## Enforcement

Currently a **ritual** (level 2). Skill promotion after the first real runs. Relation: `qa-retro` is the
**incident-triggered sibling** for test gaps — both feed Improvement instances into the same register.
