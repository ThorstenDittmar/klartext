# E2E-before-done

> **Essence type:** Activity
> **Advances Alpha:** Software System (proves the change works end to end before it lands)  ·  **Work Products:** captured evidence of the end-to-end run
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (before marking work Done / before merge)
> **Status:** living  ·  **Owner / enactment owner:** Hannibal (work-package coordinator; first run H01-422)
> *(Subtype: gate — a pre-merge verification Activity; clarifier kept out of the Essence-type enum value.)*

## Purpose

Before a change is marked Done or merged, verify it **end to end on the live system** and **capture the
evidence**. Guards the works-on-my-claim failure mode: declaring success from unit-level passes or a
completion claim, without proof the whole path runs on the real system.

## Definition / delta

This is the A2 acceptance gate of a work package:

1. **Run end-to-end on the live system** — exercise the full path the change touches against the running
   system, not only the isolated unit or a mock.
2. **Capture the evidence** — record the proof of the run (output, screenshot, log, response) so the result
   is verifiable after the fact, not asserted from memory.
3. **Gate before merge** — the run happens *before* the first merge and *before* "Done" is claimed. A
   failing or absent end-to-end run blocks completion.

Acceptance is judged against the captured evidence, never against a completion claim alone.

**Completion (Done):** the change was exercised end to end on the live system · evidence of the run was
captured and is verifiable · the run passed *before* merge / before "Done" was claimed.

**Enforcement note (generic).** Ritual, **enacted by Hannibal** (the work-package coordinator) as the A2
gate; first run H01-422. Composes with the [[merge-protocol]] practice (the pre-merge gate it references)
and the [[four-eyes]] pattern (evidence is checked by a party other than the executor).

## Related

- [[naht-check]] (the other pre-merge gate) · [[four-eyes]] ·
  [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
