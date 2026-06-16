# Document Scoping — klartext enactment

> **Scope.** klartext's enactment of the **Document Scoping** practice: which anti-pattern catalog the
> header references, and our promotion plan.
> **Out of scope.** The generic definition and the header shape — see the L3 card. Conventions specific to a
> single document type live in that document.
> **Anti-pattern guarded.** Wrong home / content drift — readers and agents putting the right content in the
> wrong document (see `../continuous-improvement.md` §0 / RC1).
> **Language.** English — documentation-language rule.
>
> **L3 definition:** [`../../library/practices/document-scoping.md`](../../library/practices/document-scoping.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working · **NN:** —

## klartext bindings

- **Anti-pattern catalog.** The "Anti-pattern guarded" line references our catalog: the root causes
  **RC1–RC6** and the three risks in `../continuous-improvement.md` §0 (Verhäddern / side-effects /
  Eigensaft). A dedicated `anti-patterns.md` will be extracted **only if** the catalog outgrows the RCA.
- **Language.** Method/process/technical docs are English (documentation-language rule); product-facing
  content keeps German — the header is written in the document's own language.

## Enforcement (klartext)

Currently a **ritual** (Enforcement Hierarchy level 2). Candidate for promotion to **mechanical**: a lint/CI
check that fails when a Markdown file under our docs lacks the scope header.

## Evidence / learnings

- The split itself (F0.1-P2) applies the header convention to every new card.
