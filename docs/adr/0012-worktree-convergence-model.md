# 0012 — Consistency Model for Agent Worktrees: Guarded Voluntary Convergence

**Status:** Accepted — direction decided, mechanism built separately by DevOps
**Decided by:** User (direction, 2026-06-14), in a design session with DevOps
**Author / Sign-off:** System Architect
**Extends:** ADR-0010 §4 (shared layer pinned) and §2 (worktree isolation).
**Consequence of:** [ADR-0011](0011-return-to-desktop-app-session-start.md) — the return to the desktop
app removed the implicit `git` auto-rebase that `scripts/start-agent.sh` performed on every terminal
start. That side effect was the only thing keeping the isolated worktrees in step with `main`.
**Mechanism:** DevOps builds `klartext converge` + the SessionStart drift signal in a separate PR that
**cites this ADR**. This record fixes the *policy*; it does not specify the implementation.

## Context

ADR-0010 §2 isolates each agent in its own worktree (`~/klartext-worktrees/<slug>/`) and §4 pins a
shared substrate on `main`: `settings.json`, hooks, allowlists, auto-memory pins, and the coding
standards in `CLAUDE.md`. Under the terminal operating model, `start-agent.sh` rebased each worktree on
start, so a change committed to the shared layer propagated into every worktree at its next session —
silently, as a launcher side effect.

ADR-0011 moved session start back into the desktop app, which has no such launcher step. **The implicit
propagation is gone.** A change to the shared substrate now lands on `main` and stays there; the
isolated worktrees do not see it until something pulls it in. The result is **drift**: worktrees running
against a stale copy of the shared standards, settings, and pins.

This is not hypothetical. The `autoMemoryDirectory` cutover demonstrated the cost directly — only 3 of
11 worktrees had the pin, and closing the gap required a hand-rollout tracked one worktree at a time.
The same friction recurs on **every** committed change to the shared layer. Left unaddressed, the
failure mode is **RC4-class**: agents act on decisions that have already been superseded on `main`,
without anyone noticing.

The question this ADR answers is therefore narrow and structural: **once the shared substrate changes on
`main`, how does it reach the isolated worktrees — and on whose initiative?**

## Decision

We adopt **guarded voluntary convergence**. The model is defined by its position on five axes. The axes
are the transferable asset; the position below is klartext's deliberate choice.

| Axis | Position | Why |
|---|---|---|
| **Direction** | **Pull**, not Push | The agent pulls on its own initiative. A push (someone rebasing a worktree from outside) reaches into a working directory the agent owns. |
| **Coercion** | **Consensus**, not Force | Convergence **never touches WIP** and **never auto-rebases feature branches**. It is an invitation, not a command. |
| **Consistency** | **Eventual**, not Strong | Worktrees are *allowed* to lag. Convergence is an explicit act, not a precondition for work. *(Refined by the [Addendum — Two-mode consistency](#addendum--two-mode-consistency-for-breaking-way-of-working-changes-2026-06-14): eventual by default, but a stop-the-world **barrier** for a change that is **breaking for a drifted agent**.)* |
| **Activation** | **Explicitly forced**, not implicitly emergent | A **named command** plus a **drift warning** — not a hidden launcher side effect as before. The mechanism is visible and owned. |
| **Convergence unit** | **Whole-branch** (`rebase origin/main`), not partial | Motivated by the shared layer: settings + hooks + allowlists + pins + standards form one coherent state. A partial pull would produce an incoherent mix. *(Point A.)* |

### Two convergence paths *(Point B — completeness)*

**Detection is universal** — the drift signal fires in *every* worktree regardless of which branch it is
on. **The action is branch-dependent:**

- **Home branch (`agent/<slug>`)** → `klartext converge` (rebase on `origin/main`).
- **Feature branch with an open PR** → manual rebase as part of the PR lifecycle. **The command never
  touches a feature branch** — that is the "never auto-rebase feature branches" guard, made concrete.

### Trigger discipline *(Point C)* and non-blocking guarantee *(Point D)*

Convergence is **expected when taking up new work**, prompted by the drift warning. It is **never
blocking**: a stale worktree can always start a session and do work. The warning informs; it does not
gate.

### Detection granularity is a swappable choice, not pinned here

This ADR names the **axis** of detection granularity but deliberately **does not pin the degree**. The
current degree lives in OE's **"Drift Awareness" Practice** (one Practice; see the method docs and
[ADR-0011] Open-Question lineage): it starts at **L1** (coarse commit-count) and may be promoted to
**L2** (shared-layer-weighted) on the basis of monitoring. Crucially, the mechanism is built **behind a
port** — `DriftSignal` with L1/L2 adapters — so a change of sharpness is an **adapter swap**, not a
change to this decision. L1→L2 is a new Improvement-Step instance owned by OE, not an amendment to this
ADR.

### Firing model *(mechanism detail — DevOps domain, recorded for traceability)*

- Drift warning fires at **SessionStart**, matcher **`startup | clear`** — **not** `compact` (a compact
  does not change the git state mid-session, so there is nothing new to converge to).
- Detection is **fail-soft and throttled**: a throttled `git fetch`; **offline → the session starts
  normally** and the warning falls back to the last known `origin/main` state.
- The same detection is available **on demand** via the CLI (`klartext converge --check`, and as a
  `health` signal).
- The SessionStart hook co-locates with the ADR-0011 **G2** local-mode check (both are
  startup-time, Local-environment invariants).

## Rejected Alternatives

| Alternative | Verdict | Reason |
|---|---|---|
| **Auto-rebase on start** (restore the old launcher side effect — Push / Force) | Rejected | Reaches into the worktree the agent owns: destroys or stashes WIP without consent, causes `index.lock` contention against a live session, and takes sovereignty away from the agent. The very coupling ADR-0010 §2 removed. |
| **Strong consistency — block work until the worktree is synced** | Rejected | Kills autonomy. An agent could not start working on a stale-but-fine worktree. Trades the whole point of isolation (independent progress) for a guarantee we do not need. |
| **Leave it implicit (status quo after ADR-0011)** | Rejected | Silent drift drives agents to act on superseded decisions — the RC4 "documented vs. actual" failure class. The cost was already paid once in the autoMemory cutover. |

## Consequences

**Positive**
- Convergence becomes a **visible, owned act** rather than an invisible launcher side effect — consistent
  with ADR-0011's move toward explicit, inspectable lifecycle mechanics.
- Future shared-substrate changes become a **one-liner** for each agent (`klartext converge`) instead of
  a hand-tracked rollout.
- Worktree isolation (ADR-0010 §2) is preserved intact: nothing reaches into a worktree from outside.

**Negative / Risks**
- Agents **must run `klartext converge`** to pick up shared changes; a worktree that never converges
  drifts indefinitely. Mitigated — not eliminated — by the drift warning at SessionStart.
- The non-blocking guarantee means a determined agent can ignore the warning. This is the deliberate
  price of "consensus, not force."

**Project-specific scope**
- The **axes** (direction / coercion / consistency / activation / convergence-unit) are the transferable
  method asset. The **position** klartext takes on them is this project's choice — another project, with
  different isolation or throughput needs, may legitimately choose differently on any axis.

## Naming

The command is **`klartext converge`** (conceptual name, chosen by the user — explicitly **not**
`worktree-sync`). The rename from the earlier working name `worktree-sync` is carried through the method
docs and the `anchor` skill by OE (PR #109 / Improvement Register #106), separately from this ADR.

## Addendum — Two-mode consistency for breaking way-of-working changes (2026-06-14)

**Status:** Accepted — **Decided by:** User (by practice, 2026-06-14) · **Author / Sign-off:** System
Architect · **Gate:** OE. **Trigger incident:** the **2026-06-14 anchor break** — a breaking
way-of-working change landed on `main` while some worktrees were still drifted; the `anchor` ritual a
drifted agent ran no longer matched the new state and broke **before** that agent ever converged.

### Why the base decision needs a refinement

The Decision sets the **Consistency** axis to *eventual* and rejects *strong consistency* as a standing
rule. That is correct for ordinary work. But eventual convergence has a hole for **breaking changes to
the way of working**: eventual consistency assumes the *old* state keeps working until an agent catches
up — which is exactly false for a breaking change. A drifted agent runs the now-broken ritual in the
window before it converges. The anchor break is that hole realised.

### Decision — refine the Consistency axis (scoped to way-of-working changes)

> **Consistency = eventual by default; strong / barrier when the change is breaking for a drifted agent.**

| Mode | When | Behaviour |
|---|---|---|
| **Rolling** *(default)* | Backward-compatible change — a drifted agent keeps running correctly and picks it up later | No global halt. Each agent converges on its own initiative at its next session — the base ADR-0012 path, unchanged. |
| **Barrier** *(stop-the-world)* | **Breaking** change — the old state breaks (anchored command / path / skill no longer matches) | All agents stabilise + pause, the change lands, all resync **and verify current** before resuming. |

**Trigger — classify every way-of-working change explicitly.** Each way-of-working PR answers one
question: *"Is this breaking for a **drifted** agent?"* — **no silent default** (recorded as a PR
label / checklist answer), and **uncertainty resolves to breaking** (fail-safe: a needless halt is
cheaper than breaking a drifted agent).

**Lever — expand–contract first.** Before classifying a change *breaking*, make it backward-compatible
where possible (e.g. keep the old command / path as an **alias** during a transition window, then
remove it). A change built this way is **Rolling**, not Barrier. This is the primary lever to keep the
barrier set small — the barrier is the exception, not the norm.

### Reconciliation with the base decision (this is not a reversal)

- **Scope.** This addendum governs **way-of-working / shared-substrate changes only** — skills, rituals,
  `settings.json` / hooks / allowlists, and the commands and paths they reference. **Product changes**
  (code, ADRs, domain docs — which advance the Software System, not the Way of Working) are **out of
  scope** and remain purely eventual.
- **The Barrier mode does not revive the rejected "Strong consistency — block work until synced"
  alternative.** That rejection stands: convergence is *not* a standing precondition for all work. The
  barrier is a **bounded, coordinated, land-time event** for a single breaking method change — declared,
  executed, and over. Outside a declared barrier, convergence stays voluntary and eventual, and the
  **non-blocking guarantee (Point D) is fully preserved** on the default rolling path.

### Procedure and mechanism live elsewhere — referenced, not duplicated

- **Procedure:** the rollout steps (Barrier = *Stabilise & Halt* (the `anchor` ritual) → *Update* incl.
  tooling bootstrap → *Resync & Verify current*) are owned by OE's Practice **Controlled Method Rollout**
  (`docs/superpowers/improvement/practices/controlled-method-rollout.md`, PR #115). This addendum records
  only the **decision**; the Practice carries the **how**.
- **Mechanism (DevOps):** the per-PR **classification gate** ("breaking?") and the
  **verify-current-before-resume** check — which is exactly the SessionStart **drift / G2** check (the
  detection half of *Drift Awareness*, Register #106). The convergence action remains `klartext converge`
  (base decision). Until those land, the barrier is run by hand, as it was on 2026-06-14.

### Consequences

- Closes the eventual-consistency hole for breaking method changes **without** giving up the cheap
  rolling default for everything else.
- **Cost:** a real classification step on every way-of-working PR, plus an occasional coordinated halt.
  Mitigated by expand–contract keeping most changes on the rolling path.
