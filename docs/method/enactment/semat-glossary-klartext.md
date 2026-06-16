# SEMAT Glossary (L2) — klartext-specific Process & Method Vocabulary

> **Scope.** klartext's **own** process/method terms — our kernel extensions, our practices, and the
> concepts of our running record (Improvement Register, environment facts). Specific to klartext's runs,
> decisions and evidence.
> **Companion (L3).** The generic Essence/SEMAT meta-language terms (SEMAT, Essence, Kernel, Alpha,
> Practice, Method, Library, …) live in
> [`../library/semat-glossary.md`](../library/semat-glossary.md).
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

## Our method elements

The authoritative register of our method's elements (practices, patterns, work products, gates) is
**`method.md`** — our Essence **Method** document. Practice *content* lives in `practices/` — our
**Practice Library**. This glossary defines *terms* only and does not list elements (SSOT discipline).

- **Method Literacy** *(Competency, our kernel extension)* — the ability to locate way-of-working topics in
  Essence terms (element type, Alpha) and to use the method document set. Levels per Essence
  (1 *Assists* … 5 *Innovates*). Registered in `method.md`.
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
