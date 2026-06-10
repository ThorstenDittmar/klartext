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

## Practices — described (cards exist)

| Element | Advances Alpha | Enforcement | Card |
|---|---|---|---|
| Improvement Step | Way of Working | ritual | ✅ `practices/improvement-step.md` |
| Document Scoping | Way of Working | ritual | ✅ `practices/document-scoping.md` |
| Retrospective | Way of Working (tracks Improvement sub-alpha) | ritual | ✅ `practices/retrospective.md` |

## Practices — enacted as skills (cards pending)

Lived practices: each has an executable enactment (a Claude Code skill) but no description card yet — the
inverse of RC1 (*enforced-ish but not described* instead of *described but not enforced*).

| Element | Enacted as | Advances Alpha | Enforcement today | Card |
|---|---|---|---|---|
| TDD | `tdd` skill (wraps superpowers TDD) | Software System, Requirements | ritual + partly mechanical (CI test gate) | ❌ |
| QA Review | `qa-review` skill (called by `tdd` step 3) | Software System | ritual | ❌ |
| QA Retro | `qa-retro` skill (test-gap learning loop) | Way of Working, Software System | ritual | ❌ |
| Task Readiness | `task-readiness` skill | Work | ⚠️ **advisory — never invoked in H01 (T6/RC2)** | ❌ |
| Knowledge Routing | `knowledge-routing` skill | Team, Way of Working | ritual (anchored in pre-compact) | ❌ |
| Pre-Compact Capture | `pre-compact` skill | Way of Working | ritual (user-triggered) | ❌ |
| Frontend Verification | `verify` skill (QA owns criteria, UX/UI executes — four-eyes instance) | Software System | ritual | ❌ |
| Systematic Debugging | `systematic-debugging` skill | Software System | ritual | ❌ |
| Frontend Standards | `frontend` skill | Software System | ritual | ❌ |
| Agent Onboarding | `agent-onboarding` skill | Team | ritual | ❌ |

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
Compact log/digest (gitignored, local).

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
