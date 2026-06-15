# Practice: Controlled Method Rollout

> **Scope.** This document defines **Controlled Method Rollout** — how a change to the **agents' way of
> working** (skills, rituals, shared `settings.json`/hooks/allowlists, commands and the paths/commands they
> reference) is rolled out across the isolated worktrees **safely**, choosing the lightest safe mode.
> **Out of scope.** Product changes (code, ADRs, domain docs — those advance the Software System alpha, not
> the Way of Working). The convergence *mechanism* (`klartext converge`, ADR-0012 — DevOps). Drift *detection*
> (the **Drift Awareness** practice, register #106).
> **Anti-pattern guarded.** *"Merge and keep running"* for method changes: a **breaking** way-of-working change
> lands on `main` while worktrees still drift → the anchored commands/paths a drifted agent runs no longer
> match. **Live instance (2026-06-14):** a way-of-working change on `main` broke the `anchor` ritual for agents
> whose worktree was on an older state — the incident that forged this card.
> **Language.** English — documentation-language rule.
>
> **Status:** active (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working
> **Source check:** composition, no Kernel change. The two-mode rule is a **condition on ADR-0012's
> Consistency axis** (eventual by default; strong/barrier when breaking), recorded as an **ADR-0012 addendum**.
> The backward-compatible-first lever is the well-known **Parallel Change / expand–contract** pattern (Fowler) —
> adopted, not invented.

## Goal

Ensure a way-of-working change reaches **every** isolated worktree without breaking a **drifted** agent — at
the **lowest** coordination cost the change allows. Closes the gap that pure ADR-0012 *eventual* convergence
leaves open: eventual consistency is unsafe for breaking changes, because a drifted agent runs a now-broken
ritual before it ever converges.

## Advances Alpha

**Way of Working** — every method change lands through a mode that keeps the team's operating model coherent
across the worktrees instead of silently fracturing it.

## The two modes (decision — recorded in the ADR-0012 addendum)

| Mode | When | What happens |
|---|---|---|
| **Rolling** *(default)* | **Backward-compatible** change — a drifted agent keeps running correctly and picks the change up later | No global halt. Each agent converges on its own initiative at the next session (ADR-0012 guarded voluntary convergence). |
| **Barrier** *(stop-the-world)* | **Breaking** change — the old state breaks (anchored command/path/skill no longer matches) | All agents stabilized + paused, the change lands, all resync **and verify current** before resuming. |

## The trigger — classify every way-of-working change

Every way-of-working PR answers, **explicitly**, one question: **"Is this breaking for a *drifted* agent?"**

- **No silent default.** The answer is recorded (PR label / checklist), never assumed.
- **Uncertainty → breaking wins** (fail-safe: cheaper to halt once too often than to break a drifted agent).
- **Expand–contract first.** Before classifying a change *breaking*, ask: *can we make it backward-compatible?*
  (e.g. keep the old command/path as an **alias** during a transition window, then remove it). A change built
  this way is **Rolling**, not Barrier — this is the main lever to **need the barrier less often**.

## Steps — Barrier mode (stop-the-world)

1. **Stabilize & Halt.** Each agent secures what lives only in chat (**= the `anchor` ritual**), reaches a
   stable state, and pauses. *Nothing that exists only in a session is lost before we touch shared state.*
2. **Update.** The change lands on `main`, **including tooling bootstrap** — pull the main checkout
   (`~/klartext`) so the shared venv carries the new commands, and run any skill-sync.
3. **Resync & Verify.** Every agent converges (`klartext converge`) **and verifies it is current** (the
   SessionStart drift / G2 check is green) **before** resuming work.

*Rolling mode is just step 2 (land it); agents converge on their own at the next session — no halt, no
coordinated verify.*

## Mechanization

- **Classification gate** — the "breaking?" answer as a PR label/step that triggers (or skips) the barrier. *(DevOps)*
- **"Verify current before resume"** — exactly the SessionStart drift / G2 check (DevOps, the detection half of
  Drift Awareness #106): a resynced agent starts green, a drifted one is warned. *(DevOps)*
- **Converge** — `klartext converge`, the action half (ADR-0012). *(DevOps)*

## Work Products

- This card.
- The **ADR-0012 addendum** carrying the two-mode decision (authored by SA, OE gates).
- The per-PR **breaking-classification** label/answer.

## Completion Checklist (Done)

- [ ] The change is **classified** (breaking for a drifted agent? yes/no), explicitly, on the PR.
- [ ] Expand–contract was considered — could it be made backward-compatible (alias/transition window)?
- [ ] **Rolling:** landed; agents converge at next session (no halt).
- [ ] **Barrier:** Stabilize & Halt → Update (+bootstrap) → Resync & **Verify current** completed before resume.

## Enforcement

**Partly mechanical (2026-06-15).** The two mechanical promotions are owned by DevOps:
- **Classification gate** at PR time — **LIVE + ENFORCED** (PR #125; `Classification (rolling|breaking)`
  is a required status check on `main`, strict, since 2026-06-15). A WoW-PR without a `rolling`/`breaking`
  label is now blocked at merge. *(Scope still narrow — method docs under `docs/superpowers/improvement/**`
  not yet triggered; revisit after a practice window — see register.)*
- **Drift / G2 verify-before-resume** check — still pending (DevOps). Until it lands, the *resync-and-verify*
  step of a barrier is run by hand (as on 2026-06-14).

## Notes

- **First enactment = the 2026-06-14 anchor incident.** A breaking way-of-working change on `main` broke the
  `anchor` ritual for drifted agents; the user + DevOps ran a manual stop-the-world (a sync script: secure →
  update → resync) on all agents. This card lifts that handled-by-hand procedure into the method — mirroring
  how the Improvement Step and Environment Knowledge cards were validated by self-application.
- **Why two modes and not always stop-the-world:** the full brake is expensive; most changes can be built
  backward-compatible and ride the cheap ADR-0012 rolling path. The discipline is at *land time*: ask the
  breaking question, and prefer expand–contract so the answer is usually "no".
- Companion: the **Memory-Substrate Dependency Contract** (`contracts/memory-substrate.md`) tells you *what the
  storage substrate guarantees*; the breaking-classification here is informed by it (a change that violates a
  contract clause for a drifted agent is breaking).
