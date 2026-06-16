# Merge Protocol — klartext enactment

> **Scope.** klartext's enactment of the **Merge Protocol** practice: who owns the merge, the gatekeeper
> split, the live precedent, and the sunset clause.
> **Out of scope.** The generic rules — see the L3 card. Branch-protection mechanics (CI gates,
> `../continuous-improvement.md` §3); how tasks are cut and dispatched (Hannibal's coordination); the
> naht-check itself (DevOps activity, see `../method.md`).
> **Anti-pattern guarded.** "File-path-disjoint tasks ≠ regulated merge order" — parallel PRs whose merge
> sequence is left to chance (RC5; origin: H01-422, user-flagged).
> **Language.** English — documentation-language rule.
>
> **L3 definition:** [`../../library/practices/merge-protocol.md`](../../library/practices/merge-protocol.md)
> **Status:** living (ritual) · **Owner:** Hannibal (card support: OE) · **Advances Alpha:** Work · **NN:** ✓ (≥ 2 parallel dispatches)

## klartext bindings

- **Named merge owner:** default **Hannibal** (the work-package coordinator — *Coordinate Activity*).
  Execution may be delegated to **DevOps as gatekeeper**; ownership of the order stays with Hannibal.
- **Pre-merge gate:** the **E2E-before-done (A2 gate)** runs on the final branch before the first merge.
- **Artifact verification:** `gh pr view`, `git log origin/main` — never completion claims.
- **Shared-tree care — sunset clause:** the foreign-uncommitted-edit check (`git status` before any
  checkout/reset in the shared tree) **dissolves if/when worktree-per-agent lands** (which is now the
  steady state — revisit whether this rule still applies).

## Enforcement (klartext)

Ritual (level 2), non-negotiable for parallel dispatches. Mechanical promotion candidate: branch-protection
merge-queue / required review order — evaluate when parallel volume grows.

## Evidence / learnings

- **First live enactment H01-422 (2026-06-10):** #53→#54→#55, named owner, artifact-verified — succeeded.
  This card was described from that run, not speculation.
