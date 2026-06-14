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
| **Uncontrolled** (external-like) | app `autoMemory` resolution (pin honored? per-cwd default? trust), `~/.claude` semantics, filesystem | **Environment Knowledge** work product (version-bound + **Canary**) — **already in the repo**: the autoMemory resolution lives in `environment/claude-code-app.md` (v2, #99/#103); same Resource = the app, so no separate card | DevOps (empirical, four-eyes) |
| **Controlled** (our artifact) | `inbox.sh`, directory layout, `MEMORY.md` convention, committed pin | our **IaC + health-check** (we change it deliberately — no Canary needed) | DevOps (mechanism) + OE (conventions) |
| **The seam** | the invariants below — *whichever* side provides them | **this Dependency Contract** | OE |

## The contract — invariants

Each clause states what must hold, its **blast radius** if violated, and its **check** (the mechanization
that makes it falsifiable — a substrate health-check, DevOps, co-located with the ADR-0011 **G2** local-mode
check).

| # | Invariant | Blast radius if violated | Check | Holds today? |
|---|---|---|---|---|
| **C1** | The team memory resolves to the **same shared path for every agent**, independent of worktree/cwd (committed `autoMemoryDirectory`). | Agents read/write *different* memories → divergent truth (the autoMemory cutover pain). | Health-check asserts the resolved memory path == the committed shared path — **live in the session-health hook (#117)**. | ✅ (after the pin rollout) |
| **C2** | The substrate is **durable across sessions and session-types** (terminal *and* app). | Knowledge meant to outlive a session is lost on restart/clear → False-Persistence class. | Health-check asserts the dir exists + is writable from this session type. | ✅ |
| **C3** | The inbox is **readable/writable by every session at a git-worktree-independent path**. | Cross-agent messages land where the recipient cannot see them (the #108 / mis-address class). | Health-check asserts `inbox.sh` base resolves outside the worktree and is reachable — **live in the session-health hook (#117)**. | ✅ |
| **C4** | **Concurrent writes** (e.g. parallel memory consolidation) corrupt neither the `MEMORY.md` index nor any inbox message. | Lost/garbled memories or index under simultaneous agent activity. | Index-integrity assertion (every `MEMORY.md` entry → a real file; no duplicate entries) in the health-check. | ✅ **Decided (lean), 2026-06-14 — see below** |

**C4 — Decided (lean: eventual + reconcile), 2026-06-14 (user, by practice).** The exposure is **narrow**:
per-fact files are **single-owner** (distinct files → no collision) and inbox messages are **one file each
with a unique timestamp+slug name** (no collision). The *only* shared hot file is **`MEMORY.md`** (the index).
Guarantee: *no lost or garbled memory under normal concurrent operation* — held by a **convention + reconciler**,
not a lock:

- **Fact files stay single-owner** — never concurrently co-edited; a cross-owner change is routed via OE
  (`knowledge-routing`), not edited in place.
- **`MEMORY.md`** — each agent **appends its own one-line entry**; OE's **`consolidate-memory`** pass is the
  reconciler/structural writer, and the **index-integrity check** (every entry → a real file, no duplicates —
  exactly the check OE ran on 2026-06-14) catches and surfaces any rare clobber for repair.

A hard guard (lock / single-writer index) was **considered and rejected** as disproportionate for a
rarely-written index whose only observed concurrency (parallel consolidation, 2026-06-14) produced no
corruption. If the index-integrity check ever *does* trip in practice, that is the falsifiable signal to
revisit (a new Improvement Step) — the lean stance is itself monitored.

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

## Status & open

- **C1, C3** — ✅ live in the session-health hook (#117).
- **C2** (durability) — holds; its explicit hook assertion is still pending (DevOps, fold into the hook).
- **C4** — ✅ **decided lean (2026-06-14)**; its check = the **index-integrity assertion** (every entry → a real
  file, no duplicates), to be added to the hook (DevOps).
- Uncontrolled face (autoMemory resolution) — ✅ already an Environment Knowledge work product
  (`environment/claude-code-app.md`, v2); no separate card.
- **Monitor (OE):** if the index-integrity check ever trips in practice, revisit the lean stance (new
  Improvement Step).
