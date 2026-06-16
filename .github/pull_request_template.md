<!--
  Classification (ADR-0012)
  If this PR touches a Way-of-Working surface — CLAUDE.md, docs/method/enactment/skills/**,
  agents/**/claude.md, .claude/settings.json, scripts/**, api/cli.py — add EXACTLY ONE label:

    • rolling  — additive / backward-compatible. Worktrees adopt it lazily via `klartext converge`.
    • breaking — changes the meaning of an existing rule, hook, path, or contract.
                 Needs a coordinated rollout (all worktrees converge before it is relied upon).

  Default-free: if you are unsure, choose `breaking`.
  The Classification Gate check fails until exactly one label is present on such PRs.
  PRs that touch no Way-of-Working surface need no label — the gate passes automatically.
-->

## What

<!-- One or two sentences: what changes and why. -->

## Classification

<!-- Only required if this PR touches a Way-of-Working surface (see comment above). -->
- [ ] `rolling` — additive / backward-compatible
- [ ] `breaking` — meaning-changing; needs coordinated rollout
- [ ] not applicable — touches no Way-of-Working surface

## Notes

<!-- Anything reviewers should know: trade-offs, follow-ups, out-of-scope items. -->
