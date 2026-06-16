# Systematic Debugging — klartext enactment

> **Scope.** klartext's enactment of the **systematic-debugging** wrapper practice: the concrete bindings
> of the `qa-retro` tail — when it fires, who owns it, where the learning lands, and how it joins the
> Improvement Register.
> **Out of scope.** The generic root-cause discipline (the Iron Law, the four phases) — that is
> `superpowers:systematic-debugging`, **referenced, not restated** here. The composition delta — see the
> L3 wrapper card.
> **Language.** English — documentation-language rule.
> **QA-OWNED.** This is QA-owned discipline; drafted by an OE-spawned sub-agent *as if QA*. **Real QA
> ratifies on wake** (see the L3 card's ratification flag).
>
> **L3 definition:** [`../../library/practices/systematic-debugging.md`](../../library/practices/systematic-debugging.md)
> **Upstream Resource:** [`../../library/resources/superpowers.md`](../../library/resources/superpowers.md) (`superpowers:systematic-debugging`)
> **Status:** living (ritual) · **Owner:** QA · **Advances Alpha:** Software System + Way of Working · **NN:** ✓
> **Enacted as:** the `systematic-debugging` skill (`docs/superpowers/skills/systematic-debugging/SKILL.md`) → loads upstream, then the `qa-retro` skill

## klartext bindings

### When the qa-retro tail fires

After a fix is green, the decision *"should a test have caught this during the original
implementation?"* gates the tail:

- **Yes** → `qa-retro` runs: write the missing test (red → green), name the **blind spot**, record a
  **learning entry**.
- **No** (environment issue, data issue, not a code gap) → no action; the decision itself is recorded by
  the skill's Step 2.

### Homes (klartext)

- **Learning entries** → `docs/superpowers/qa-learnings/` (one file per learning; QA-owned).
- **Improvement instances** that emerge → the **Improvement Register** in
  [`../continuous-improvement.md`](../continuous-improvement.md) §3 — the *same* register the periodic
  `retrospective` feeds.
- **Root-cause mapping** uses the klartext RC catalog (`../continuous-improvement.md` Phase 1) — the same
  catalog the periodic retro maps to.

### Relation to the other QA loops

- **Periodic sibling:** the `retrospective` practice (event-triggered, whole-team). `systematic-debugging`
  is the **incident-triggered** entry point; both converge on one register — no second register, no
  divergent truth.
- **Blind-spot heuristics** the QA agent applies live in QA's knowledge file (e.g. *FakeService =
  domain-bypass*; *fake = behavioral parity, not just return values*) — those are QA Hoheitswissen, not
  re-stated here.

## Enforcement (klartext)

Ritual at invocation (the skill runs on any bug/unexpected behavior); the `qa-retro` tail is
**non-optional when the answer is "yes"** — it is how the QA system learns. Promotion beyond ritual is a
QA/Improvement-Register decision.

## Related

- L3 wrapper card: [`../../library/practices/systematic-debugging.md`](../../library/practices/systematic-debugging.md).
- Upstream Resource: [`../../library/resources/superpowers.md`](../../library/resources/superpowers.md).
- Dependency contract: [`../contracts/superpowers.md`](../contracts/superpowers.md) (S2 — QA ratifies the wrapped debugging discipline still carries its Iron Law).
- Periodic sibling enactment: [`retrospective.md`](retrospective.md).
- The skill source: `docs/superpowers/skills/systematic-debugging/SKILL.md` (F3 — not modified by this package).
