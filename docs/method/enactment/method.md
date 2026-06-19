# The klartext Method

This is klartext's **Method-composition object** (L2). F0.2 completes it (composed Library practices + lived Alpha states).

> **What this document *is* (composition statement).** This register **is** klartext's instance of the Essence
> **Method** element — *the composition of the kernel and a set of practices for a specific purpose*. Concretely:
> the **Library practices** (the reusable L3 cards under `../library/practices/`, `../library/patterns/`,
> `../library/dependency-contract.md`, `../library/adr-mechanism.md`, `../library/standards-charter.md`, `../library/resources/`) **composed** into our way of working and shown
> here **with their lived Alpha states** (which Alpha each advances, enforcement, NN, and — for the practices we
> have actually run — their validated lifecycle). Each row links the **L3 definition** (reusable card) and, where
> one exists, the **L2 instance** (our enacted sibling under `practices/`). F0.1 produced the cards; F0.2-P-F
> closes the register so every composed element resolves to a card. Path convention: bare `practices/…` /
> `contracts/…` paths are L2 (this `enactment/` tree); `../library/…` paths are L3.

> **Scope.** The **composition of our way of working**: the authoritative register of the elements — Practices,
> Patterns, Work Products, gates, roles — that make up the klartext method, each with its Essence type, the
> Alpha it advances, enforcement level and card status. This is our instance of the Essence **Method** element
> ("the composition of a kernel and a set of practices to fulfill a specific purpose").
> **Out of scope.** Practice *content* (lives in `practices/` — our **Practice Library**); the meta-language
> reference (`semat-definition.md`); term definitions (`semat-glossary.md`); decisions and rationale
> (`continuous-improvement.md`).
> **Anti-pattern guarded.** Implicit/unlisted method elements — completeness that cannot be checked (RC1;
> cf. the Community-omission incident: no list meant no completeness check).
> **Language.** English — documentation-language rule.
>
> **Owner:** OE · **Status:** living · **Maintenance ritual:** updated in the same Improvement Step (step 3,
> Record) that adds, changes, promotes or retires an element.
> The **Card** column doubles as the migration diagnostic — the only *temporary* aspect of this document:
> ❌ entries are *enacted* (lived, often as a skill) but not yet *described* in our meta-language.

> **Non-negotiable (NN) flag** *(added 2026-06-10, closes the last Foundation-Established checkbox)*:
> ✓ = must run whenever its trigger condition applies; skipping requires a **recorded deviation** (cf. the
> retro deviation clause). — = strong convention, context may override without a record. All mechanical
> gates are non-negotiable by nature.

> **Retirement rule** *(added 2026-06-10, user-requested)*: elements are **never deleted** from this
> register. When an element is abandoned or replaced, its row gets status **`retired`** or
> **`superseded by <element>`** plus a one-line rationale (and a pointer to the Improvement-Register row
> or ADR carrying the full why). Modeled on the ADR supersession mechanism. Decisions *against* a way of
> working are method knowledge of equal rank to decisions *for* one — they must survive compactions and
> generation changes.

## Practices — composed (all carded)

Every composed practice now resolves to an **L3 definition card** (`../library/practices/`) and, where we enact
it as our own sibling, an **L2 instance** (`practices/`). The migration diagnostic that this column used to
carry (the ❌ "enacted but not described" backlog) is **closed by F0.2** — the table below merges the formerly
two-part split into one register. Several of these are *enacted as Claude Code skills*; the skill is the
executable L2 enactment, the card is the L3 description.

| Element | Advances Alpha | Enforcement | NN | Card (L3 def · L2 instance) |
|---|---|---|---|---|
| Improvement Step | Way of Working | ritual | ✓ | ✅ `../library/practices/improvement-step.md` · `practices/improvement-step.md` |
| Document Scoping | Way of Working | ritual | — | ✅ `../library/practices/document-scoping.md` · `practices/document-scoping.md` |
| Retrospective | Way of Working (tracks Improvement sub-alpha) | ritual | ✓ (Work cannot reach *Closed* without it) | ✅ `../library/practices/retrospective.md` · `practices/retrospective.md` |
| Merge Protocol | Work | ritual | ✓ (for parallel dispatches) | ✅ `../library/practices/merge-protocol.md` · `practices/merge-protocol.md` |
| Environment Knowledge | Way of Working | ritual (manual canary — flagship Resource not scriptable) | ✓ (before an env-fact-dependent decision; after a tool update) | ✅ `../library/practices/environment-knowledge.md` · `practices/environment-knowledge.md` |
| Controlled Method Rollout | Way of Working | ritual (classification gate + drift/G2 verify = mechanical promotions, DevOps) | ✓ (every way-of-working change: classify breaking-for-a-drifted-agent → rolling default / barrier for breaking) | ✅ `../library/practices/controlled-method-rollout.md` · `practices/controlled-method-rollout.md` |
| TDD (enacted as `tdd` skill, wraps superpowers TDD) | Software System, Requirements | ritual + partly mechanical (CI test gate) | ✓ | ✅ `../library/practices/tdd.md` · `practices/tdd.md` |
| QA Review (enacted as `qa-review` skill, called by `tdd` step 3) | Software System | ritual | ✓ | ✅ `../library/practices/qa-review.md` · `practices/qa-review.md` |
| QA Retro (enacted as `qa-retro` skill, test-gap learning loop) | Way of Working, Software System | ritual | ✓ (when triggered) | ✅ `../library/practices/qa-retro.md` · `practices/qa-retro.md` |
| Task Readiness (enacted as `task-readiness` skill) | Work | ritual — **validated H01-422: invoked 3/3 dispatches** (drained to `main` PR #52) | ✓ | ✅ `../library/practices/task-readiness.md` · `practices/task-readiness.md` |
| Knowledge Routing (enacted as `knowledge-routing` skill) | Team, Way of Working | ritual (runs within the anchor ritual) | ✓ | ✅ `../library/practices/knowledge-routing.md` · `practices/knowledge-routing.md` |
| Anchor — session safeguard (formerly *Pre-Compact Capture*; renamed 2026-06-13 — no longer tied to /compact, the loss-free path is /clear; +conditional successor-seed step; enacted as `anchor` skill) | Way of Working | ritual (user-triggered) | ✓ (North Star: no insight lost) | ✅ `../library/practices/anchor.md` · `practices/anchor.md` |
| Systematic Debugging (enacted as `systematic-debugging` skill) | Software System | ritual | — | ✅ `../library/practices/systematic-debugging.md` · `practices/systematic-debugging.md` |
| Agent Onboarding (enacted as `agent-onboarding` skill) | Team | ritual | ✓ (when adding an agent) | ✅ `../library/practices/agent-onboarding.md` (L3 only — OE-owned, no separate L2 sibling) |
| Project Onboarding (stand up an endeavour's operating system from the method seed) | Way of Working | ritual | ✓ (when standing up a new endeavour) | ✅ `../library/practices/project-onboarding.md` (L3 only — generic; no L2 sibling, the seed is klartext's export) |
| Frontend Verification (enacted as `verify` skill; QA owns criteria, UX/UI executes — four-eyes instance) | Software System | ritual | ✓ (for UI changes) | ✅ `practices/verify.md` (wholly-L2 instance) |
| Frontend Standards (enacted as `frontend` skill) | Software System | ritual | — | ✅ `practices/frontend.md` (wholly-L2 instance) |
| Frontend Testing (QA-owned; frontend test criteria — flagged missing in F0.2-P-D) | Software System | ritual | ✓ (for UI changes) | ✅ `practices/frontend-testing.md` (wholly-L2 instance) |

## Patterns — named structures

Eight are now **carded** under `../library/patterns/`; the rest stay **prose, not carded (lean)** — they live in
`CLAUDE.md` / `continuous-improvement.md` and don't yet warrant their own card. Note: **Naht-Check** and
**E2E-before-done** are Essence type **Activity** (gates), not Pattern — kept in this table by origin (element-sweep)
but typed correctly.

| Element | Essence type | Card / where it lives | Enforcement |
|---|---|---|---|
| Four-Eyes Principle (executor / criteria-owner pair) | Pattern | ✅ `../library/patterns/four-eyes.md` | ritual |
| KB-First Lookup (SEMAT/method questions: own reference first, web on miss, backfill gaps in the same step) | Pattern | ✅ `../library/patterns/kb-first-lookup.md` | ritual |
| Method Keeper (OE owns the method; locates way-of-working topics in Essence terms before solutioning) | Pattern (role) | ✅ `../library/patterns/method-keeper.md` | ritual |
| Memory Park / Custody (out-of-tree redundancy for at-risk knowledge: park verbatim in auto-memory with restore condition + delete-after-verification; applied 3× on 2026-06-10, bridged two data-loss incidents) | Pattern | ✅ `../library/patterns/memory-park.md` | ritual |
| Blocker Protocol (on an unlocatable/blocked step: STOP → classify in Essence/RC terms → escalate to the owner — never improvise; first run: Hannibal B2, 2026-06-10) | Pattern | ✅ `../library/patterns/blocker-protocol.md` | ritual |
| Agent Provenance (every agent self-stamps its work — commit trailer / file header — so authorship survives compaction; C5 substrate clause) | Pattern | ✅ `../library/patterns/agent-provenance.md` | ritual (mechanical detection deferred — see Dependency Contracts C5) |
| Naht-Check (every PR verified to contain exactly the intended files, nothing else; DevOps, every increment since #45) | **Activity** (gate) | ✅ `../library/patterns/naht-check.md` | ritual |
| E2E-before-done (A2 gate: end-to-end verification on the live system *before* merge, evidence captured; first run H01-422) | **Activity** (gate) | ✅ `../library/patterns/e2e-before-done.md` | ritual |
| Domain Respect | Pattern | prose (`CLAUDE.md` § Agent Roles), not carded (lean) | ritual |
| Infrastructure Perimeter | Pattern | prose (`CLAUDE.md`), not carded (lean) | ritual |
| Salvage Branch Policy | Pattern | prose (`continuous-improvement.md`), not carded (lean) | ritual |
| Enforcement Hierarchy | Pattern (cross-cutting principle) | prose (`continuous-improvement.md` §1), not carded (lean) | ritual |
| Role Description | Pattern | prose (`job-description` skill), not carded (lean) | — |
| Salvage Triage (a/b) (per quarantined file: (a) belongs in repo → commit to main; (b) machine-local → gitignore/outside; freeze → tag/bundle, never a branch in the shared tree) | Activity | prose (`continuous-improvement.md` drain warnings), not carded (lean) | ritual |

## Competencies (kernel extension)

| Element | Levels (Essence) | Purpose |
|---|---|---|
| **Method Literacy** — the ability to locate way-of-working topics in Essence terms (element type, Alpha) and to use the method document set | 1 *Assists* … 5 *Innovates* | Target for agent onboarding and the team refresh: every agent reaches at least level 2 (*Applies*). Referenced by practice cards: the Retrospective requires ≥ 2 for the leader (via the Method Keeper pattern), ≥ 1 for participants. |

## Mechanical gates (activities / checks)

Our strongest enforcement points — mechanical by design: branch protection on `main` (6 required CI checks,
strict) · CI workflows (lint, tests, QA, integration) · Semgrep rules (`.semgrep/`) · tach layer boundaries ·
pre-commit hooks · infrastructure tests · health-endpoint tests · PostCompact/PreCompact audit hooks + compact
monitor (launchd).

## Work Products in circulation

Specs (`docs/superpowers/specs/`) · Plans (`docs/superpowers/plans/`) · `PENDING.md` (delegation tracking) ·
ADRs (`docs/adr/`) · QA learnings (`docs/superpowers/qa-learnings/`) · Practice cards (`practices/`) · Method
docs (this set) · Agent knowledge files (`agents/*/claude.md`) + start scripts · Knowledge briefings & DevOps
briefings (formats defined, **no declared home — RC1 candidates**) · Sign-offs (**unresolved H01 pain point**) ·
Compact log/digest (gitignored, local) · **Friction Reports** (capture-validation output; element-sweep find
retro 2 — no declared home yet, currently routed via custody depots) · Retro records (`learnings/`) ·
**Team Roster** (`agents/team.yaml`, added 2026-06-12) — advances the **Team** alpha; owner OE; maintenance
ritual: updated in the same step as the event that changes it (onboarding/offboarding/migration); stores only
non-derivable facts (status app|terminal, active flag, display name) — existence and worktree state stay
derivable from `agents/*/` and `git worktree list` (RC4 guard: no second truth); consumers: launcher/start
tooling (DevOps mechanics).

**Environment Work Products** (`docs/method/enactment/environment/`) — our **version-bound, falsifiable**
knowledge about the tools we *use* (Claude Code app/CLI, git, Supabase, macOS); produced by the **Environment
Knowledge** practice. Each carries version-binding + a manual **Canary** + a **dependency chain** + status tags
(tested / observed-untested / inferred / superseded). First instance: `claude-code-app.md` (v1.12603.1). Owner
OE (form + home); empirical content four-eyes-verified by the testing agent (DevOps). Distinct from **Resources**
below (which we *reference*, not *produce*).

**Dependency Contracts** — the **invariants our way of working requires from** a central IT component we depend
on (the *upstream* counterpart to a **dependency chain**, which lists the downstream blast radius). Each clause
carries its blast radius + a falsifiable check. New lean element (2026-06-14), KB-confirmed distinct from the
dependency chain. Owner OE (form + clauses); mechanization + empirical content four-eyes (DevOps). Bind only
**central** functionality this way — *Flut vermeiden*.
- **L3 element definition** (the generic Dependency-Contract element): ✅ `../library/dependency-contract.md`.
- **L2 instances** (our actual contracts): ✅ `contracts/memory-substrate.md` (team memory + inbox + pin substrate;
  C1–C5 specified — C1/C3 live #117, **C2/C4 live #133**, C5 provenance = self-stamp *ritual*; mechanical
  detection deferred: mtime unreliable → content/git-based design strand, OE-owned) · ✅ `contracts/superpowers.md`
  (the superpowers skill framework we build our skills on).

**Resources** (referenced, **never vendored/produced** — Essence element): external reference assets we depend on
but keep outside the tree; licensed-asset home `assets-local/` (gitignored; README = provenance register,
convention in `setup.sh`). The reusable L3 register lives at `../library/resources/`.
- ✅ **superpowers** — `../library/resources/superpowers.md` (the skill framework; basis of `tdd`, `qa-review`,
  `systematic-debugging`, the `verify`/`frontend` skills, and the anchor/brainstorming/plan rituals).
- **IJI *Agile Retrospective Essentials*** — referenced by `../library/practices/retrospective.md` (the
  Retrospective practice is *composed* from it, CC BY 4.0; the Improvement sub-alpha is adopted from it).
- **Parallel Change / expand–contract (Martin Fowler)** — referenced by
  `../library/practices/controlled-method-rollout.md` (adopted pattern, not invented).
- **Essence Kernel / Language (OMG/SEMAT)** — referenced by `../library/alpha-states.md` and
  `../library/semat-definition.md` (the meta-language and the Alpha State Cards we use as the inspection grid).

> This list is the **seed of the Artifact Register** (Phase 2 instrument candidate, see
> `continuous-improvement.md`).

## Roles / Team

The ten agents are instances of the **Team Alpha**; the role SSOT is `CLAUDE.md` § Agent Roles. Hannibal's
coordination fills the kernel activity space *Coordinate Activity*. A maintained **team roster** is decided as
the Artifact-Register pilot (Phase 2).

## Practice-defined Alphas (extensions)

| Element | States | Defined by |
|---|---|---|
| **Improvement** — a possible adaptation to improve the team's Way of Working | Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use | `practices/retrospective.md` (adopted from IJI Agile Retrospective Essentials); instances tracked in the Improvement Register (`continuous-improvement.md` §3) |

## Known gaps (migration diagnostic — temporary)

- ~~Retro practice has no card~~ — **closed 2026-06-10** (`../library/practices/retrospective.md`).
- ~~Process-learnings home missing~~ — **closed 2026-06-10** (`learnings/`).
- ~~Practices enacted-as-skills with no description card (the ❌ backlog: TDD, QA Review, QA Retro, Task
  Readiness, Knowledge Routing, Anchor, Frontend Verification, Systematic Debugging, Frontend Standards, Agent
  Onboarding)~~ — **closed 2026-06-16 by F0.2** (all carded; see *Practices — composed*). The patterns backlog
  (four-eyes, memory-park, blocker-protocol, naht-check, e2e-before-done, kb-first-lookup, method-keeper,
  agent-provenance) is **closed** in the same step.
- ~~Frontend test criteria missing as a distinct practice~~ — **closed 2026-06-16** (Frontend Testing row added,
  `practices/frontend-testing.md`; flagged by QA in F0.2-P-D).
- **Walking Skeleton practice** — planned, no card yet. *(still open)*
- **`task-readiness` is advisory** — the only H01-grade enforcement hole still open in the skill set (T6/RC2).
  *(still open — carding it did not change enforcement level)*
- **Briefings / sign-offs without declared homes** — RC1 candidates → Artifact Register (Phase 2). *(still open)*
