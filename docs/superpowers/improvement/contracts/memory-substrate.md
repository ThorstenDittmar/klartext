# Dependency Contract: Memory Substrate

> **What this is.** A **Dependency Contract** — the **invariants our way of working requires from** the
> storage substrate it runs on. It is the *upstream* counterpart to Environment Knowledge's **dependency
> chain**: the dependency chain lists *what of ours breaks* if a fact changes (downstream blast radius); a
> Dependency Contract lists *what we require to hold* (the invariants). Complementary, not duplicate — each
> clause names its blast radius.
> **The substrate.** The durable team memory (`~/.claude/klartext-team-memory/`), the file inbox
> (`scripts/inbox.sh`), the `MEMORY.md` index, and the `autoMemoryDirectory` pin that makes the app resolve
> the shared path. Not "external" (we build `inbox.sh`, the layout, the convention) and not purely ours (the
> app's auto-memory resolution, `~/.claude` semantics, the filesystem) — a **seam**.
> **Language.** English — documentation-language rule.
>
> **Status:** draft v1 (2026-06-14) · **Owner:** OE (contract form + clauses) · DevOps (mechanization +
> empirical content) · **Advances Alpha:** Way of Working
> **Source check:** new lean element **Dependency Contract**, KB-confirmed distinct from the existing
> *dependency chain* (Environment Knowledge). No Kernel change — an artifact type alongside Work Products.

## The seam — three parts

| Face | What | Modeled as | Owner |
|---|---|---|---|
| **Uncontrolled** (external-like) | app `autoMemory` resolution (pin honored? per-cwd default? trust), `~/.claude` semantics, filesystem | **Environment Knowledge** work product (version-bound + **Canary**) — lifts the existing empirical finding `reference_automemory_scope_behavior` into the repo | DevOps (empirical, four-eyes) |
| **Controlled** (our artifact) | `inbox.sh`, directory layout, `MEMORY.md` convention, committed pin | our **IaC + health-check** (we change it deliberately — no Canary needed) | DevOps (mechanism) + OE (conventions) |
| **The seam** | the invariants below — *whichever* side provides them | **this Dependency Contract** | OE |

## The contract — invariants

Each clause states what must hold, its **blast radius** if violated, and its **check** (the mechanization
that makes it falsifiable — a substrate health-check, DevOps, co-located with the ADR-0011 **G2** local-mode
check).

| # | Invariant | Blast radius if violated | Check | Holds today? |
|---|---|---|---|---|
| **C1** | The team memory resolves to the **same shared path for every agent**, independent of worktree/cwd (committed `autoMemoryDirectory`). | Agents read/write *different* memories → divergent truth (the autoMemory cutover pain). | Health-check asserts the resolved memory path == the committed shared path. | ✅ (after the pin rollout) |
| **C2** | The substrate is **durable across sessions and session-types** (terminal *and* app). | Knowledge meant to outlive a session is lost on restart/clear → False-Persistence class. | Health-check asserts the dir exists + is writable from this session type. | ✅ |
| **C3** | The inbox is **readable/writable by every session at a git-worktree-independent path**. | Cross-agent messages land where the recipient cannot see them (the #108 / mis-address class). | Health-check asserts `inbox.sh` base resolves outside the worktree and is reachable. | ✅ |
| **C4** | **Concurrent writes** (e.g. parallel memory consolidation) corrupt neither the `MEMORY.md` index nor any inbox message. | Lost/garbled memories or index under simultaneous agent activity. | *(to define with the check)* | ⚠️ **OPEN — not yet guaranteed** |

**C4 is an explicit open decision, not an assumption.** Surfaced 2026-06-14 when multiple agents consolidated
the shared memory simultaneously; no corruption was observed, but nothing *guarantees* it. Naming it as a
contract clause turns a hope into a decision: either prove/limit concurrency is safe, or add a guard
(lock / append-only / single-writer convention). To be decided as its own Improvement Step.

## Why a contract (the lever the seam gives us)

Because we **own** the inner face, the contract reveals **design levers**, not just risk to watch: with the
Claude app or GitHub we can only observe + Canary; here we can *build* the substrate to satisfy the contract
(make the inbox concurrency-safe, keep the pin path absolute + committed). A violation on **either** side is
checked against the **same** contract — so "what changed under us" and "what we changed" are caught by one set
of invariants.

## Relationship to other elements

- **Environment Knowledge** (`practices/environment-knowledge.md`) — provides the uncontrolled-face work
  product + Canary; the contract's external clauses reference it.
- **Controlled Method Rollout** (`practices/controlled-method-rollout.md`) — a change that violates a contract
  clause for a *drifted* agent is **breaking** → barrier mode. The contract feeds that classification.
- **Drift Awareness** (register #106) / **ADR-0012** — convergence keeps a worktree's *copy* of the substrate
  current; the contract states what the substrate must guarantee in the first place.

## Open

- **C4 concurrency** — decide the guarantee + its guard (own Improvement Step).
- Lift `reference_automemory_scope_behavior` into an Environment Knowledge work product (DevOps, four-eyes).
- Build the substrate health-check asserting C1–C3 now, C4 once decided (DevOps, co-located with G2).
