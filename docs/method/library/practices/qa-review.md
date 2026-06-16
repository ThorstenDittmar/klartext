# QA Review

> **Essence type:** Practice
> **Advances Alpha:** Software System (Demonstrable — the right tests exist, not just that the existing tests pass)  ·  **Work Products:** the gap-closing tests written into the diff (RED → GREEN); a QA review report (the five-category verdict, gaps found, deferrals)
> **Activity / Activity Space:** Test the System → before declaring work done, a fresh-eyes review of the diff for the tests that *should* exist
> **External dependencies (referenced Resources):** none — this is a klartext-own QA practice (not a superpowers wrapper)
> **Enforcement:** ritual (invoked at the close of every implementation session; `tdd` calls it as Step 3)  ·  **NN:** ✓
> **Status:** living  ·  **Owner:** QA
> **Enacted as:** the `qa-review` skill (`docs/method/enactment/skills/qa-review/`)

> **Seeded by an OE-spawned sub-agent (F0.2-P-C, BARRIER mode); awaits ratification by real QA on wake (Guardrail 2).**

## Purpose

How klartext verifies that an implementation is *test-complete* before it is declared done: dispatch a
**fresh QA sub-agent** — one with **no context** from the implementation session — to review the diff with
clean eyes for missing tests, edge cases, and contract completeness, then write the missing tests. Guards the
failure mode where **all-green is mistaken for done**: the existing tests pass, but the tests that *should*
exist were never written. A passing suite proves the written tests pass; it does not prove the right tests
were written.

## Definition / delta

This is a **self-owned** klartext QA practice — it references no upstream Resource. The generic shape:

**The fresh-eyes principle.** The reviewer is a **separate sub-agent with no implementation context**. This
is deliberate, not incidental: an author re-reading their own diff sees the code they meant to write, not the
cases they forgot. A context-free reviewer reads only what is on the page.

**The run.**
1. **Collect the diff** (`git diff HEAD`, or `--staged` for uncommitted work).
2. **Dispatch the fresh sub-agent** with the review criteria and the diff. Its sole job: find missing tests
   and write them.
3. **Review against a fixed category set** — coverage, edge/error cases, infrastructure tests, fake-contract
   completeness, and (when applicable) domain-composition tests. The concrete category checklist is a
   klartext binding (see L2).
4. **Write the gaps as RED tests** directly into the test files — never merely describe them. A gap marked
   `[WRITTEN]` without code is a false claim; confirm RED before reporting.
5. **Report** in a fixed format (complete · gaps written · requires-manual-decision), then **act**: make every
   RED test GREEN, or record an explicit reason for any deferral.

**Completion (Done):** every category checked · every gap either written as a now-GREEN test or carried as an
explicit, justified deferral · no unresolved manual-action item left silent · a report produced.

**Enforcement note (generic).** Ritual at invocation; structural slices of the coverage check are
mechanizable (a source-file → test-file checker). The judgement — *which* tests are missing, whether a fake
silently diverges — stays human/agent-judged: qa-review is QA judgement, not a coverage counter.

## Related

- klartext enactment (the bindings): [`../../enactment/practices/qa-review.md`](../../enactment/practices/qa-review.md)
- The composition that calls it: [`tdd.md`](tdd.md) (Step 3 close-out).
- The incident-triggered test-gap sibling: [`qa-retro.md`](qa-retro.md).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
