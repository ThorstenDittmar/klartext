# SEMAT Glossary — Process & Method Vocabulary

> **Scope.** This document holds our **process/method** vocabulary — the terms we use to forge and run our
> way of working (Essence/SEMAT terms + our own practices).
> **Out of scope.** The product's **domain** vocabulary (e.g. *Wirkgefüge*, *Narrativ*) belongs in the
> product's ubiquitous-language glossary (German; location TBD), not here.
> **Anti-pattern guarded.** Wrong home — mixing process and product vocabulary (see
> `continuous-improvement.md` §0 *Eigensaft* / RC1).
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

## Our method elements

The authoritative register of our method's elements (practices, patterns, work products, gates) is
**`method.md`** — our Essence **Method** document. Practice *content* lives in `practices/` — our
**Practice Library**. This glossary defines *terms* only and does not list elements (SSOT discipline).

- **Walking Skeleton / Tracer Bullet** — a minimal **real** end-to-end thread through the system, built to
  validate the architecture before fleshing it out (Cockburn). Used here to pressure-test the minimal
  meta-frame.
- **Method Literacy** *(Competency, our kernel extension)* — the ability to locate way-of-working topics in
  Essence terms (element type, Alpha) and to use the method document set. Levels per Essence
  (1 *Assists* … 5 *Innovates*). Registered in `method.md`.
- **Resource** — external supporting material a Practice references but we do not produce (e.g. the IJI Alpha
  State Cards deck). Home: `assets-local/` (gitignored, README = provenance register). Not a Work Product.
- **Improvement** *(sub-alpha, practice-defined)* — a possible adaptation to improve the team's Way of
  Working; states *Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use*. Defined
  by the Retrospective practice; instances live in the Improvement Register.
- **Environment Knowledge** *(Practice)* — the repeatable way we hold **version-bound, falsifiable** facts
  about our development environment (the tools we *use*, not *build*) so a stale fact cannot silently drive a
  decision (RC4). Each fact is version-bound, has a **Canary**, and lists its **dependency chain**. Card:
  `practices/environment-knowledge.md`; Work Products: `environment/`.
- **Canary** *(our term)* — a concrete check attached to a version-bound environment fact that re-proves or
  breaks it; when it breaks, the fact is presumed stale until re-verified. **Manual** where the subject tool
  cannot be scripted (e.g. the Claude Code app), otherwise a candidate for a mechanical check.

## Cross-cutting principles

- **SSOT (Single Source of Truth)** — exactly one canonical home per piece of information; everything else
  references it. Anti-drift (RC1/RC4).
- **Ubiquitous Language (DDD)** — shared meaning comes from one small authoritative glossary, not from
  importing jargon. This file *is* that mechanism for our process vocabulary.
- **Enforcement Hierarchy** — (1) mechanical > (2) ritual > (3) never advisory-only. A practice can be
  promoted up this hierarchy (e.g. ritual → skill).
