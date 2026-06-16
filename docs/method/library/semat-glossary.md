# SEMAT Glossary (L3) — Generic Essence / Meta-Language Vocabulary

> **Scope.** The **generic** Essence/SEMAT meta-language terms that hold for **any** endeavour using
> the method — not specific to klartext's runs, decisions, evidence or product.
> **Companion (L2).** klartext-specific process/method terms (our kernel extensions, our practices,
> our running-record concepts) live in
> [`../enactment/semat-glossary-klartext.md`](../enactment/semat-glossary-klartext.md).
> **Out of scope.** The product's **domain** vocabulary (e.g. *Wirkgefüge*, *Narrativ*) belongs in the
> product's ubiquitous-language glossary (German; location TBD), not here.
> **Anti-pattern guarded.** Wrong home — mixing process and product vocabulary (see
> `../enactment/continuous-improvement.md` §0 *Eigensaft* / RC1).
> **Language.** English — documentation-language rule.
>
> **Owner:** OE · **Status:** living (seeded lean, grown through real runs).
> **How this grows:** a new term is added when it actually shows up in a real run (an Improvement Step), not
> speculatively. Maintained via the Improvement Step practice.

---

## Meta-language (used as-is, not modified)

- **SEMAT** — *Software Engineering Method and Theory.* The initiative behind the Essence standard.
- **Essence** — the OMG standard we adopt as our **meta-language** for describing practices and composing
  them into a method. We use it **as-is and only extend it**; we never modify the standard. What we change
  *with* Essence is our own process, not Essence.
- **Kernel** — Essence's fixed common ground: the seven Alphas, activity spaces, competencies. We treat it
  as the **skeleton we fill**; we extend (add our own things on top), we do not re-invent it.
- **Alpha** — an essential *thing whose state we track* through a defined lifecycle (e.g. "Way of Working").
  This is the single most valuable import — it gives our artifacts and dependencies an explicit lifecycle
  (directly addresses root cause **RC4**).
- **Way of Working (Alpha)** — our own way of working, treated as a tracked Alpha with states
  (Principles Established → Foundation Established → In Use → In Place → Working Well → Retired).
  Our continuous improvement *is* the engine that advances this Alpha. *(State lifecycle: deliberately
  deferred, not forgotten.)*
- **Practice** — a **separately-describable, composable** unit of "a way of doing something" with a clear
  goal; it advances one or more Alphas. The reusable brick we compose into our Method. Lives in the
  Practice Library (`practices/`).
- **Method** — the composition of the Kernel and a set of Practices for a specific purpose = our forged way
  of working. Ours is described in `method.md`. (Cockburn: *methodology per project* — forge a fitting method,
  don't adopt one wholesale.)
- **Library (Practice Library)** — the catalog of described Practices from which Methods are composed. Ours is
  the `practices/` directory. Distinct from the Method: the Library is the *stock*, the Method is the
  *composition in use*.
- **Walking Skeleton / Tracer Bullet** — a minimal **real** end-to-end thread through the system, built to
  validate the architecture before fleshing it out (Cockburn). Used here to pressure-test the minimal
  meta-frame.
- **Resource** — external supporting material a Practice references but we do not produce (e.g. the IJI Alpha
  State Cards deck). Home: `assets-local/` (gitignored, README = provenance register). Not a Work Product.

## Cross-cutting principles

- **SSOT (Single Source of Truth)** — exactly one canonical home per piece of information; everything else
  references it. Anti-drift (RC1/RC4).
- **Ubiquitous Language (DDD)** — shared meaning comes from one small authoritative glossary, not from
  importing jargon. This file *is* that mechanism for our process vocabulary.
- **Enforcement Hierarchy** — (1) mechanical > (2) ritual > (3) never advisory-only. A practice can be
  promoted up this hierarchy (e.g. ritual → skill).
