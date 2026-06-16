# Systematic Debugging

> **Essence type:** Practice
> **Advances Alpha:** Software System (Demonstrable — defects are root-caused, not patched) and Way of Working (the QA system learns from each caught gap)  ·  **Work Products:** the failing-then-green fix test; a `qa-retro` learning entry when the bug exposed a test blind spot
> **Activity / Activity Space:** Implement the System → find the root cause of a defect before changing code; feed any exposed test gap back into the QA system
> **External dependencies (referenced Resources):** **superpowers (Resource)** — wraps `superpowers:systematic-debugging`
> **Enforcement:** ritual (the skill is invoked on any bug/unexpected behavior; the `qa-retro` tail is non-optional when the answer is "yes")  ·  **NN:** ✓
> **Status:** living  ·  **Owner:** QA (this is QA-owned discipline — the `qa-retro` tail composes on it)
> **Enacted as:** the `systematic-debugging` skill (`docs/superpowers/skills/systematic-debugging/SKILL.md`) — a thin loader that invokes the upstream skill, then appends the `qa-retro` step

> **QA-RATIFIED (2026-06-16, review on PR #148).** This card is QA-owned; drafted by an OE-spawned
> sub-agent and **ratified by real QA** against the pinned superpowers 5.1.0 install (the Iron Law +
> four-phase structure confirmed present). The composition is QA-blessed; mechanization (a session-health
> grep against the pinned install) remains an open OE/DevOps candidate.

## Purpose

How klartext debugs any bug or unexpected behavior: the generic root-cause discipline, **composed**
with our QA feedback loop. This card is a **wrapper** — it declares the upstream Resource and states
only the klartext composition delta; it does **not** restate the debugging method.

## Definition / delta (composition only)

The generic systematic-debugging discipline — the root-cause-before-fix Iron Law and its phased
investigation — lives **upstream** in `superpowers:systematic-debugging` (the referenced Resource). It
is **not** restated here; restating it would be vendoring-by-paraphrase (RC4). For the discipline
itself, the upstream skill is the single source of truth.

**The klartext composition delta** (the only thing this card adds) — a **qa-retro tail**:

1. **Load the upstream discipline first.** The `systematic-debugging` skill's Step 1 invokes
   `superpowers:systematic-debugging`; *all its rules apply without exception*. The klartext addition
   runs *after* the fix, never replacing the investigation.
2. **After the fix is green, run the QA-retro decision** (Step 2): *should the QA agent have written a
   test for this during the original implementation?*
   - **Yes** → invoke `qa-retro` — document the blind spot and update the QA system (a new failing test,
     the identified gap, a learning entry). Non-optional when the answer is yes: it is how the QA system
     learns; a bug fixed without it can recur.
   - **No** (environment/data issue, not a code gap) → no action.

This tail is what makes klartext debugging *close the loop* into the **Retrospective** family: the
incident-triggered test-gap sibling (`qa-retro`) and the periodic `retrospective` practice feed
Improvement instances into the **same** register.

## Related

- **Upstream Resource:** [`../resources/superpowers.md`](../resources/superpowers.md) (`superpowers:systematic-debugging`).
- **The qa-retro tail:** the `qa-retro` skill (the incident-triggered test-gap retrospective — QA-owned).
- **Periodic sibling:** [`retrospective.md`](retrospective.md) — both feed the one Improvement Register.
- **Dependency contract:** [`../../enactment/contracts/superpowers.md`](../../enactment/contracts/superpowers.md) — invariant S2 (the wrapped debugging discipline still carries its Iron Law; QA ratifies this half).
- [`../_card-template.md`](../_card-template.md) — the wrapper rule (declare, don't paraphrase).
