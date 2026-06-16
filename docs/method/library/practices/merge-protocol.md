# Merge Protocol

> **Essence type:** Practice
> **Advances Alpha:** Work  ·  **Work Products:** a named merge owner + a declared merge order; the verified integration on the mainline
> **Activity / Activity Space:** Coordinate Activity → land parallel-dispatched work on the mainline in a deliberate, verified order
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (for every work package with ≥ 2 parallel dispatches)
> **Status:** living  ·  **Owner:** the work-package coordinator (card support: OE)
> **Enacted as:** — (ritual; mechanical promotion candidate = merge-queue / required review order)

## Purpose

Every parallel dispatch lands on the mainline in a **deliberate, named order** under a **named merge owner** —
no PR sequence left to chance, no foreign uncommitted work endangered. Guards the failure mode where
file-path-disjoint tasks are treated as if their merge sequence were irrelevant.

## Definition / delta

1. **Named merge owner** — the coordinator of the work package owns the merge sequence. Execution may be
   delegated (to a gatekeeper); ownership of the *order* is not.
2. **Explicit order, dependency-shaped** — declared *at dispatch time*, e.g. contract → test → fix. Each
   later PR rebases on the merged predecessor.
3. **Pre-merge gate** — end-to-end verification runs on the final branch *before* the first merge.
4. **Artifact verification** — after the sequence, the merge owner verifies against artifacts (PR states,
   mainline log), never against completion claims.
5. **Shared-tree care** — before any checkout/reset in a shared working tree: check for foreign uncommitted
   edits; destructive operations are announced. *(Dissolves if/when worktree-per-agent isolation lands.)*
6. **Cleanup** — task branches are deleted after merge (short-lived by schema).

**Completion (Done):** merge owner named at dispatch time · order declared before the first merge,
dependency-justified · end-to-end gate passed before merging began · sequence verified against artifacts ·
task branches deleted.

**Enforcement note (generic).** Ritual, non-negotiable for parallel dispatches. Mechanical promotion
candidate: branch-protection merge-queue / required review order — evaluate when parallel volume grows.

## Related

- klartext enactment: [`../../enactment/practices/merge-protocol.md`](../../enactment/practices/merge-protocol.md)
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
