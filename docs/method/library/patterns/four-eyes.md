# Four-Eyes Principle

> **Essence type:** Pattern
> **Advances Alpha:** Software System (also Work — protects integration)  ·  **Work Products:** none (a structuring constraint, not an artifact)
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (whenever execution and acceptance criteria are separable)
> **Status:** living  ·  **Owner:** OE (pattern form)

## Purpose

Separate the party that **executes** a piece of work from the party that **owns its acceptance criteria** —
so no agent both does the work and judges whether the work is acceptable. Guards the self-grading failure
mode: an executor who also owns the criteria can declare success without an independent check.

## Definition / delta

A four-eyes instance pairs two distinct roles on one piece of work:

1. **Executor** — produces the change (code, document, configuration).
2. **Criteria-owner** — owns the standard the change is measured against and performs (or owns) the check.
   The criteria-owner is a *different* agent/role from the executor.

The two must not collapse into one identity. Where a single agent has both skills, the roles are still
split across agents by domain (e.g. QA owns the verification criteria; UX/UI executes the change). The
check is performed against the criteria-owner's standard, never against the executor's own claim.

**Completion (Done):** executor and criteria-owner are distinct identities · the criteria predate the
check (owned by the criteria-owner, not invented by the executor) · the check ran and its result is
recorded against those criteria.

**Enforcement note (generic).** Ritual; mechanically promotable where the platform supports it —
required-reviewer rules, branch protection forbidding self-approval, a CI gate owned by the criteria role.
The single shared GitHub identity (see [[agent-provenance]]) is *why* self-approval enforcement currently
relies on role separation rather than account separation.

## Related

- Enacted today as an instance in the `verify` skill (QA owns criteria · UX/UI executes).
- [[agent-provenance]] (identity that makes executor/criteria-owner distinguishable) · [[naht-check]] ·
  [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
