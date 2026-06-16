# Naht-Check

> **Essence type:** Activity
> **Advances Alpha:** Work (clean integration onto the mainline)  ·  **Work Products:** none (a verification over an existing PR)
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (every increment)
> **Status:** living  ·  **Owner / enactment owner:** DevOps (enacted on every increment since #45)
> *(Subtype: gate — a verification Activity over an existing PR; clarifier kept out of the Essence-type enum value.)*

## Purpose

Before a PR merges, verify that it contains **exactly the intended files — nothing more, nothing less**.
Guards the seam (*Naht*) failure mode: stray files, leftover scratch artifacts, an unrelated change, or a
forgotten file riding along on a change set, polluting the mainline.

## Definition / delta

For each PR, the enactment owner inspects the diff against the declared intent of the change:

1. **Every intended file is present** — nothing the change required is missing.
2. **No unintended file is present** — no scratch files, no unrelated edits, no leftover artifacts, no file
   that belongs to a different work package.
3. **Mismatch → the PR does not merge** — the diff is corrected (split out the stray change, add the
   missing file) before the seam is closed.

The check is performed against the *declared* file set of the change, not against a vague impression that
"the PR looks fine."

**Completion (Done):** the PR diff was inspected against the declared intent · every intended file present ·
no unintended file present · any mismatch resolved before merge.

**Enforcement note (generic).** Ritual today, **enacted by DevOps** on every increment. Strong mechanical
promotion candidate: a CI check comparing the changed-file set against a declared manifest / path allowlist.
Composes with the [[four-eyes]] pattern (a second party owns the "intended file set" criterion).

## Related

- [[e2e-before-done]] (the other pre-merge gate) · [[agent-provenance]] ·
  [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
