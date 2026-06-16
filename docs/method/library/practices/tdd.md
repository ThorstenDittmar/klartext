# Test-Driven Development (tdd)

> **Essence type:** Practice
> **Advances Alpha:** Software System (Demonstrable · Usable — driven by tests) and Way of Working (the test discipline is part of how we work)  ·  **Work Products:** the test suite (per level — see L2); the verified implementation
> **Activity / Activity Space:** Implement the System → write the failing test, then the minimal code that passes
> **External dependencies (referenced Resources):** **superpowers (Resource)** — wraps `superpowers:test-driven-development`
> **Enforcement:** ritual (the skill is invoked at the start of every feature/bugfix; the structural test-coverage check is mechanical — see L2)  ·  **NN:** ✓
> **Status:** living  ·  **Owner:** OE (composition shape, L3) · QA (test-level standards, L2). *SA stakes (not ownership): the L2 test levels stay consistent with the layer architecture; the S3 vendoring lint is SA-built (`.semgrep/rules/arch/`).*
> **Enacted as:** the `tdd` skill (`docs/method/enactment/skills/tdd/SKILL.md`) — a thin loader that invokes the upstream skill, then applies the klartext standards

## Purpose

How klartext implements any feature or bugfix: the generic TDD discipline, **composed** with our
project test standards. This card is a **wrapper** — it declares the upstream Resource and states only
the klartext composition shape; it does **not** restate what TDD is.

## Definition / delta (composition only)

The generic TDD discipline — the red-green-refactor cycle and its Iron Law — lives **upstream** in
`superpowers:test-driven-development` (the referenced Resource). It is **not** restated here; restating
it would be vendoring-by-paraphrase (RC4). For the discipline itself, the upstream skill is the single
source of truth.

**The klartext composition shape** (the only thing this card adds):

1. **Load the upstream discipline first.** The `tdd` skill's Step 1 invokes
   `superpowers:test-driven-development`; *all its rules apply without exception*. Everything below is an
   **extension**, never a replacement.
2. **Then apply klartext test standards** (the project delta — the *what to test and where*, not the
   *how to TDD*). The concrete bindings — the inside-out test levels (domain → service → repository →
   router), fakes-not-mocks, the Supabase integration-test rule, the `/health` endpoint rule, and the
   `qa-review` close-out step — are klartext-specific and live in the **L2** enactment card.
3. **Close with QA review.** The composition is not "done" at all-green; the `tdd` skill's final step
   invokes `qa-review` (the right tests exist, not just that the existing tests pass).

The split follows the wrapper rule: the *declaration of the composition* is here (L3); the
klartext-specific bindings (levels, fakes, integration rule, health rule, tooling) are in L2.

## Related

- **Upstream Resource:** [`../resources/superpowers.md`](../resources/superpowers.md) (`superpowers:test-driven-development`).
- **klartext enactment (the bindings):** [`../../enactment/practices/tdd.md`](../../enactment/practices/tdd.md).
- **Dependency contract:** [`../../enactment/contracts/superpowers.md`](../../enactment/contracts/superpowers.md) — the invariant (S2) that the wrapped TDD discipline still carries its Iron Law.
- [`../_card-template.md`](../_card-template.md) — the wrapper rule (declare, don't paraphrase).
- The bug-fix flow's incident-triggered sibling: `systematic-debugging` ([`systematic-debugging.md`](systematic-debugging.md)) + the `qa-retro` test-gap retro.
