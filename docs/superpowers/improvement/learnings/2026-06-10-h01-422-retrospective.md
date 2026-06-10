# Retro 2 — H01-422 Walking Skeleton (record + learnings)

> **Retro record — second run of the Retrospective practice (2026-06-10).**
> **Trigger (entry criterion):** work-package close H01-422, declared by Hannibal (Work alpha *Concluded*;
> *Closed* via this retro's lessons). **Leader:** OE (Method Keeper) · **Active input:** Hannibal (close
> report + agenda), UX/UI, Narrative, QA (via post-package captures, consolidated in Hannibal's custody
> depot), user. **DevOps:** merge execution verified against artifacts; post-compact self-report (reset
> mode, loss self-assessment) still pending — carried as open input. **Non-participants** CM + Audit
> delivered findings voluntarily (record-review tier avant la lettre).
> **Involvement check:** SA *was* a participant (B1 contract-SoT decision) and gave no capture — gap
> recorded, targeted question routed. Otherwise: nobody missing.
> **Language.** English — documentation-language rule.

## Headline result

**The skeleton validated the integrated way of working end-to-end** — dispatch with held `task-readiness`
gate (3/3, coordinator-attested; see learning 4) → TDD → qa-review (found 5 extra tests) → E2E verification
*before* merge (typing → 201, screenshot) → enacted merge protocol (#53→#54→#55, named owner, verified
against artifacts) → captures → this retro. The T6/RC2 circle from H01 (advisory gate never invoked) is
**closed with evidence**. Way-of-Working *Foundation Established*: **5/6** (from ~4/6) — "integrated way of
working available" is now checkable ✓; the single open box is "non-negotiables marked per practice"
(agreed action below). **When it closes, the team-refresh milestone fires.**

## Learnings

### 1. Guard chains need end-to-end verification, not per-link checks
The compaction-monitoring **2nd trial FAILED — one level deeper than the 1st**. The chain has three links:
PostCompact hook (writes `compact-log.txt`) → log → monitor script (reads, alerts). Retro 1 fixed link 3
(script existed only on salvage); the infra tests verify link 3's existence. Today's evidence: ≥6 compacts
(OE manual, DevOps auto, 4 capture sessions) and **zero log lines anywhere** — link 1 never fired. Cause
candidates (verification = agreed action): hooks live in `klartext/.claude/settings.json` but sessions run
with cwd `/Users/thormar` (project settings likely never load), plus a cwd-relative log path. **Per-link
existence checks pass while the chain is dead. A guard chain needs one end-to-end test: inject a synthetic
log entry → expect digest/notification.** ⚠️ Side question (potentially big): if project settings don't load
for our sessions, *every* project-level hook/permission may be inert — verify.

### 2. False persistence — a named RC4 variant
Two independent cases (UX/UI, QA): **compacted session summaries claimed writes that never happened**
(files unchanged, git log empty). "Memory says saved, artifact says no." Consequence for every capture:
the completion checklist must end with **artifact verification** (`git status` / `git log` on the claimed
targets), never with the session's own claim. Maps to RC4 (active-vs-recorded drift) — no new root cause.

### 3. The capture practice works — and its gap list is now precise
The validation run on 4 non-OE sessions produced convergent frictions (3× independent): OE-centric homes;
missing `agents/<name>/claude.md` branch; PENDING.md sub-agent write permission promised by the skill but
never declared in any `start.sh` (would fail silently — RC2 class); unclear step-1.5 trigger; no slot for
parked findings; step 6B not executable for domain agents. Plus Hannibal's dispatch-wording finding:
"nichts committen" was read as "nichts schreiben" (RC6 — tacit seam assumption), leaving QA knowledge
chat-only. **"Instantiate through use" delivered exactly what speculation could not: a checkable fix list.**

### 4. task-readiness held — but leaves no artifact trace
All three builder dispatches carried the gate as first instruction and all three sessions ran it
(coordinator-attested + capture-corroborated). Honest limit: invocation leaves **no independent artifact**;
verification relies on session testimony. Improvement candidate recorded (mechanical trace, e.g. a
readiness note in the PR body).

## Step-1 evaluation of prior improvements

- **Compaction monitoring:** 2nd trial **failed** → *Action Agreed* (3rd): DevOps — fix hook layer
  (settings location vs. session cwd + absolute paths) **+ one end-to-end chain test**; DoD: synthetic
  `| auto |` entry produces digest + notification on a live session; then 3rd trial.
- **Branch protection:** held again across #53–#58 (incl. transient CI rate-limit handled by re-run) —
  stays *In Use*, evidence grows.
- **Classify step:** held through retro prep (no new inventions; Method-Keeper reuse) — stays *In Use*.

## Agreed actions (owner · DoD · enforcement)

1. **pre-compact multi-agent fix bundle** — OE · skill gets: domain-agent home branch
   (`agents/<name>/claude.md` + own learnings), per-agent home list, step-1.5 trigger rule, "parked
   findings/retro inputs" category in step 1, conditional step 6B, **artifact-verification step (learning 2)**;
   DoD: re-validation on one non-OE session passes without the reported frictions · ritual. *(EN migration +
   versioned home ride along per the existing Prioritized row.)*
2. **start.sh permission audit** — OE · all `agents/*/start.sh` checked: PENDING.md write permission
   declared where the skill promises it; DoD: audit note + fixed scripts committed · mechanical (permissions).
3. **Compact-monitor chain repair** — DevOps · as in step-1 evaluation above · mechanical.
4. **Dispatch wording rule** — Hannibal · dispatch template separates "write files: YES / commit-merge: NO";
   DoD: next dispatch uses it · ritual.
5. **Non-negotiables marked per practice** — OE · `method.md` gets a non-negotiable flag per element;
   DoD: column present, every practice marked · ritual. **Closes the last Foundation-Established box →
   triggers the team refresh.**
6. **Merge-protocol practice card** — OE (content from Hannibal) · card describes the enacted protocol
   (named merge owner + explicit order + artifact verification); DoD: card + method.md row · ritual.

## Routing (step 7)

Domain knowledge from the depot stays with its owners: UX/UI A1–A3 → `agents/ux/claude.md`; QA capture
(protocol sections, learnings files, contract-test pattern) → `agents/qa/claude.md` + `qa-learnings/`;
Narrative A1 (interface-owner role) → `agents/narrative/claude.md` — each entered by the owning session
(user relays), **with artifact verification per learning 2**. CM's `# type: ignore` gate proposal → register
(done by Hannibal) → SA rule → DevOps wiring. DELETE-404 decision A/B is **product work, not retro scope**
(Team, not Product) — routed via Hannibal to Narrative+SA as a regular task. Hannibal's custody depot is
deleted after the above routings are verified. SA receives the involvement-check question.

**Work alpha H01-422: Closed** (lessons learned = this record).
