# Practice: Document Scoping

> **Scope.** This document defines the **Document Scoping** practice — the cross-cutting convention that
> every document opens with a scope header.
> **Out of scope.** Conventions specific to a single document type live in that document; this is only the
> cross-cutting rule.
> **Anti-pattern guarded.** Wrong home / content drift — readers and agents putting the right content in the
> wrong document (see `continuous-improvement.md` §0 / RC1).
> **Language.** English — documentation-language rule.
>
> **Status:** active (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working

## Goal

Every document declares, at its very top, **what belongs in it and what does not** — so content lands in the
right home, and any reader (human or agent) immediately knows the document's boundaries.

## The header (apply to every document)

Place this block directly under the document title, **in the document's own language**:

> **Scope.** This document holds &lt;X&gt;.
> **Out of scope.** &lt;Y&gt; belongs in &lt;link&gt;, not here.
> **Anti-pattern guarded.** &lt;named anti-pattern&gt; — see &lt;reference&gt;.
> **Language.** &lt;language&gt; — documentation-language rule.

- **Scope** — one sentence: what content this document is the home for.
- **Out of scope** — what is easily confused with it but belongs elsewhere, **with a link to where**
  (mark `TBD` if that home does not exist yet).
- **Anti-pattern guarded** — the named failure mode this boundary prevents, referencing our anti-pattern
  catalog: the root causes **RC1–RC6** and the three risks in `continuous-improvement.md` §0
  (Verhäddern / side-effects / Eigensaft). A dedicated `anti-patterns.md` will be extracted **only if** the
  catalog outgrows the RCA.
- **Language** — the document's language, per the documentation-language rule.

## Work Products

- A scope header at the top of every document.

## Completion Checklist (Done)

- [ ] The document opens with the four-line scope header.
- [ ] "Out of scope" links to the correct alternative home (or marks it `TBD`).
- [ ] "Anti-pattern guarded" names a failure mode and references the catalog.
- [ ] The header is written in the document's own language.

## Enforcement

Currently a **ritual** (Enforcement Hierarchy level 2). Candidate for promotion to **mechanical**: a lint/CI
check that fails when a Markdown file under our docs lacks the scope header.
