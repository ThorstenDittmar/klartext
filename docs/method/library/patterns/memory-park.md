# Memory Park / Custody

> **Essence type:** Pattern
> **Advances Alpha:** Way of Working (protects the team's durable knowledge)  ·  **Work Products:** none (a custody manoeuvre over existing knowledge artifacts)
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (whenever at-risk knowledge would otherwise live in only one place)
> **Status:** living  ·  **Owner:** OE (pattern form)

## Purpose

Protect knowledge that is **at risk of loss** (a context reset, a destructive git operation, a not-yet-landed
artifact) by **parking a verbatim copy out of tree** — in a redundant custody depot — with an explicit
restore condition and a delete-after-verification rule. Guards the single-copy failure mode: knowledge that
exists in exactly one place that is about to disappear.

## Definition / delta

When a piece of knowledge is at risk and not yet safely persisted:

1. **Park verbatim** — copy the content unchanged into an out-of-tree custody depot (e.g. auto-memory),
   never a paraphrase. A paraphrase is a second source of truth and may drift from the original.
2. **Record the restore condition** — state exactly when and to where the parked copy is to be restored
   (e.g. "restore into `docs/...` once branch X lands").
3. **Delete after verification** — once the knowledge is confirmed safely in its durable home, **delete the
   parked copy**. The park is a bridge, not a second permanent home — leaving it in place re-creates the
   drift it was meant to prevent.

**Completion (Done):** content parked verbatim (not paraphrased) · restore condition written down with a
target home · the parked copy is deleted once the durable home is verified to hold it.

**Enforcement note (generic).** Ritual; bridges a gap mechanical persistence does not yet cover. Applied
3× on 2026-06-10, bridging two data-loss incidents. Hard to mechanize (the "at-risk" judgement is human);
the delete-after-verification step is the part most prone to being forgotten.

## Related

- Often runs inside the session-safeguard ritual (`anchor` skill) and the knowledge-routing flow.
- [[blocker-protocol]] (a parked item may accompany an escalation) ·
  [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
