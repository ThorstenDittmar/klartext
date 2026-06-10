# Practice: Merge Protocol

> **Scope.** How parallel-dispatched work lands on `main`: merge ownership, ordering, and verification.
> **Out of scope.** Branch protection mechanics (CI gates, `continuous-improvement.md` §3); how tasks are
> cut and dispatched (Hannibal's coordination); the naht-check itself (DevOps activity, see `method.md`).
> **Anti-pattern guarded.** "File-path-disjoint tasks ≠ regulated merge order" — parallel PRs whose merge
> sequence is left to chance (RC5; origin: H01-422, user-flagged).
> **Language.** English — documentation-language rule.
>
> **Status:** active (ritual) · **Owner:** Hannibal (card support: OE) · **Advances Alpha:** Work
> **Non-negotiable** for every work package with ≥ 2 parallel dispatches.
> **Source:** first live enactment H01-422 (2026-06-10): #53→#54→#55, named owner, artifact-verified —
> succeeded; described from that run, not speculation.

## Goal

Every parallel dispatch lands on `main` in a **deliberate, named order** under a **named merge owner** —
no PR sequence left to chance, no foreign uncommitted work endangered.

## Rules

1. **Named merge owner** — the coordinator of the work package owns the merge sequence (default: Hannibal).
   Execution may be delegated (DevOps as gatekeeper); ownership of the *order* is not.
2. **Explicit order, dependency-shaped** — declared *at dispatch time*, e.g. contract → test → fix.
   Each later PR rebases on the merged predecessor.
3. **Pre-merge gate** — E2E-before-done (A2 gate) runs on the final branch *before* the first merge.
4. **Artifact verification** — after the sequence, the merge owner verifies against artifacts
   (`gh pr view`, `git log origin/main`), never against completion claims.
5. **Shared-tree care** — before any checkout/reset in the shared working tree: check for foreign
   uncommitted edits (`git status`); destructive operations are announced. *(Sunset clause: this rule
   dissolves if/when worktree-per-agent lands.)*
6. **Cleanup** — task branches are deleted after merge (short-lived by schema).

## Completion Checklist (Done)

- [ ] Merge owner named at dispatch time.
- [ ] Order declared before the first merge, dependency-justified.
- [ ] E2E gate passed before merging began.
- [ ] Sequence verified against artifacts (PR states, `main` log).
- [ ] Task branches deleted.

## Enforcement

Ritual (level 2), non-negotiable for parallel dispatches. Mechanical promotion candidate: branch-protection
merge-queue / required review order — evaluate when parallel volume grows.
