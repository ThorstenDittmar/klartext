# QA Retrospective — klartext enactment

> **Scope.** klartext's enactment of the **qa-retro** practice: where the learning entry lands, the
> blind-spot → action table against the concrete QA files, the Improvement-Register binding, and the
> `systematic-debugging` / `tdd` triggers.
> **Out of scope.** The generic test-gap loop and its seven steps — see the L3 card. The root-cause
> discipline (`systematic-debugging`); the periodic whole-team retro (`retrospective`).
> **Language.** English — documentation-language rule.
> **Seeded by an OE-spawned sub-agent (F0.2-P-C); awaits real-QA ratification on wake.**
>
> **L3 definition:** [`../../library/practices/qa-retro.md`](../../library/practices/qa-retro.md)
> **Status:** living (ritual) · **Owner:** QA · **Advances Alpha:** Way of Working + Software System · **NN:** ✓ (when triggered)
> **Enacted as:** the `qa-retro` skill (`docs/method/enactment/skills/qa-retro/SKILL.md`)

## klartext bindings

### Triggers

- **From `systematic-debugging`:** after a fix is green, the decision *"should a test have caught this during
  the original implementation?"* — **yes** → `qa-retro` runs (the qa-retro tail of that practice).
- **From `tdd`:** a bug-fix that should have been caught earlier.
- **Manual (`/qa-retro`):** a user-reported or production-observed defect.

### Learning-entry home

One file per blind spot in `docs/superpowers/qa-learnings/YYYY-MM-DD-<short-description>.md` (QA-owned),
fixed shape: what happened · missing test + which of the five categories · why qa-review missed it ·
consequence (file changed + Semgrep rule, or "not applicable"). Precedent on disk:
`2026-06-12-fake-error-behaviour-parity.md`.

### Blind-spot → action (against the concrete QA files)

| Blind-spot type | Action — file |
|---|---|
| Unknown category | new category in `docs/method/enactment/skills/qa-review/qa-categories.md` |
| Wrong trigger condition | fix trigger in `qa-categories.md` or `domain-composition-rules.md` |
| Agent failure (3+ repeats) | sharpen the rule wording |
| Statically checkable pattern | new rule in `.semgrep/rules/qa/` — `qa-<name>.yaml` |

**Boundary:** all changes stay in QA domain (`api/tests/`, `.semgrep/rules/qa/`, the `qa-learnings/`, the
`qa-*` skill files). A change outside it (a CI step, a `pyproject.toml` dependency, an **arch-layer** Semgrep
rule) is **not** made here — DevOps Briefing or brief System Architect instead. (Note the known structural
discrepancy: `agents/qa/claude.md` records that actual rules currently sit flat in `.semgrep/rules/` with a
`klartext-*` prefix, pending an SA directory decision — do not pre-empt it.)

### Improvement-Register binding

Improvement instances that emerge feed the **Improvement Register** in
[`../continuous-improvement.md`](../continuous-improvement.md) §3 — the *same* register the periodic
`retrospective` feeds. Root-cause mapping uses the same klartext RC catalog (Phase 1). No second register, no
divergent truth: `qa-retro` is the incident-triggered entry point, `retrospective` the periodic one.

## Enforcement (klartext)

Ritual, incident-triggered; **non-optional when the trigger answer is "yes"** — it is how the QA system
learns, and a bug fixed without it can recur. Promotion beyond ritual is a QA / Improvement-Register decision.

## Related

- L3 definition: [`../../library/practices/qa-retro.md`](../../library/practices/qa-retro.md).
- The triggers: [`systematic-debugging.md`](systematic-debugging.md) (the qa-retro tail) · [`tdd.md`](tdd.md) (bug-fix flow).
- The periodic sibling: [`retrospective.md`](retrospective.md) · the review practice it sharpens: [`qa-review.md`](qa-review.md).
- The skill source: `docs/method/enactment/skills/qa-retro/SKILL.md` (F3 — not modified by this package).
