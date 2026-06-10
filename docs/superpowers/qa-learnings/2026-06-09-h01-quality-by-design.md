# QA Learning: H01 — Quality by Design

**Date:** 2026-06-09
**Trigger:** H01 retrospective (post-mortem / RCA phase)
**Type:** Way-of-Working learning — missing test layer

## Summary

H01 exposed the absence of a contract-test layer. Tests existed at domain and router levels, but
no layer verified the *contract* between frontend and backend — assumptions at the seam were
implicit (RC6). The 422 bug was a direct consequence.

## Finding: Missing Contract-Test Layer (QA Q2 from Phase-1 RCA)

Between frontend unit tests (all mocked) and the missing E2E tests, no layer verified:
- What HTTP status codes the API returns for edge cases
- Whether domain invariants (`Fragment.create()` rejecting empty content) fire through the HTTP layer

### Why the gap was invisible during H01

1. Frontend tests mocked the API → the real endpoint was never called
2. Router tests used `FakeNarrativeUnitService` → domain validation never ran
3. No owner was assigned to the seam between frontend and backend (RC3)

### Root cause intersection (the 422)

The empty-content 422 sat at the intersection of:
- **RC6**: The contract was never surfaced ("the API accepts empty content" = unspoken assumption)
- **RC3**: The seam had no owner
- **RC5**: No process step "read the backend schema before implementing"

The validation rule existed in `Fragment.create()` — it was just never *surfaced*, *owned*, or
*checked* as a contract.

## Lesson: Name the Missing Layer

The contract-test gap is not about missing coverage in existing test files — it's about a missing
*concept*. The layer didn't exist because no one named it.

QA's role is to name the missing layer and define the pattern, not just add more tests
at the existing layers.

## Action

Contract-test layer defined and implemented in H01-422 (see `2026-06-10-h01-422-contract-test.md`):
- Pattern: `_make_real_service_client()` — real service + fake repository
- Test class: `TestCreate<Type>Contract`
- Registered in `agents/qa/claude.md` under "Contract-Test-Pattern"
