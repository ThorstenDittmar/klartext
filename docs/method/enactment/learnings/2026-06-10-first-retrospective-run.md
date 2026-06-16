# Learning: Guards drift too — enforcement mechanisms need their own existence checks

> **Retro record — first run of the Retrospective practice (2026-06-10).**
> **Trigger (entry criterion):** milestone *"C-minimal method foundation laid"* — method document set
> complete, first three practices composed, all on `main` (PRs #45/#46/#48/#49).
> **Leader:** OE (Method Keeper, Method Literacy ≥ 2) · **Participant:** user.
> **Language.** English — documentation-language rule.

## The learning

The compaction monitor — itself deployed as a *guard against drift* (RC4) — silently failed from day one:
launchd fired on schedule, but the target script (`scripts/check-compact-log.sh`) does not exist. The only
trace was an error line in a gitignored log nobody was required to read. **RC4 applies to enforcement
mechanisms themselves:** a mechanical guard without its own existence/liveness check is just an advisory
rule wearing a mechanical costume.

**Why it matters:** our Enforcement Hierarchy (mechanical > ritual > never advisory-only) assumed that
"mechanical" means "holds by itself". This incident shows the hierarchy needs a footnote: a mechanism only
counts as mechanical if something *checks the mechanism* (infrastructure test, health check).

**How to apply:** every mechanical gate gets a verifier — for scripts/jobs an infrastructure test that the
target exists and is executable; this matches the existing IaC rule "scripts and health checks update
together". Agreed action lives in the Improvement Register (compaction-monitoring row, owner DevOps).

## Run summary (evidence for the practice itself)

- **Step 1 (evaluate previous actions):** 2 *Trialed* instances evaluated — Classify step → **In Use**
  (≥4 successful applications); compaction monitoring → **failed trial**, back to *Action Agreed* with a
  sharper DoD. Nothing left silently on *Action Agreed*. ✅
- **Step 2 (evidence):** compact-monitor log, CI/PR status, documented incidents (Community omission,
  Eigensaft near-misses, premature compact recommendation at 30% utilization → RC2: advisory rules do not
  bind behavior under pressure — folded into the monitoring item's rationale).
- **Step 3 (alpha-walk):** Way of Working *Foundation Established* re-assessed ~1.5/6 → **≈4/6**; blocking
  checkbox identified: *integrated way of working available* → exactly the 422 Walking Skeleton's job.
- **Step 4 (RC mapping):** both findings map to existing RCs (RC4, RC2) — no new root cause.
- **Steps 5/6:** "Docs increment to DevOps" → *Prioritized* with action proposal; monitor re-fix →
  *Action Agreed* (owner + DoD + mechanical enforcement).
- **Step 7:** this file; register updated; retro card + `method.md` updated in the same session
  (entry criteria, two-tier competencies, state-annotation fix).

**Practice verdict:** the card worked as written; the completion checklist was walkable. The failed-trial
path (Results Evaluated negative → new action) was exercised on the first run — the RC2 medicine
("decided ≠ verified") demonstrably bites.

## Addendum — involvement check, applied retroactively (2026-06-10)

The run itself exposed a gap in the card: participation was framed as "work-package participants only",
which structurally cannot detect *"someone should have been involved and was not"* (the Community-omission
failure mode). The card now defines **whole-team reach with two tiers** (active input from work-package
participants, record review by everyone else) plus an explicit **involvement check** per retro.

Applied retroactively to this run, the check finds: **DevOps was a work-package participant** (PRs
#45/#46/#48/#49, the compaction monitor) **and gave no input** — notably on the monitor, where their
perspective is exactly the missing evidence (why did the script never land in the repo?). Routed via the
combined DevOps briefing; their answer feeds the monitor improvement's next state. The record-review tier
for the remaining agents is not yet meaningful (team refresh pending) — roster check run manually instead.
