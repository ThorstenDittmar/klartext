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
- **Method** — a composition of Practices = our forged way of working. (Cockburn: *methodology per project* —
  forge a fitting method, don't adopt one wholesale.)

## Our practices (the bricks we are forging)

- **Improvement Step** *(Practice)* — our atomic continuous-improvement practice
  (Pick up → Clarify & decide → Record → Route → Set next step). Advances the Way-of-Working Alpha.
  Defined in `practices/improvement-step.md`. Currently a ritual; skill promotion deferred.
- **Document Scoping** *(Practice)* — every document opens with a scope header
  (scope · out-of-scope + link · anti-pattern guarded · language). Defined in `practices/document-scoping.md`.
- **Walking Skeleton / Tracer Bullet** *(Practice, planned)* — a minimal **real** end-to-end thread through
  the system, built to validate the architecture before fleshing it out. (Cockburn.) Used here to pressure-test
  the minimal meta-frame.

## Cross-cutting principles

- **SSOT (Single Source of Truth)** — exactly one canonical home per piece of information; everything else
  references it. Anti-drift (RC1/RC4).
- **Ubiquitous Language (DDD)** — shared meaning comes from one small authoritative glossary, not from
  importing jargon. This file *is* that mechanism for our process vocabulary.
- **Enforcement Hierarchy** — (1) mechanical > (2) ritual > (3) never advisory-only. A practice can be
  promoted up this hierarchy (e.g. ritual → skill).
