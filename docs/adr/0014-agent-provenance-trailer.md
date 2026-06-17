# 0014 — Agent Provenance: One Identity Across Inbox, Memory, and Git

**Status:** Accepted — SA-owned. The enforcement half (commit-msg hook + CI check) is **built and live on `main`** — #161: `scripts/agent_trailer.py` (inject + validate) and the `agent-provenance.yml` CI gate, spawn-aware, with an `Agent: human` bypass. Live proof: PR #163 (`766b7a0`) carried `Agent: oe` and passed the gate. Residual #162 (install the hook in each local clone) is low-priority — CI enforces server-side regardless.
**Decided by:** User (direction — extend provenance to git as a **sibling** of memory's C5, 2026-06-15).
**Author / Sign-off:** System Architect.
**Spun out of:** [ADR-0013](0013-separating-method-from-product.md) Decision (c) — separated because it is independently landable and crosses into the Infrastructure Perimeter.
**Relates to:** the team-memory **contract clause C5** (last-edited-by provenance); ADR-0010 §2 (worktree-per-agent); ADR-0012 (`converge`, lead-and-spawn execution).

## Context

A klartext colleague has **one identity** that is rendered across several substrates, but until now git was the gap. The identity facts:

- **SSOT = the `agents/<name>/` directory name** (the slug). `team.yaml` carries metadata only — it is not the source of identity.
- Already rendered: the **inbox** `from`/`to` fields; **team-memory** last-edited-by (contract clause **C5**).
- **Missing: git.** All agents commit under the single GitHub identity `ThorstenDittmar` (the reason GitHub rejects self-approval on our PRs — see the SA sign-off process). A commit therefore does not record **which agent** authored it. With lead-and-spawn execution (ADR-0012 / ADR-0013), where a lead spawns sub-agents that commit, the attribution gap widens.

This is the same provenance **need** C5 answers for memory, for a different substrate. The trailer is git's **sibling** of C5 — a parallel mechanism, not a generalisation of it: C5 self-stamps memory files (which live outside git), the trailer stamps git commits. Two provenance mechanisms for two substrates; neither subsumes the other.

## Decision

**Record agent provenance as a git commit trailer.**

- **Trailer:** `Agent: <slug>` — where `<slug>` is the `agents/<name>/` directory name (the SSOT).
- **Spawn-aware:** when a lead has spawned a sub-agent to do the work, the trailer is `Agent: <lead> (spawned <task>)` — the accountable identity is the lead; the spawn is visible.
- **Placement:** a standard git trailer in the commit message footer, alongside the existing mandated `Co-Authored-By:` line. It is additive — it does not replace the Co-Authored-By convention.
- **Enforcement (Enforcement Hierarchy — mechanical):**
  - a **commit-msg hook** that adds/validates the `Agent:` trailer at commit time, and
  - a **CI check** that rejects a method/agent commit lacking a well-formed trailer.
  This is the most strongly enforceable rendering of the one-identity model — git history becomes self-describing.
- **Deferred:** per-agent **real GitHub identities** (distinct authors/accounts). Out of scope here; start with the visible, enforceable trailer. Revisit only if the single-identity constraint (self-approval, attribution in the GitHub UI) becomes a binding problem.

## Rejected / deferred alternatives

| Alternative | Verdict | Reason |
|---|---|---|
| **Per-agent GitHub identities now** | Deferred | Heavier (accounts, auth, key management) and not required to close the attribution gap. The trailer gives self-describing history immediately; real identities can follow if needed. |
| **Derive the agent from `team.yaml`** | Rejected | `team.yaml` is metadata, not the SSOT. Identity is the `agents/<name>/` directory name; the trailer must reference that, so it cannot drift from `team.yaml`. |
| **Bundle into ADR-0013** | Rejected | Separable and Infrastructure-Perimeter; independently landable (this ADR). |

## Consequences

**Positive**
- Git history records **which agent** produced each commit → the one-identity model is complete across inbox, memory, **and** git.
- Spawn-aware form keeps accountability with the lead while making the spawn visible — fits the lead-and-spawn execution model of ADR-0012/0013.
- Mechanical enforcement (hook + CI) — not a review-time convention that erodes under pressure.

**Negative / Risks**
- A new commit-msg hook is friction if it rejects commits; it must fail with a clear, copy-pasteable fix and a documented bypass for genuine non-agent commits.
- Until the hook lands, the trailer is a manual convention (ritual-level) and applied unevenly. **Mitigated** — the hook + CI gate landed in #161; the trailer is now mechanically enforced.

## DevOps Briefing

```
Need:      A commit-msg hook + CI check enforcing the `Agent: <slug>` commit trailer
           (spawn-aware: `Agent: <lead> (spawned <task>)`), slug = agents/<name>/ dir name.
Why:       Close the git attribution gap — git is the one substrate where the single
           GitHub identity (ThorstenDittmar) hides which agent authored a commit.
           Git's commit-trailer sibling of team-memory contract clause C5 — a parallel
           provenance mechanism for a different substrate, not a generalisation (ADR-0014).
Domain:    Config / CI / Hooks (Infrastructure Perimeter: .pre-commit-config.yaml or a
           commit-msg hook, .github/workflows/, possibly api/cli.py for a helper).
Approach:  (suggestion) commit-msg hook injects/validates the trailer from the worktree's
           agent slug; CI rejects a method/agent commit without a well-formed trailer;
           define the non-agent bypass and the spawn-aware form.
Impact:    All agents — every commit gains the trailer; CI gate applies to method/agent paths.
```

SA defines the rule (this ADR); DevOps owns the mechanism and wires the hook + CI. Neither acts alone — the rule is documentation until DevOps enforces it.

## Open questions — resolved by the enforcement build (#161)

1. ~~Exact scope of the CI gate — all commits, or only method/agent-path commits?~~ → **All commits.** `agent-provenance.yml` validates every commit on the branch, with an explicit `Agent: human` bypass for genuine non-agent commits — not a path-restricted gate.
2. ~~The non-agent bypass form — explicit marker vs allowlist.~~ → **Explicit marker:** `Agent: human` (no allowlist).
3. ~~Helper in `api/cli.py` (`klartext commit` wrapper) or purely in the hook?~~ → **Purely in the hook** — the logic lives in `scripts/agent_trailer.py`; no CLI wrapper.

**Known limitation (parked, 2026-06-17):** the trailer stamps the *agent*, not the *generation* — a predecessor and a successor of the same role both read `Agent: <slug>`. Surfaced when #163 was squashed (two `Agent: oe` stamps collapsed to one). Tracked in team-memory `project_adr0014_generation_provenance`; currently judged unimportant.
