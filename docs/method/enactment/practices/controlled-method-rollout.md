# Controlled Method Rollout — klartext enactment

> **Scope.** klartext's enactment of the **Controlled Method Rollout** practice: the ADR-0012 anchoring, the
> live mechanization state (the classification gate), the tooling-bootstrap specifics, and the incident that
> forged the card.
> **Out of scope.** The generic two-mode definition — see the L3 card. The convergence *mechanism*
> (`klartext converge`, ADR-0012 — DevOps). Drift *detection* (the **Drift Awareness** practice, register
> #106). Product changes (code, ADRs, domain docs).
> **Anti-pattern guarded.** *"Merge and keep running"* for method changes: a **breaking** way-of-working
> change lands on `main` while worktrees still drift. **Live instance (2026-06-14):** a way-of-working change
> on `main` broke the `anchor` ritual for agents whose worktree was on an older state.
> **Language.** English — documentation-language rule.
>
> **L3 definition:** [`../../library/practices/controlled-method-rollout.md`](../../library/practices/controlled-method-rollout.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working · **NN:** ✓ (every way-of-working change)

## klartext bindings

- **The two-mode rule** is a **condition on ADR-0012's Consistency axis** (eventual by default;
  strong/barrier when breaking), recorded as an **ADR-0012 addendum** (authored by SA, OE gates).
- **The backward-compatible-first lever** is the **Parallel Change / expand–contract** pattern (Fowler) —
  adopted, not invented.
- **Barrier step 2 (Update) includes tooling bootstrap:** pull the main checkout (`~/klartext`) so the
  shared venv carries the new commands, and run any skill-sync.
- **Barrier step 1 (Stabilize)** = the `anchor` ritual on every agent.
- **Barrier step 3 (Resync)** = `klartext converge` + the SessionStart drift / G2 check is green.
- **Companion:** the **Memory-Substrate Dependency Contract** (`../contracts/memory-substrate.md`)
  tells you *what the storage substrate guarantees*; a change that violates a contract clause for a drifted
  agent is breaking.

## Mechanization (klartext)

- **Classification gate** — the "breaking?" answer as a PR label/step. **LIVE + ENFORCED** (PR #125;
  `Classification (rolling|breaking)` is a required status check on `main`, strict, since 2026-06-15). A
  WoW-PR without a `rolling`/`breaking` label is blocked at merge. *(Scope still narrow — method docs under
  `docs/superpowers/improvement/**` not yet triggered; revisit after a practice window — see register.)*
- **Drift / G2 verify-before-resume** check — still pending (DevOps). Until it lands, the *resync-and-verify*
  step of a barrier is run by hand (as on 2026-06-14).
- **Converge** — `klartext converge`, the action half (ADR-0012). *(DevOps)*

## Enforcement (klartext)

**Partly mechanical (2026-06-15).** See Mechanization above; the two mechanical promotions are owned by
DevOps.

## Evidence / learnings

- **First enactment = the 2026-06-14 anchor incident.** A breaking way-of-working change on `main` broke the
  `anchor` ritual for drifted agents; the user + DevOps ran a manual stop-the-world (secure → update →
  resync) on all agents. This card lifts that handled-by-hand procedure into the method.
- **Why two modes and not always stop-the-world:** the full brake is expensive; most changes can be built
  backward-compatible and ride the cheap ADR-0012 rolling path. The discipline is at *land time*: ask the
  breaking question, and prefer expand–contract so the answer is usually "no".
- This very refactoring (F0.1-P2) is itself executed under this practice in **BARRIER mode** (ADR-0013
  Execution context).
