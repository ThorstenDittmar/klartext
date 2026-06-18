# Essence (OMG Kernel & Language)

> **Essence type:** Resource
> **Advances Alpha:** — (a Resource is referenced material, not a Practice — it advances no Alpha on its own; the practices built on the Kernel do)
> **Work Products:** none (a Resource produces no Work Product — it is consumed, not authored, by us)
> **Activity / Activity Space:** — (not an Activity; it is the meta-language the method is forged in)
> **External dependencies (referenced Resources):** none — **this card *is* the external thing**; it declares the dependency rather than depending further
> **Enforcement:** convention (the version pin is a convention; the practices built on the Kernel carry their own enforcement)
> **NN:** —
> **Status:** living  ·  **Owner:** OE (the meta-language baseline + the reference rule)
> **Enacted as:** our self-contained rendition in [`../semat-definition.md`](../semat-definition.md) + the kernel state checklists in [`../alpha-states.md`](../alpha-states.md)

## Purpose

**Essence** is the OMG standard our entire way of working is forged in — the **Kernel** (the seven Alphas,
the activity spaces, the competencies) and the **Language** for describing Practices and composing them into
a Method. It is the same *class* of object as [`superpowers.md`](superpowers.md): material we **reference but
do not own and do not produce**. We adopt it **as-is and only extend it** (our own Practices/Patterns on top)
— we never modify the standard.

This card exists so the dependency is **declared and version-bound, not silently assumed**. Unlike a live
fetch, our rendition is deliberately **self-contained** (`semat-definition.md`, RC4 medicine) — so the
baseline travels *with* the method. But without a version pin its divergence — against upstream OMG, and (more
importantly for cross-project transfer) against a consumer's *adapted* copy — is not derivable. **This card is
that pin.**

## The reference rule — referenced, never vendored, never extracted

Same L3 Resource contract as superpowers (`_card-template.md`, Type-specific notes):

- **Referenced** — our cards build on the Kernel's vocabulary (Alphas, states, Practices); `semat-definition.md`
  is a *working summary rendition*, not a copy of the normative OMG text.
- **Never vendored** — the normative spec is not committed into the repo; we hold our rendition + this pointer.
- **A consumer adopts the Kernel themselves** — the dependency is satisfied in the consumer's *understanding*
  of the same standard, not by claiming ownership of the OMG text. When the L3 Library travels to another
  endeavour, **this card and our rendition travel** (normal L3 objects); the normative OMG spec does not — the
  consumer references the same standard at the same pinned baseline (the L3-travels-but-the-material-does-not
  rule: SA ratification, PR #137).

## Provenance & version binding

| Field | Value |
|---|---|
| **Standard** | Essence — Kernel and Language for Software Engineering Methods (OMG) |
| **Baseline pin** | **v1.2** — OMG document **formal/18-10-02**, adopted **July 2018** |
| **Upstream status** | v1.2 = latest **formal**; **v2.0 beta 2** (March 2026) is the current in-process revision — *informational, not formal* (verified against `omg.org/spec/Essence/`; no v1.3 is listed) |
| **Spec home** | `https://www.omg.org/spec/Essence/1.2/` |
| **Our rendition** | `semat-definition.md` (self-contained summary, rendered 2026-06) + `alpha-states.md` (the kernel state checklists) |
| **Our extensions** | klartext Practices/Patterns + tracked Work Products — additions *on top of* the Kernel, not changes to it |

The pin is what the **L2 Dependency-Contract instance** ([`../../enactment/contracts/essence.md`](../../enactment/contracts/essence.md))
checks against: an upstream move (e.g. v2.0 going formal) is a **contract concern** — re-check our
rendition against the new edition — **not a silent drift** (RC4).

## What depends on it

Everything. The Kernel / Alphas / states / Practices / Methods vocabulary underpins the whole L3 Library and
our way of working — directly `semat-definition.md`, `alpha-states.md`, `semat-glossary.md`, and every
practice/pattern card that names an Alpha or a Kernel element.

## Related

- [`../semat-definition.md`](../semat-definition.md) — our self-contained rendition (carries the inline baseline pin).
- [`superpowers.md`](superpowers.md) — the sibling referenced-never-vendored Resource (same contract).
- [`../_card-template.md`](../_card-template.md) — the Resource-card type note + the reference rule.
- L2 contract instance: [`../../enactment/contracts/essence.md`](../../enactment/contracts/essence.md) — the invariants our way of working relies on *from* the Kernel.
- [ADR-0013](../../adr/0013-separating-method-from-product.md) — method/product separation (why a referenced Resource is declared, never extracted into the product).
