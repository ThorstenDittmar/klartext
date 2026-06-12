# Retrospective: DELETE-404 — First Build Run in the New Operating Model (2026-06-12)

> **Trigger:** Hannibal (Work alpha → Closed, backend level; frontend wave postponed on verified
> grounds). **Host:** OE. **Enactment:** variant (a), artifact-mediated — all six active-tier inputs
> received (Hannibal, Narrative, QA, UX/UI, SA, DevOps), record-review tier (Causal Model, Audit,
> Community) receives this record with addendum right. **Input completeness:** 6/6, no deviation.

## 1. The run in one paragraph

DELETE-404 resolved the `remove()`/`update()` API inconsistency (option B, strict 404), decided by
the seam owner, signed off by SA, implemented (PR #81), regression-locked by QA's contract tests
(PR #82), with the frontend wave **correctly postponed** because the assumed delete flow does not
exist. It was simultaneously the first build run under ADR-0010: 4 generation changes, coordination
across mixed session types, all handovers as artifacts.

## 2. Trialed instances — evaluated (alpha walk)

| Instance | Verdict | Evidence |
|---|---|---|
| **task-readiness trace (PR body)** | **In Use** | traces in PR #81/#82 bodies (gate dated, decision reasoned, sign-off dated, merge owner named); strongest proof: UX's gate caught a blocker BEFORE the first line of code (planned consumer did not exist) |
| **Lightweight alpha lines in plans** | **In Use** (single-run evidence — watch next run) | Requirements walked Bounded → Addressed with evidence at each step; Software System close evidence delivered (Usable → Ready/backend); the Requirements line gave task-readiness a checkable target |
| **Merge protocol** | **In Use** | second real enactment: named order #81→#82, execution delegated to the gatekeeper, merge held until SA review, artifact-verified after; DevOps: "Briefing trug alle Entscheidungs-Fakten — ohne Rückfrage ausführbar" |
| **Dispatch wording (write/commit template)** | **In Use — DoD met** | all three builder dispatches carried the separated write/commit block |
| **Structural change (worktrees + terminal)** | stays **Trialed** (5/10 migrated) | carried a 4-agent build run under load; rollout continues at natural endpoints |

## 3. The lesson of this retro: silent transport failures masquerade as process failures

The central synthesis — visible only with all six inputs side by side:

- **Narrative** reports: `inbox.sh send` writes **empty messages** when the body is missing, with
  no error — his briefings to QA and UX/UI went out without content.
- **QA** reports: **duplicate artifact creation** (Narrative delivered a contract test after
  Hannibal's QA brief) and "no visibility into who is building which deliverable."

These are the same incident from two perspectives: the **third inbox bug of the same family**
(silent failure — after filename-too-long-yet-"delivered" and the title-overwrite confusion)
produced a coordination failure that looked like a process gap. Rule derived: **before adding
coordination process, check the transport for silent failures.** The empty-body guard is the fix;
the deliverable-claim idea stays registered as a real (but second-order) candidate.

## 4. Findings and agreed actions

**Agreed (owner, mechanism):**
1. **inbox.sh empty-body guard** — abort/warn on empty body (DevOps; mechanical, trivial).
2. **Dispatch template: mandatory field "consumer verified: <path/call-site>"** for frontend tasks
   against backend contracts (Hannibal; converges with his own planning learning "verify consumer
   existence before dispatching a wave" — same error type as 422/DELETE, this time caught by the
   gate instead of suffered by the user).
3. **`klartext merge <pr>` wrapper/runbook** — the gatekeeper's merge mechanics were unscripted
   friction every run (auto-merge disabled, `gh pr merge` vs. checked-out main, stale agent
   branches) (DevOps).
4. **Committed-contract rule:** a signed contract counts as SoT only once committed — uncommitted
   main-tree artifacts are invisible to worktree colleagues (worktree blindness hit a *signed*
   artifact this run; SA's collision was resolved pre-merge by the inbox relay — the model worked,
   the rule makes it cheap). Includes SA's own candidate: check open PRs on the same file before
   authoring a contract version (OE briefs SA; lands in SA process rules + contracts practice).
5. **Sign-off mechanics precision:** formal GitHub approvals are impossible single-account —
   sign-offs are **review comments** (equal artifact). Card/rule update (OE; SA's claude.md via
   briefing).
6. **ADR-0010 consequences addendum:** stop-and-wait throughput — every handover waits for the
   user's nudge; throughput = f(user availability). Honest negative, belongs in the ADR (OE briefs
   SA as ADR author). Hannibal's "Inbox-Staffel" convention (pre-nudge the foreseeable next
   recipient) registered as mitigation candidate.
7. **Remaining migration schedule:** SA, Causal Model, Audit, Community + OE migrate at natural
   endpoints; **OE is next** (retro close = the method keeper's natural endpoint).

**Registered (Identified, next retro prioritizes):** deliverable-claim/WIP marker (QA) ·
Inbox-Staffel convention (Hannibal) · launcher migration guard — warn when roster still says `app`
(QA's anomaly pair: migration skipped when planned, then executed unplanned without ritual; both
harmless by luck) · iTerm2 comfort upgrade (optional, DevOps research).

## 5. Positive evidence worth naming

- **Hannibal's depot diligence:** held a deletion *despite having clearance* because the deletion
  condition did not cover all content — interpreting release conditions narrowly is the exact
  behavior custody depots need.
- **SA's collision resolution:** reviewed the implemented version instead of defending his own,
  discarded his uncommitted draft — evidence beats authorship.
- **Five PRs (#81–#84 + #79/#80 infra), zero shared-tree incidents, zero data loss** — first
  multi-agent build day without a single near-miss.

## 6. Element sweep

New elements that appeared in use this run, checked against `method.md`:
- **Team Roster** (`agents/team.yaml`) — registered (Work Product) ✓
- **Knowledge-file landing path** (own branch → PR → OE review comment → gate) — NEW rule, home:
  agent-onboarding skill + method.md note (OE action).
- **Generation-change procedure** (pre-restart → seed → wake prompt → roster flip) — lived 5×,
  exists only in register prose → **practice card candidate** (OE, after rollout completes).
- **Inbox protocol** (send/read conventions, batch-before-acting, constraints-in-same-message) —
  lived heavily, no card → fold into the generation-change/operating-model card set later.

## 7. Work alpha

DELETE-404: **Closed (backend)**. Frontend wave: postponed with verified reasoning — re-enters as
its own work item when a delete flow exists in the frontend.

## Completion checklist

- [x] Trigger named (Hannibal, Work → Closed)
- [x] Input completeness: 6/6 active tier, artifact-mediated, no deviation
- [x] Involvement check: record-review tier (CME, Audit, Community) receives this record with
      addendum right — routing via user
- [x] Element sweep done (section 6)
- [x] Learnings recorded (this file), register updated in the same step
- [x] No deviation to record
