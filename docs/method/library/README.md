# `docs/method/library/` — Layer 3: the Practice Library (generic)

> **Path = classification.** Everything under this stem is **L3**: a generic, reusable method
> definition that holds for **any** endeavour using the practice — not specific to klartext's runs,
> decisions, evidence or product. A CI check (DevOps) rejects method content that sits in the wrong
> stem and any card that mixes generic definition with klartext-specific enactment. The path is the
> classifier — there is no `layer:` frontmatter field (a path cannot lie; frontmatter can drift).

## What lives here (L3)

- **Generic practice/pattern definitions** — one card per element, written so a different endeavour
  could adopt it unchanged. Use the template: [`_card-template.md`](_card-template.md).
- **The self-contained Essence summary/grounding** — our reference for the meta-language (the OMG
  Kernel & Language stay an **external referenced Resource**, never copied in here).
- **Generic skills** — the reusable core of a ritual skill (klartext-specific bindings go to L2).
- **Resource cards** — declarations of external material we *reference but do not produce*
  (e.g. the `superpowers` plugin, the Essence Kernel/Language). A Resource is **referenced, never
  vendored and never extracted** into this Library; a consumer installs it themselves.

## What does NOT live here

- klartext's runs, register, retros, friction, lived Alpha-states, environment facts, product →
  those go to [`../enactment/`](../enactment/README.md) (L2).
- A re-statement (paraphrase) of an external Resource's content. A card that wraps an external
  Resource **declares the dependency and states only its own composition/extension delta** —
  restating the Resource is vendoring-by-paraphrase (RC4: no second source of truth) and is **not**
  a well-formed L3 element.

## Why this stem exists

This realises the Essence **Library vs. Method-in-use** distinction (ADR-0013): a Library holds the
*stock* of separately-describable, composable practice **definitions**; the **Method-in-use** (L2)
is the composition actually lived by klartext. The single path-match serves three purposes at once:
classification, the CI path-scoping selector, and the `git filter-repo` selector for the eventual
L3 extraction — so the extraction runs mechanically, **provided** the objects here are well-formed.

> **Owner:** OE (form + classification) · **SA** reviews L3 well-formedness · **DevOps** enforces the
> path check. Decision record: [ADR-0013](../../adr/0013-separating-method-from-product.md).
