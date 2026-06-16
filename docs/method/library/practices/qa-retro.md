# QA Retrospective

> **Essence type:** Practice
> **Advances Alpha:** Way of Working (the QA system learns from each caught gap — defines/tracks the **Improvement** sub-alpha) and Software System (the missing test is written, the defect can no longer recur silently)  ·  **Work Products:** the missing test (RED → GREEN); a learning entry (one per blind spot); an update to the QA check criteria (category / trigger / Semgrep rule); an Improvement instance when one emerges
> **Activity / Activity Space:** Stop the Work → incident-triggered inspect-and-adapt: a bug tests should have caught becomes a documented blind spot and a system fix
> **External dependencies (referenced Resources):** none — this is a klartext-own QA practice (not a superpowers wrapper)
> **Enforcement:** ritual (invoked when a bug is found that tests should have caught; the `systematic-debugging` and `tdd` bug-fix flows append it)  ·  **NN:** ✓ (when triggered)
> **Status:** living  ·  **Owner:** QA
> **Enacted as:** the `qa-retro` skill (`docs/method/enactment/skills/qa-retro/SKILL.md`)

> **Seeded by an OE-spawned sub-agent (F0.2-P-C, BARRIER mode); awaits ratification by real QA on wake (Guardrail 2).**

## Purpose

How klartext turns a **bug that the tests should have caught** into a permanent improvement of the QA system
rather than a one-off patch. A defect reaching manual testing or production despite all checks passing means
the QA agent has a **systematic blind spot**; this practice makes the blind spot visible and closes it. Guards
the failure mode where a bug is fixed and forgotten — the same class of bug then recurs because nothing in the
checking system changed.

## Definition / delta

This is a **self-owned** klartext QA practice — it references no upstream Resource. It is the
**incident-triggered sibling** of the periodic `retrospective` practice; both feed Improvement instances into
the **one** Improvement Register. The generic loop:

**Trigger.** Event-based: a bug fixed at the end of a `systematic-debugging` session; a `tdd` bug-fix where the
bug should have been caught earlier; or manual invocation when a user/production reports a defect.

**The run.**
1. **Describe what happened** — behaviour (not implementation), when discovered, which test category should
   have caught it.
2. **Write the missing test (RED)** — the test that *would* have caught the bug; confirm it fails for the
   right reason before proceeding.
3. **Fix the code (GREEN)** — the minimal change; the whole suite passes.
4. **Identify the blind spot** — *why* did the checking system not produce this test originally? One of:
   **unknown category** (the check set does not cover this kind of test), **known category / wrong trigger**
   (the category exists but its trigger missed this case), or **known category / agent failure** (the trigger
   was right, the reviewer missed it).
5. **Update the checking system** by blind-spot type — add a category, fix a trigger condition, sharpen the
   rule wording after repeated failures, or add a mechanical rule for a statically checkable pattern.
6. **Write the learning entry** — one per blind spot, in a fixed shape (what happened · the missing test +
   category · why the review missed it · the consequent change).
7. **Pattern recognition** — if the same category appears 3+ times, the wording is too weak or a mechanical
   rule is needed; fix it now, do not defer.

**Completion (Done):** the missing test exists and is GREEN · the blind spot is classified · the checking
system was updated accordingly (or the deliberate no-change is justified) · a learning entry written ·
recurrence of the same category checked.

**Enforcement note (generic).** Ritual, incident-triggered. Parts of the system update are mechanizable (a
new static rule for a checkable pattern); the blind-spot classification and the learning are human/agent-judged.

## Related

- klartext enactment (the bindings): [`../../enactment/practices/qa-retro.md`](../../enactment/practices/qa-retro.md)
- The triggers that append it: [`systematic-debugging.md`](systematic-debugging.md) (the qa-retro tail) and the `tdd` bug-fix flow ([`tdd.md`](tdd.md)).
- The periodic sibling: [`retrospective.md`](retrospective.md) — both feed the one Improvement Register.
- The review practice whose criteria it sharpens: [`qa-review.md`](qa-review.md).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
