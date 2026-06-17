# Frozen Plan — Method / Product Separation Refactoring

> **Status:** FROZEN — F0 in progress (OE-led, started 2026-06-16). §6/§7 mechanic verified + sharpened by DevOps; OE + DevOps signed off; plan merged to `main` (#130). F0 = produce the method as well-formed Essence objects, path-classified (§4), executed in lead-and-spawn barrier mode (§2).
> **Owners (method coordination):** OE + DevOps. **Hannibal is OUT** (product coordinator, not method). **SA:** architecture landed (ADR-0013/0014). **QA:** coverage-audit + qa-review gate owner.
> **Decision records:** [ADR-0013](../../adr/0013-separating-method-from-product.md) (layer architecture, path-based classification, distribution), [ADR-0014](../../adr/0014-agent-provenance-trailer.md) (agent provenance). **Practice:** `improvement/practices/controlled-method-rollout.md` (barrier mode). **Contract:** `improvement/contracts/memory-substrate.md` (C1–C5).
> **This document is the coordination backbone** — it is designed to **survive the rebuild** (§2). The substrate (inbox/memory) it coordinates is itself in scope of the change, so coordination runs over **this repo artifact + the user out-of-band**, not over the substrate.

## 1. Purpose & scope

Separate klartext's **collaboration method** from the **product/app code**, realizing the Essence **Library vs. Method-in-use** architecture (ADR-0013). Three tasks, one question ("what is our method as a thing, and how does it relate to the projects that use it"):

- **#1 App ↔ method separation** — (#1a) coarse CI directory-scoping now; (#1b) card-wise extraction of Layer 3 along the path convention.
- **#2 Agent git-attribution** — the provenance trailer (ADR-0014), = C5 generalized to git.
- **#3 klartext ↔ semAIt isolation** — (#3a) urgent user-global-state isolation; (#3b) skill-distribution isolation (cut-dependent).

**Out of scope:** product code logic; semAIt's own product build (it seeds once from our **post-cut** state and diverges; it is a *consumer of a product*, not a co-user of our method).

## 2. Coordination model — lead-and-spawn BARRIER

This refactoring is a **breaking way-of-working change** → **barrier mode** of the Controlled Method Rollout practice (Stabilize & Halt → Update → Resync & Verify). It is executed via **lead-and-spawn**, *not* the steady-state long-lived-session + inbox model (which is unchanged):

- One **lead** at a time (OE or DevOps) orchestrates by **spawning fresh sub-agents** for sub-tasks. Fresh spawns read the laid-down state → **drift = 0**. The current all-clean state (every non-OE/DevOps agent filed + clean) is the window that makes this cheap.
- **Channel that survives the rebuild:** this frozen plan (repo artifact) + the **user out-of-band**. The **inbox is used only for wake-signals while it is stable**; once the substrate/inbox is itself being changed (#3/F3), coordination is plan + user only. *Rationale: you cannot coordinate a substrate change through the substrate being changed; the Memory-Substrate Contract's C1–C5 are not guaranteed mid-change.*

### Guardrails (mandatory)
1. **Lead-handoff = anchor-complete.** Before the other lead takes over, the outgoing lead has filed + verified everything.
2. **Domain authority preserved.** A spawned sub-agent is **seeded with its domain's Hoheitswissen**; the **real domain agent wakes afterwards to verify/ratify** its domain's changes. The lead executes under barrier; the domain owner ratifies on return. (Validated on the ADR: OE-spawn-draft → SA-ratify → real SA owned + landed.)
3. **Spawn-aware provenance.** Commits/memory edits stamp `Agent: <lead> (spawned <task>)` (ADR-0014 / C5).
4. **Lead controls parallelism** (avoids the C4 concurrency case on the repo).
5. **Scope is announced** ("now in lead-and-spawn barrier mode for X") to avoid mode-confusion; **wake-verify per touched domain is mandatory.**

## 3. Roles & sleep/wake

- **Awake (method crew):** OE, DevOps, SA, QA. (Method-driving roles — generic.)
- **Asleep (product-domain experts):** Narrative, Causal Model, Audit, Community, UX. (Layer-2/product — woken only if their domain is touched, and then **converge-first** before working.)
- **Leads:** **OE F0–F1**, **DevOps F2–F3**, anchor-handoff between. SA on-call for ADR follow-ups (ADR-0014). QA on-call for the coverage-audit gate + qa-reviews (spawned per the lead-and-spawn model; real QA ratifies).

## 4. F0 — produce the method as well-formed Essence objects, path-classified (OE-led, gating)

F0 is **not just "draw the path cut."** It is **"produce klartext's method as a coherent set of well-formed Essence objects, laid down in the L3/L2 path stems."** That subsumes two kinds of work: **(b1) split** existing cards into generic-definition (L3) + klartext-evidence (L2), **and (b2) build** the Essence objects that do not yet exist as well-formed elements. *(Rationale: the card-wise split assumes a well-formed generic definition to extract — but `method.md` itself flags that many of our practices are lived-as-skills with **no card**, several patterns are prose, and there is no explicit Method-composition object. A path-classified pile with holes is not a real Essence Library for semAIt to seed from.)*

- **Path convention** (ADR-0013): **L3 stems** = `scripts/`, the converge part of `api/cli.py`, method-related `.github/workflows/`, hooks, and **`docs/method/library/`** (generic definitions + the Essence summary + generic skills). **L2 stems** = **`docs/method/enactment/`** (klartext runs/evidence/friction/register/learnings/environment) + klartext-specific skills. `docs/superpowers/skills/` classified per file (OE-confirmed table in ADR-0013).
- **Semantic criterion:** L3 = holds for ANY endeavour using the practice; L2 = specific to klartext's runs/decisions/evidence/product. **OE/SA classify once; a CI check (DevOps) enforces forever.**

### 4.1 Essence objects to build/complete (lean — load-bearing only; source = `method.md` "Known gaps")
- **Practice cards** for the ~10 un-carded lived practices (TDD, QA Review, QA Retro, Task Readiness, Knowledge Routing, Anchor, Frontend Verification, Systematic Debugging, Frontend Standards, Agent Onboarding) — each referencing the Alpha it advances, the Work Products it produces, and the Activity/Activity-Space it fills.
- **Pattern cards** for the prose patterns (Memory Park / Custody, Blocker Protocol, …).
- **The explicit Method-composition object** (L2) — klartext's method = *these* Library practices, composed, with their lived Alpha states. The L2 counterpart to the L3 Library.
- **Element cards for the elements we forged**: the **Dependency Contract** element and the **Agent-Provenance** Pattern.
- **Partial/iterative (do not over-engineer — Gall's Law):** Activity-Space mapping and Competencies beyond *Method Literacy* may stay partial and grow later; they are not a freeze blocker.

- **F0 acceptance criterion (the gate) — sharpened:** the cut is **DONE only when (i) every method object is automatically path-classifiable** (CI rejects method content outside the L3/L2 stems and any still-"mixed" card) **AND (ii) every L3 object is a well-formed Essence element** (a card exists; it names the Alpha it advances + its Work Products + its Activity). Both halves, under SA review. The per-card split of `practices/`+`contracts/` and the building of the missing cards are the bulk of F0's work.
- **Consequence:** because classification = path, the F3 extraction (`git filter-repo --path` on L3 stems) runs **mechanically**, so DevOps can lead it without per-object judgment — *provided F0 produced well-formed L3 objects in the first place.*

## 5. Sequence F0 → F3

| Phase | Lead | Work | Gate to next |
|---|---|---|---|
| **F0** | OE | Produce the method as well-formed Essence objects, path-classified (§4): **split** existing cards + **build** the missing ones (un-carded practices, prose patterns, the Method-composition object, the new-element cards) + the CI classification check. | **F0 acceptance criterion green** (both halves: every object path-classifiable — no mixed cards, no out-of-stem method files — **and** every L3 object a well-formed Essence element). |
| **F1** | OE (DevOps spawns mechanic bits) | **#3a** urgent isolation (per-project memory pin, settings, MCP — semAIt is spinning up *now*) · **#1a** coarse CI directory-scoping (footgun-safe, classify-gate pattern — *DevOps already started, TDD + qa-review-gated*) · first inventory. Cut-independent → may run in parallel with F0. | #3a isolation verified; #1a landed (qa-review-gated). |
| **F2** | DevOps | **Three HARD gates** (see §6): coverage audit · first-pass contract audit · tested out-of-band backup/restore. | **All three gates pass.** |
| **F3** | DevOps | **#3b** skill-distribution isolation · **#1b** card-wise extraction (`filter-repo` on L3 stems, full history; squash-snapshot for the semAIt seed) · **#2** provenance trailer (ADR-0014). Under lead-and-spawn barrier. | Extraction verified; provenance live; substrate restored-and-verified. |

**Then:** semAIt seeds **once** from the **post-cut** state; F-execution closes; agents wake + converge; steady-state resumes.

## 6. The three hard gates (F2) — explicit pass criteria

1. **Coverage audit** — *owners DevOps + QA, qa-review-gated.* Audit existing test coverage of the mechanics we touch (`converge`, `classify_gate`, `session_health`, `cli`) incl. error/edge cases; close the load-bearing gaps **TDD-first**. **Cut-independent inventory DONE (DevOps, 2026-06-15):** `converge` 10 · `classify_gate` 23 · `session_health` 28 · `cli` 42 · `session_start_hook` 14 tests, incl. error/edge cases (rebase-abort, offline-fetch, bare-worktree, dirty-WIP). **Re-review (DevOps Essence-audit + User, 2026-06-16) found and CLOSED real gaps pre-freeze (cut-independent):** contract clauses **C2/C4 were specified-but-unenforced (RC1) → now live in the hook (#133)**; the **QA-gate `main()` exit-contract** was untested → pinned (#134, F2-6.1); **inbox schema/provenance/read-ordering** pinned (#132). **C5 detection deferred** (mtime unreliable → content/git-based design strand, OE-owned, non-blocking). The "seams we touch" sharpening still attaches after F0. **Pass = no untested load-bearing seam at the cut points; qa-review sign-off (spawned qa-review; real QA ratifies on wake).**
2. **First-pass contract audit** — *owner OE.* The contract set **is** the 2↔3 interface from the protection side. Bar (the "Schnur"): contract a seam **iff** central **and** a future semAIt-update could change it non-obviously (same bar as the memory-substrate contract — avoid Flut). **Pass = every load-bearing 2↔3 seam has a contract clause; OE sign-off.**
3. **Tested out-of-band backup/restore** — *mechanic DevOps (verified 2026-06-16); scope + integrity criterion OE (substrate is OE/shared domain).* Built in F2, **tested before F3**.
   - **Backup** (`scripts/substrate_backup.py`) → `$KLARTEXT_BACKUP_ROOT/<UTC-ISO-timestamp>/` (local external path; **fail-loud** if unset/unreachable). Contents: `~/.claude/klartext-team-memory/` (memory+inbox+`.read`) → `team-memory/`; `~/.claude` user-state (settings.json, skills/, plugin/MCP config; no caches) → `claude-user-state/`; **`.env` of all worktrees separately → `secrets/` mode 600, manifest-flagged confidential (never in plaintext logs)**; per-worktree WIP via `git stash create` → `git bundle` + untracked list → `wip/<worktree>/`; `manifest.json` (source paths, SHA256 per tree, worktree HEADs, timestamp).
   - **Restore** (`scripts/substrate_restore.py`) → into a **SANDBOX** (never over the live substrate during the test) → integrity via **OE's C4 index-integrity check** (now **live as `check_index_integrity`, #133**) against the sandbox copy.
   - **Gate flow:** Backup → sandbox-restore → **C4 green** → only THEN may F3 touch the live substrate. **Pass = C4 green on the restore** (an un-replayed backup is False Persistence).
   - *Bonus: a versioned out-of-band store also addresses the C5 versioning gap — keep lean, the safety net is primary.*

## 7. Rollback — two axes (mechanic verified, DevOps 2026-06-16)
- **Code:** before F3, an **annotated tag `pre-f3-<timestamp>`** on `main` + recorded branch HEADs → rollback via revert/reset.
- **Substrate:** on F3 failure, restore the live substrate from the §6.3 backup **using the procedure already verified in the sandbox**.
- **Ordering:** **substrate first** (critical, non-versioned), then code. Trigger = F3 lead (DevOps); restore **before** the next attempt. *git alone does not cover the non-versioned substrate — this axis is mandatory before F3 touches it.*

## 8. Open follow-ups (tracked, not blocking the cut)
- **ADR-0014 mechanic** — commit-msg hook + CI check for the `Agent: <slug>` trailer (DevOps Briefing per ADR-0014).
- **Package/plugin name** for the L3 distributable — at the Phase-2 trigger (first consumption / third-party), not now.
- **semAIt seed** — taken from the **post-cut** state (User decision); semAIt holds no diverged method today (clean seed).
- **Field Report channel** (klartext → semAIt evidence) — first draft is OE-domain; separate from this refactoring.

## 9. Freeze
This plan is **frozen** when: DevOps has verified §6/§7, OE and DevOps both sign off, and it is merged to `main`. **F0 starts only after the freeze.** Until then: planning only — no refactoring file is touched.

## 10. F3 execution log (DevOps-led; inbox FROZEN — coordination via this PR + user out-of-band)

> **F3 GO:** User (2026-06-16, relayed by OE — probe tested-valid, all worktrees clean, 0 WIP = ideal moment).
> **Channel freeze:** in effect from F3 start. No `inbox.sh` coordination during F3. Progress, gate points
> and verify evidence are recorded **here**; OE countersigns the F3-exit substrate checkpoint via the user.

### F3 preconditions — DONE (§7 both axes armed)
- **Substrate rollback net (retained):** `~/klartext-substrate-backups/2026-06-16T21-21-27Z/` (dir mode 700).
  Four-group §6.3 backup; **`verify_restore == []` → tested-valid** (G1 a∧b∧c · G2/G3 byte-identity · G4 ·
  manifest SHA256). 22 worktrees · 1 secret (`klartext/api/.env`, path only) · 22 wip entries (0 stash bundles —
  all worktrees tracked-clean). **This backup stays as the rollback net; cleanup only after F3 success.**
- **Code rollback anchor:** annotated tag **`pre-f3-2026-06-16T21-21-27Z`** → `main` `3e2a256`. Branch HEADs at
  F3 start: `main` `3e2a256` · `agent/devops` `fb1ffc1` · `agent/hannibal` `30692c6` ·
  `agent/system-architect` `f2e2942`. Rollback ordering: **substrate first, then code** (§7).

### F3 steps (sequence) — status
- [x] **#3b** skill-distribution isolation — **DONE** (#160 merged `58cb989`; all 12 skill executables →
  `docs/method/enactment/skills/`, generic defs stay in L3 cards; SA all-12→L2 + OE S2/S3 + OE closing
  countersign; the 5-stale-ref skill-body catch fixed in `439eaa5`; full sweep clean).
- [x] **#1b** semAIt seed — **DONE** (SA-ratified scope + mechanic; OE+user-confirmed location). It is a
  **COPY** (State A: klartext retains `docs/method/library/` in full, nothing moved out) via a **snapshot**,
  not filter-repo (ADR-0013 §History-separation sanctions snapshot for the one-time seed; `library/` had
  12 commits, no history of value). Seed at `/Users/thormar/klartext-method-seed/` (plain 29-file tree +
  single-commit `method-library.bundle` `f6865fc` + MANIFEST); verified: bundle reconstructs 29 files
  byte-identical. Code stems deferred/never (klartext enactment, not definitions); Direction-C plugin
  extraction is Phase-2. semAIt imports the artifact into its own repo (klartext↔semait isolation).
- [x] **#2** ADR-0014 provenance hook — **DONE** (#161 merged `8d47c46`). commit-msg hook (inject/validate)
  + `agent-provenance.yml` CI gate live; the gate caught + fixed its own merge-commit dogfood bug
  (`--no-merges`). 21 tests (incl. qa-review gap tests); SA ratified (faithful to ADR-0014), OE confirmed
  the agent-model. *ADR-0014 status `Proposed → Accepted` is SA's flip (rule owner).*

### F3 exit — ✅ COMPLETE (OE-countersigned 2026-06-17)
- Extraction verified (#1b) · provenance live (#2) · **substrate restored-and-verified — OE countersigned**
  (independently: live C4 clean / 47 index entries / 0 orphan; retained backup byte-faithful manifest +
  modes held; `pre-f3` tag stands).
- **Retained backup deleted** (cleartext `.env` cleanup obligation discharged; `~/klartext-substrate-backups/`
  removed, no leftover).
- **Inbox UNFREEZES** — coordination returns to the steady-state long-lived-session + inbox model (§2).
  Remaining steady-state restoration (not DevOps build work): semAIt seeds once from the artifact (semAIt's
  team); the asleep product-domain agents wake + `converge` on their next session.

**That closes F3 — and the whole F0 → F3 method/product separation.**
