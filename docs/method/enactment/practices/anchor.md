# Anchor — klartext enactment

> **Scope.** klartext's enactment of the **Anchor** practice: the concrete durable homes a reset survives,
> the worktree/`converge` sync hint, the team-memory binding, and the relay used for routing.
> **Out of scope.** The generic definition, the mode split, the eight steps, the False-Persistence guard — see
> the L3 card. The classification of routed knowledge (`knowledge-routing` enactment); decisions and rationale
> (`../continuous-improvement.md`).
> **Anti-pattern guarded.** Context-loss of chat-only knowledge (RC2) and False Persistence — a summary
> claiming a write that never happened (RC4 variant, evidenced 2026-06-10).
> **Language.** English — documentation-language rule (the skill body is German; renamed from `pre-compact` 2026-06-13).
>
> **L3 definition:** [`../../library/practices/anchor.md`](../../library/practices/anchor.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working · **NN:** ✓ (no insight lost)

## klartext bindings

- **What survives a reset (the concrete homes).** The method document set across both stems: L2
  `docs/method/enactment/` (`continuous-improvement.md` incl. Improvement Register §3, `method.md`,
  `learnings/`, `environment/`) and L3 `docs/method/library/` (`semat-definition.md` / `semat-glossary.md`,
  `alpha-states.md`, `practices/`); plus `CLAUDE.md`, `docs/superpowers/plans/PENDING.md`,
  `assets-local/README.md`, memory files under `~/.claude/`, code/commits/issues, and the skill files.
- **Homes by content type (step 5).** Own Hoheitswissen → `agents/<name>/claude.md`; way-of-working
  decision + rationale → `continuous-improvement.md` (OE; others brief OE); process learning → `learnings/`;
  new/changed method element → a practice card + `method.md` in the **same step** (OE only); improvement
  candidate → the Improvement Register §3; parked finding → a named custody depot (Memory-Park pattern).
- **Write-access first.** Only choose a home this session may write per its `start.sh`; otherwise brief the
  owner rather than fail silently.
- **Delegation/finding check (step 1.5).** Coordination agents (OE, Hannibal) scan for outgoing delegations;
  domain agents for received tasks + outgoing findings. Open delegations are written **directly** to
  `PENDING.md` — the one exception to "user is the channel" (tracking, not domain knowledge).
- **Successor seed (restart).** `scripts/inbox.sh send <self> <self> "Successor-Seed: …"`; verify via
  `inbox.sh unread <self>`.
- **Worktree sync hint (restart, optional).** After a clean commit, `git rebase origin/main` on the
  `agent/<slug>` home branch, or `klartext converge` once shipped — the app does **not** auto-rebase at start
  (the drift gap in the Improvement Register). Never force-rebase a feature branch with an open PR.

## Team-memory binding

The shared team memory (`~/.claude/klartext-team-memory/`) is unversioned and written under one identity →
anchored memory edits carry the **C5 self-stamp** provenance convention (see the `knowledge-routing`
enactment and `../contracts/memory-substrate.md`).

## Enforcement (klartext)

A **ritual** (Enforcement Hierarchy level 2), user-triggered. The artifact-verification step is backed by the
PostCompact/PreCompact audit hooks + the compact monitor (launchd). Embedded sibling: `knowledge-routing`
runs inside this ritual (step 4 / the routing step).

## Evidence / learnings

- False-Persistence evidence: 2× compacted summaries claimed writes that never happened (2026-06-10) — the
  reason the artifact-verification step is mandatory.
- Pilot lesson 2026-06-11: a fresh session does not act before the user's first message → the successor seed
  must carry an explicit wake prompt.
