# Retrospective — klartext enactment

> **Scope.** klartext's enactment of the **Retrospective** practice: who triggers/hosts here, the input-
> gathering mechanism (subagent vs. live session), the homes, the RC catalog, and our runs.
> **Out of scope.** The generic definition, the Improvement sub-alpha states, the eight steps — see the L3
> card. The incident-triggered test-gap retro (`qa-retro` skill — the sibling practice); decisions and
> rationale (`../continuous-improvement.md`); the Improvement Register itself (lives in
> `../continuous-improvement.md` §3).
> **Anti-pattern guarded.** Decided-but-never-verified measures (RC2 — the "check effectiveness" gap);
> impressions instead of evidence as retro input.
> **Language.** English — documentation-language rule.
>
> **L3 definition:** [`../../library/practices/retrospective.md`](../../library/practices/retrospective.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working (tracks Improvement sub-alpha) · **NN:** ✓ (Work cannot reach *Closed* without it)
> **Resource binding:** IJI *Agile Retrospective Essentials* deck lives in `assets-local/` (CC BY 4.0).

## klartext bindings

- **Triggers vs. hosts (clarified 2026-06-10):** **Hannibal** (coordinator — *Coordinate Activity*) triggers;
  the **Method Keeper (OE) hosts**. Precedent: `qa-retro` is led by its practice owner (QA).
- **Root-cause mapping** maps findings to **RC1–RC6** (`../continuous-improvement.md` Phase 1).
- **Element sweep** reconciles against `../method.md` (RC4 medicine applied to the method itself).
- **Homes:** Improvement Register → `../continuous-improvement.md` §3; learning entries →
  `../learnings/` (one file per learning); card/`method.md` updates in the same step.

### Competencies (klartext)

- **Leader** — Method Literacy ≥ 2 (*Applies*); attaches to the existing **Method Keeper** pattern (OE) — no
  separate role imported (checked against the standard 2026-06-10).
- **Participants** — Method Literacy ≥ 1 (*Assists*).
- *"Whole team inspects and adapts"* is an **In Place** checkbox of the Way-of-Working alpha — full active
  whole-team participation is the *target state*, not an entry requirement for early runs. Team-wide literacy
  ≥ 2 is batched at the *Foundation Established* milestone (team refresh).

### How input is gathered (enactment mechanism)

The two participation tiers need different mechanisms:
- **Record review** asks about *domain match* — answerable from **disk** (`agents/<name>/claude.md`, roster).
  → A **forked subagent** per agent is sufficient; cheap broadcast, no live sessions needed.
- **Active input** asks about *experience* — knowledge that may exist only in the participant's long-living
  session. Two variants:
  - **(a) Artifact-mediated (preferred, cheap):** a forked subagent reads the participant's knowledge file +
    work products. **Valid only if** that agent's session knowledge was captured to disk (anchor-style
    capture) **at or after work-package end** — else it is a simulation that misses the very evidence the
    retro exists to collect.
  - **(b) Live session (fallback, expensive):** query the agent's long-living session via the user as
    channel. **Required** whenever (a)'s precondition is not confirmed — when in doubt, (b).
  - **Entry criterion (per participant):** capture confirmed → (a); otherwise → (b).

*Current state (2026-06-10; `pre-compact` renamed to `anchor` 2026-06-13):* the capture practice is
German-only; a versioned repo copy was added 2026-06-13 (`docs/superpowers/skills/anchor.md`, machine-local
install pending DevOps), validated only on OE sessions → (a) is **not yet trustworthy** for other agents;
active input therefore uses (b) until the capture practice is promoted (see the Improvement Register).

*Activation note:* the record-review tier becomes meaningful only after the team refresh (team-wide Method
Literacy ≥ 1); until then OE + user run the involvement check manually against the roster.

## Enforcement (klartext)

Currently a **ritual** (level 2). Skill promotion after the first real runs. Relation: `qa-retro` is the
**incident-triggered sibling** for test gaps — both feed Improvement instances into the same register.

## Evidence / learnings

- Runs recorded under `../learnings/` (first retrospective run, H01-422, delete-404 retrospective).
