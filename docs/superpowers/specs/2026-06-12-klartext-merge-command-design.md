# Design: `klartext merge` — verified PR-merge wrapper

> **Status:** approved (user, 2026-06-12) · **Owner:** DevOps · **Advances Alpha:** Work
> **Source:** DELETE-404 retrospective action item (DevOps' own retro candidate, accepted by OE).
> **Method-policy ratification:** merge-method policy proposed by DevOps, OE/Hannibal ratification
> pending (see Open Questions). Build proceeds with the proposed policy; documented as such.

## Problem

Merging a PR as the Gatekeeper currently means re-deriving the same mechanics every run:
poll CI by hand, choose a merge method, merge via the API (because `gh pr merge` breaks when
`main` is checked out in a worktree), delete the branch, verify against `main`. This friction
was surfaced in the DELETE-404 retro: every run reinvents the flow, and the worktree / disabled
auto-merge papercuts are hit each time.

`klartext merge <pr>` encodes the verified-merge flow once.

## Goal

One command lands a single PR on `main` the verified way: preconditions checked → required
checks green → merged with the right method → branch deleted → result verified against `main`.

Out of scope (YAGNI): merge-order orchestration across multiple PRs (stays with Hannibal's
Merge Protocol / human), auto-rebasing branches, multi-PR stack commands. This command merges
**one** PR cleanly.

## Command

```
klartext merge <pr-number> [--method squash|merge] [--keep-branch] [--timeout SECONDS]
```

- `<pr-number>` — required, the PR to merge.
- `--method` — `squash` (default) or `merge`. **No `rebase`** (see Merge-method policy).
- `--keep-branch` — skip branch deletion (default: delete, per Merge Protocol rule 6).
- `--timeout` — max seconds to wait for checks (default: 900).

## Flow

1. **Preconditions** — via `gh pr view <pr> --json state,mergeable,mergeStateStatus`:
   PR must be `OPEN` and not in a blocked/dirty merge state. Otherwise abort (`typer.Exit(1)`)
   with the concrete reason.
2. **Poll required checks** — `gh pr checks <pr>` until no check is `pending`. Abort if **any**
   check fails (never merge a red PR). Abort on `--timeout`. Print progress.
3. **Merge via GitHub API** — `gh api repos/{repo}/pulls/{pr}/merge -X PUT -f merge_method=<method>`.
   Deliberately **not** `gh pr merge`: that uses the local git checkout and fails with
   "main is already checked out" in the worktree layout (verified friction, this session).
4. **Delete branch** (unless `--keep-branch`) — delete the PR head branch via the API.
   Merge Protocol rule 6: task branches are short-lived.
5. **Verify against artifacts** — print `git log --oneline -5 origin/main` (after fetch) so the
   landed merge/squash commit is visible. Merge Protocol rule 4: verify against artifacts, not
   completion claims.

## Merge-method policy (proposed)

Grounded in industry practice (squash as the standard feature-branch default; merge-commit to
preserve history / shared-or-stacked branches; rebase rewrites hashes) and our two lived patterns:

- **`squash` (default)** — single-agent PR = one work item. Clean linear `main`, one line per PR.
  Matches every standalone DevOps infra PR (#79, #80, #83, #85, #86).
- **`merge` (merge-commit)** — SHA-preserving, for stacks where a later PR contains an earlier
  PR's commits (DELETE-404 #81→#82). A squash/rebase there rewrites SHAs and duplicates/breaks
  the stack.
- **`rebase` excluded** — rewrites SHAs (same stack-breaking footgun as squash on a stack) and
  offers nothing squash doesn't for our single-unit PRs. Removing it removes a dangerous option.

The Merge Protocol practice governs order/ownership/verification/cleanup but is silent on the
merge method; this policy is proposed to slot in there, pending OE/Hannibal ratification.

## Error handling

Every abort raises `typer.Exit(1)` with a concrete message naming the failed precondition or
check. No silent swallowing (CLAUDE.md error-handling rule).

## Testing

The pure decision logic is factored into testable helpers and covered by infrastructure tests:
- merge-method validation (accepts `squash`/`merge`, rejects `rebase` and unknown values),
- check-status evaluation (a set of check states → `pass` / `fail` / `still-pending` decision),
- precondition evaluation (PR-state JSON → proceed / abort-with-reason).

The live `gh`/`git` calls are not headless-testable in CI; this is documented honestly (same
stance as `morning.sh`). No hollow mock tests that would pass even when the real call breaks.

## Open questions

- **Merge-method policy ratification** — sent to OE (2026-06-12): does `squash` default /
  `merge` for stacks / no `rebase` slot into the Merge Protocol, or is a different policy
  preferred? Build proceeds with the proposed policy; trivially adjustable if OE/Hannibal differ.
