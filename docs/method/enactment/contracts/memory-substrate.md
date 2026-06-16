# Dependency Contract (instance): Memory Substrate

> **What this is.** The klartext-specific **Dependency Contract** for the storage substrate our way of
> working runs on — the concrete clauses C1–C5 below. For *what a Dependency Contract is* (the generic
> element: when to forge one, the clause / blast-radius / falsifiable-check structure, the relation to
> Environment Knowledge's dependency chain), see the L3 element card:
> [`../../library/dependency-contract.md`](../../library/dependency-contract.md).
> **The substrate.** The durable team memory (`~/.claude/klartext-team-memory/`), the file inbox
> (`scripts/inbox.sh`), the `MEMORY.md` index, and the `autoMemoryDirectory` pin that makes the app resolve
> the shared path. Not "external" (we build `inbox.sh`, the layout, the convention) and not purely ours (the
> app's auto-memory resolution, `~/.claude` semantics, the filesystem) — a **seam**.
> **Language.** English — documentation-language rule.
>
> **Status:** draft v1 (2026-06-14) · **Owner:** OE (contract form + clauses) · DevOps (mechanization +
> empirical content) · **Advances Alpha:** Way of Working

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
| **C2** | The substrate is **durable across sessions and session-types** (terminal *and* app). | Knowledge meant to outlive a session is lost on restart/clear → False-Persistence class. | `check_durable` asserts the dir exists + is writable — **live in the session-health hook (#133)**. | ✅ |
| **C3** | The inbox is **readable/writable by every session at a git-worktree-independent path**. | Cross-agent messages land where the recipient cannot see them (the #108 / mis-address class). | Health-check asserts `inbox.sh` base resolves outside the worktree and is reachable — **live in the session-health hook (#117)**. | ✅ |
| **C4** | **Concurrent writes** (e.g. parallel memory consolidation) corrupt neither the `MEMORY.md` index nor any inbox message. | Lost/garbled memories or index under simultaneous agent activity. | `check_index_integrity` (every `MEMORY.md` entry → a real file; no duplicate entries) — **live in the session-health hook (#133)**. | ✅ **Decided (lean), 2026-06-14 — live #133** |
| **C5** | **Every memory edit is attributable** — who last changed a memory file is recoverable. | Unattributable shared state: 11 agents + the user write the same memory under one OS/git identity → "who wrote this?" is unanswerable (surfaced 2026-06-15). | **Detection DEFERRED** — the `mtime`-based check is unreliable (mtime advances on non-content ops → false positives); needs a content/git-based design. The **self-stamp ritual stands**. | ⚠️ **Ritual decided 2026-06-15; mechanical detection deferred (own strand)** |

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

**C5 — Decided (lean self-stamp), 2026-06-15 (user, by practice).** Trigger: an edit to
`project_automemory_migration_status.md` could not be attributed — OE wrongly guessed "the user". Root
cause is structural: the team memory is **not version-controlled** (no author, only `mtime`) **and** all 11
agents + the user commit/write under one shared identity (`ThorstenDittmar`), so neither the filesystem nor
git can say *who*. Decision: a **self-stamp convention** — every agent that writes a memory file stamps its
own slug in the frontmatter `metadata`:

```yaml
metadata:
  last-edited-by: <agent-slug>      # e.g. oe, devops, audit
  last-edited-at: <YYYY-MM-DD>
```

This builds on the existing `originSessionId` (which records *origin*, not *edits*). It gives the **last
editor** — exactly the question that arose. **Rejected as disproportionate (for now):** version-controlling
the whole memory dir — heavier, and the shared git identity means it still would not attribute to an agent
without the stamp anyway. **Enforcement is honest about its limit:** memory is not in CI and the
memory-*writing* behaviour is driven by the system prompt (not an OE-editable surface), so the stamp is a
**ritual** (Enforcement Hierarchy level 2). The convention is surfaced to all agents via
`knowledge-routing.md` (loaded at every anchor). Ties to the open shared-blackboard ownership question
(`continuous-improvement.md`, the cwd-shared-auto-memory row).

**Mechanical detection DEFERRED (2026-06-16, own strand).** The originally-named check ("warn on a memory
file whose `mtime` advanced without a matching stamp") is **unreliable**: in practice `mtime` advances on
**non-content operations** (converge/checkout/sync/backup-restore) → false positives (DevOps, Essence-audit
finding). The detection therefore needs a **content/git-based design** (e.g. *content changed without a stamp
update*), not `mtime`. **The self-stamp ritual is unaffected and stands.** This is an OE-owned design strand
(OE substrate + DevOps mechanic), non-blocking.

## Why a contract here (the lever this seam gives us)

Because we **own** the inner face, the contract reveals **design levers**, not just risk to watch: with the
Claude app or GitHub we can only observe + Canary; here we can *build* the substrate to satisfy the contract
(make the inbox concurrency-safe, keep the pin path absolute + committed). A violation on **either** side is
checked against the **same** contract — so "what changed under us" and "what we changed" are caught by one set
of invariants. (The generic form of this lever is in the L3 element card.)

## Relationship to other elements

- **Dependency Contract (L3 element)** (`../../library/dependency-contract.md`) — the generic definition this
  file is an instance of.
- **Environment Knowledge** — provides the uncontrolled-face work product + Canary; the contract's external
  clauses reference it (`environment/claude-code-app.md`).
- **Controlled Method Rollout** — a change that violates a contract clause for a *drifted* agent is
  **breaking** → barrier mode. The contract feeds that classification.
- **Drift Awareness** (register #106) / **ADR-0012** — convergence keeps a worktree's *copy* of the substrate
  current; the contract states what the substrate must guarantee in the first place.

## Status & open

- **C1, C3** — ✅ live in the session-health hook (#117).
- **C2** (durability) — ✅ `check_durable` **live in the session-health hook (#133)**.
- **C4** (index-integrity) — ✅ `check_index_integrity` **live in the session-health hook (#133)** (decided lean 2026-06-14). Double-benefit: this is also the **restore-integrity criterion** for the Frozen-Plan §6.3 backup gate.
- **C5** (provenance) — self-stamp **ritual** stands; **mechanical detection deferred** (mtime unreliable → own content/git-based design strand, OE-owned).
- Uncontrolled face (autoMemory resolution) — ✅ already an Environment Knowledge work product
  (`environment/claude-code-app.md`, v2); no separate card.
- **Monitor (OE):** if the index-integrity check ever trips in practice, revisit the lean stance (new
  Improvement Step).
