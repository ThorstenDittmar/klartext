# The klartext Method

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

## Practices — described (cards exist)

| Element | Advances Alpha | Enforcement | NN | Card |
|---|---|---|---|---|
| Improvement Step | Way of Working | ritual | ✓ | ✅ `practices/improvement-step.md` |
| Document Scoping | Way of Working | ritual | — | ✅ `practices/document-scoping.md` |
| Retrospective | Way of Working (tracks Improvement sub-alpha) | ritual | ✓ (Work cannot reach *Closed* without it) | ✅ `practices/retrospective.md` |
| Merge Protocol | Work | ritual | ✓ (for parallel dispatches) | ✅ `practices/merge-protocol.md` |
| Environment Knowledge | Way of Working | ritual (manual canary — flagship Resource not scriptable) | ✓ (before an env-fact-dependent decision; after a tool update) | ✅ `practices/environment-knowledge.md` |
| Controlled Method Rollout | Way of Working | ritual (classification gate + drift/G2 verify = mechanical promotions, DevOps) | ✓ (every way-of-working change: classify breaking-for-a-drifted-agent → rolling default / barrier for breaking) | ✅ `practices/controlled-method-rollout.md` |

## Practices — enacted as skills (cards pending)

Lived practices: each has an executable enactment (a Claude Code skill) but no description card yet — the
inverse of RC1 (*enforced-ish but not described* instead of *described but not enforced*).

| Element | Enacted as | Advances Alpha | Enforcement today | NN | Card |
|---|---|---|---|---|---|
| TDD | `tdd` skill (wraps superpowers TDD) | Software System, Requirements | ritual + partly mechanical (CI test gate) | ✓ | ❌ |
| QA Review | `qa-review` skill (called by `tdd` step 3) | Software System | ritual | ✓ | ❌ |
| QA Retro | `qa-retro` skill (test-gap learning loop) | Way of Working, Software System | ritual | ✓ (when triggered) | ❌ |
| Task Readiness | `task-readiness` skill | Work | ritual — **validated H01-422: invoked 3/3 dispatches** (drained to `main` PR #52) | ✓ | ❌ |
| Knowledge Routing | `knowledge-routing` skill | Team, Way of Working | ritual (runs within the anchor ritual) | ✓ | ❌ |
| Anchor — session safeguard (formerly *Pre-Compact Capture*; renamed 2026-06-13 — no longer tied to /compact, the loss-free path is /clear; +conditional successor-seed step) | `anchor` skill (`docs/superpowers/skills/anchor.md`) | Way of Working | ritual (user-triggered) | ✓ (North Star: no insight lost) | ❌ |
| Frontend Verification | `verify` skill (QA owns criteria, UX/UI executes — four-eyes instance) | Software System | ritual | ✓ (for UI changes) | ❌ |
| Systematic Debugging | `systematic-debugging` skill | Software System | ritual | — | ❌ |
| Frontend Standards | `frontend` skill | Software System | ritual | — | ❌ |
| Agent Onboarding | `agent-onboarding` skill | Team | ritual | ✓ (when adding an agent) | ❌ |

## Patterns — named structures (mostly prose, no cards)

| Element | Essence type | Where it lives today | Enforcement |
|---|---|---|---|
| Four-Eyes Principle (executor / criteria-owner pair) | Pattern | `CLAUDE.md`, `agents/oe/claude.md` (prose) | ritual |
| Domain Respect | Pattern | `CLAUDE.md` § Agent Roles | ritual |
| Infrastructure Perimeter | Pattern | `CLAUDE.md` | ritual |
| Salvage Branch Policy | Pattern | `continuous-improvement.md` | ritual |
| Enforcement Hierarchy | Pattern (cross-cutting principle) | `continuous-improvement.md` §1 | ritual |
| Role Description | Pattern | `job-description` skill | — |
| KB-First Lookup (SEMAT/method questions: own reference first, web on miss, backfill gaps in the same step) | Pattern | `semat-definition.md` §5 | ritual |
| Method Keeper (OE owns the method; locates way-of-working topics in Essence terms before solutioning) | Pattern (role) | `agents/oe/claude.md` | ritual |
| Memory Park / Custody (out-of-tree redundancy for at-risk knowledge: park verbatim in auto-memory with restore condition + delete-after-verification; applied 3× on 2026-06-10, bridged two data-loss incidents) | Pattern | element-sweep find (retro 2) — prose here, card pending | ritual |
| Blocker Protocol (on an unlocatable/blocked step: STOP → classify in Essence/RC terms → escalate to the owner — never improvise; first run: Hannibal B2, 2026-06-10) | Pattern | element-sweep find (retro 2) — prose here, card pending | ritual |
| Naht-Check (every PR verified to contain exactly the intended files, nothing else; DevOps, every increment since #45) | Activity (gate) | element-sweep find (retro 2) — enacted by DevOps, undescribed | ritual |
| E2E-before-done (A2 gate: end-to-end verification on the live system *before* merge, evidence captured; first run H01-422) | Activity (gate) | element-sweep find (retro 2) — enacted by Hannibal, undescribed | ritual |
| Salvage Triage (a/b) (per quarantined file: (a) belongs in repo → commit to main; (b) machine-local → gitignore/outside; freeze → tag/bundle, never a branch in the shared tree) | Activity | DevOps git analysis (2026-06-10) — defined in `continuous-improvement.md` drain warnings | ritual |

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

**Environment Work Products** (`docs/superpowers/improvement/environment/`) — our **version-bound, falsifiable**
knowledge about the tools we *use* (Claude Code app/CLI, git, Supabase, macOS); produced by the **Environment
Knowledge** practice. Each carries version-binding + a manual **Canary** + a **dependency chain** + status tags
(tested / observed-untested / inferred / superseded). First instance: `claude-code-app.md` (v1.12603.1). Owner
OE (form + home); empirical content four-eyes-verified by the testing agent (DevOps). Distinct from **Resources**
below (which we *reference*, not *produce*).

**Dependency Contracts** (`docs/superpowers/improvement/contracts/`) — the **invariants our way of working
requires from** a central IT component we depend on (the *upstream* counterpart to a **dependency chain**,
which lists the downstream blast radius). Each clause carries its blast radius + a falsifiable check. New lean
element (2026-06-14), KB-confirmed distinct from the dependency chain. Owner OE (form + clauses); mechanization
+ empirical content four-eyes (DevOps). First instance: `contracts/memory-substrate.md` (the team memory + inbox
+ pin substrate; C1–C4 specified — C1/C3 live in the session-health hook #117, C4 decided *lean* 2026-06-14).
Bind only **central** functionality this way — *Flut vermeiden*.

**Resources** (referenced, not produced — Essence element): external reference assets (licensed decks,
standards PDFs) · home `assets-local/` (gitignored; README = provenance register, convention in `setup.sh`).

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

- ~~Retro practice has no card~~ — **closed 2026-06-10** (`practices/retrospective.md`).
- ~~Process-learnings home missing~~ — **closed 2026-06-10** (`learnings/`).
- **Walking Skeleton practice** — planned, no card yet.
- **`task-readiness` is advisory** — the only H01-grade enforcement hole still open in the skill set (T6/RC2).
- **Briefings / sign-offs without declared homes** — RC1 candidates → Artifact Register (Phase 2).
