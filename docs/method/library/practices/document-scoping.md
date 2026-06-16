# Document Scoping

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** a scope header at the top of every document
> **Activity / Activity Space:** Way of Working → Support the Team (keep content in the right home so the method's documents stay navigable)
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** —
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** — (ritual; candidate for promotion to a mechanical lint/CI check)

## Purpose

Every document declares, at its very top, **what belongs in it and what does not** — so content lands in the
right home, and any reader (human or agent) immediately knows the document's boundaries. Guards the
wrong-home / content-drift failure mode: the right content put in the wrong document.

## Definition / delta

Place a four-line scope header directly under the document title, **in the document's own language**:

> **Scope.** This document holds &lt;X&gt;.
> **Out of scope.** &lt;Y&gt; belongs in &lt;link&gt;, not here.
> **Anti-pattern guarded.** &lt;named anti-pattern&gt; — see &lt;reference&gt;.
> **Language.** &lt;language&gt; — documentation-language rule.

- **Scope** — one sentence: what content this document is the home for.
- **Out of scope** — what is easily confused with it but belongs elsewhere, **with a link to where**
  (mark `TBD` if that home does not exist yet).
- **Anti-pattern guarded** — the named failure mode this boundary prevents, referencing the team's
  anti-pattern catalog.
- **Language** — the document's language, per the documentation-language rule.

**Completion (Done):** the document opens with the four-line scope header · "Out of scope" links to the
correct alternative home (or marks it `TBD`) · "Anti-pattern guarded" names a failure mode and references the
catalog · the header is written in the document's own language.

**Enforcement note (generic).** A ritual; the natural mechanical promotion is a lint/CI check that fails
when a method document lacks the scope header.

## Related

- klartext enactment: [`../../enactment/practices/document-scoping.md`](../../enactment/practices/document-scoping.md)
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
