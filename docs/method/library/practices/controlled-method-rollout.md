# Controlled Method Rollout

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** the per-change breaking-classification answer (rolling|breaking); the rollout record (for a barrier: stabilise → update → resync-and-verify)
> **Activity / Activity Space:** Way of Working → Support the Team (land a way-of-working change across isolated workspaces without breaking a drifted member)
> **External dependencies (referenced Resources):** Parallel Change / expand–contract pattern (Martin Fowler) — referenced as an adopted pattern, not vendored
> **Enforcement:** ritual (classification gate + drift/verify = mechanical promotions)  ·  **NN:** ✓ (every way-of-working change)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** — (ritual; classification gate + a converge/verify-before-resume check are the mechanical promotions)

## Purpose

Ensure a way-of-working change (skills, rituals, shared settings/hooks/allowlists, commands and the
paths/commands they reference) reaches **every** isolated workspace without breaking a **drifted** member —
at the **lowest** coordination cost the change allows. Closes the gap that pure eventual convergence leaves
open: eventual consistency is unsafe for breaking changes, because a drifted member runs a now-broken ritual
before it ever converges. Guards the *"merge and keep running"* failure mode for breaking method changes.

## Definition / delta

**Two modes:**

| Mode | When | What happens |
|---|---|---|
| **Rolling** *(default)* | **Backward-compatible** change — a drifted member keeps running correctly and picks the change up later | No global halt. Each member converges on its own initiative at its next session. |
| **Barrier** *(stop-the-world)* | **Breaking** change — the old state breaks (anchored command/path/skill no longer matches) | All members stabilized + paused, the change lands, all resync **and verify current** before resuming. |

**The trigger — classify every change.** Every way-of-working change answers, **explicitly**, one question:
**"Is this breaking for a *drifted* member?"**
- **No silent default** — the answer is recorded (PR label / checklist), never assumed.
- **Uncertainty → breaking wins** (fail-safe: cheaper to halt once too often than to break a drifted member).
- **Expand–contract first** — before classifying a change *breaking*, ask: *can we make it
  backward-compatible?* (keep the old command/path as an **alias** during a transition window, then remove
  it). A change built this way is **Rolling**, not Barrier — this is the main lever to need the barrier less
  often. (This is the **Parallel Change / expand–contract** pattern, Fowler — adopted, not invented.)

**Barrier-mode steps:** 1) **Stabilize & Halt** — each member secures what lives only in conversation and
pauses (nothing session-only is lost before shared state is touched). 2) **Update** — the change lands,
**including tooling bootstrap**. 3) **Resync & Verify** — every member converges **and verifies it is
current** before resuming. *(Rolling mode is just step 2; members converge on their own at next session.)*

**Completion (Done):** the change is **classified** (breaking? yes/no) explicitly · expand–contract was
considered · **Rolling:** landed, members converge at next session · **Barrier:** Stabilize & Halt → Update
(+bootstrap) → Resync & **Verify current** completed before resume.

**Enforcement note (generic).** Ritual with two mechanical promotions: a **classification gate** at
change-land time, and a **verify-current-before-resume** drift check. Until the drift check lands, the
resync-and-verify step of a barrier is run by hand.

## Related

- klartext enactment: [`../../enactment/practices/controlled-method-rollout.md`](../../enactment/practices/controlled-method-rollout.md)
- Composes with a convergence mechanism (the action half) and a drift-detection practice (the warning half).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
