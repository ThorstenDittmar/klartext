# Dependency Contract

> **Essence type:** Work Product (element)
> **Advances Alpha:** Way of Working (Non-negotiable practices & tools identified · Gaps between available and needed way of working understood)  ·  **Work Products:** the contract itself (a set of invariant clauses)
> **Activity / Activity Space:** Prepare to do the Work / Plan the Work → identify and bind the invariants a central dependency must uphold
> **External dependencies (referenced Resources):** none — this is our own element definition
> **Enforcement:** convention (each clause names its own check; the check's enforcement level is per-clause: mechanical · ritual · convention)
> **NN:** —
> **Status:** living  ·  **Owner:** OE (form + element definition)
> **Enacted as:** one card per contract under `docs/method/enactment/contracts/` (L2 instances)

## Purpose

A **Dependency Contract** captures the **invariants our way of working requires *from* a central
component we depend on** — the storage substrate, an external service, a shared tool. It is the
*upstream* counterpart to Environment Knowledge's **dependency chain**:

- a **dependency chain** lists *what of ours breaks* if a fact about a dependency changes
  (the **downstream blast radius** — what we watch);
- a **Dependency Contract** lists *what we require to hold* (the **invariants** — what we demand).

They are complementary, not duplicate. A dependency chain is observational ("if this changes, these
break"); a contract is prescriptive ("this must hold, and here is how we catch it if it does not").

## When to forge one — the "Schnur"

Forge a Dependency Contract only when **both** conditions hold (otherwise: *Flut vermeiden* — do not
contract every dependency):

1. **Central** — the way of working genuinely depends on this component; a violation has broad blast
   radius across the endeavour, not a single local feature.
2. **A future external update could change it non-obviously** — the component (or the seam we share
   with it) can shift *under us* in a way that is not loud at change-time, so an explicit, checkable
   invariant is the only thing that turns a silent drift into a caught failure.

If a dependency is central but fully **owned** by us (we change it only deliberately, loudly), an
IaC + health-check usually suffices and no contract is needed. The contract earns its keep precisely
at a **seam** — where neither pure "external" (only observe + Canary) nor pure "ours" (just build it
right) describes the relationship, so a shared set of invariants is checked against **whichever side
provides them**.

## Structure — clause + blast radius + falsifiable check

A Dependency Contract is a set of **clauses**. Each clause has exactly three parts:

| Part | What it states |
|---|---|
| **Invariant** | The single thing that must hold (one clause = one invariant). |
| **Blast radius** | What breaks across the way of working if this invariant is violated. |
| **Falsifiable check** | The mechanization that makes the invariant *checkable* — a health-check, test, or (where mechanization is not yet possible) an explicitly-named ritual. A clause without a check is an aspiration, not a contract clause. |

A clause may also carry a **status** (holds today? · decided/deferred · live in which hook) so the
contract doubles as a live ledger of which invariants are actually enforced versus still aspirational.

## Why a contract — the lever the seam gives us

Because we (partly) **own** the inner face of a seam, a contract reveals **design levers**, not just
risk to watch: with a purely external component we can only observe and Canary; at a seam we can
*build* the inner face to satisfy the contract. A violation on **either** side is checked against the
**same** clauses — so "what changed under us" and "what we changed" are caught by one set of
invariants.

## Relationship to other elements

- **Environment Knowledge** (dependency chain + Canary) — provides the *uncontrolled-face* work
  product; a contract's external-facing clauses reference it. The two are deliberately
  distinct elements (KB-confirmed, no Kernel change — a Work-Product type alongside the others).
- **Controlled Method Rollout** — a change that violates a contract clause for a *drifted* consumer is
  **breaking** (barrier mode). The contract feeds that classification.
- **Drift Awareness / convergence** — convergence keeps a consumer's *copy* of the substrate current;
  the contract states what the substrate must guarantee in the first place.

## Related

- L2 instances live under [`../enactment/contracts/`](../enactment/contracts/) — e.g.
  [`memory-substrate.md`](../enactment/contracts/memory-substrate.md) (the klartext team-memory + inbox + pin substrate, clauses C1–C5).
- [ADR-0013](../../adr/0013-separating-method-from-product.md) — method/product separation (L3 vs L2).
- The method register's *Dependency Contracts* paragraph in [`../enactment/method.md`](../enactment/method.md).
