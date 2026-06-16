# `docs/method/enactment/` — Layer 2: klartext's Method-in-use (enactment)

> **Path = classification.** Everything under this stem is **L2**: specific to **klartext's** runs,
> decisions, evidence and product. It is the *enactment* of the generic L3 Library by this one
> endeavour. The CI check (DevOps) rejects method content in the wrong stem and any mixed card.
> There is no `layer:` frontmatter field — the path classifies.

## What lives here (L2)

- **The Method-composition object** — klartext's method = *these* L3 Library practices, composed,
  with their lived Alpha states. The L2 counterpart to the L3 Library.
- **klartext-specific enactment of practices** — the bindings, checklists and conventions that a
  generic L3 card defers to (e.g. the klartext test pyramid, the domain-agent map, the app run flow).
- **Running record of the endeavour** — the Improvement Register, retrospectives, friction reports,
  QA learnings, lived Alpha-state evidence.
- **Environment facts** — our version-bound, falsifiable knowledge about the tools we *use*
  (Claude Code app/CLI, git, Supabase, macOS).
- **klartext-specific skills** and the L2 bindings of split ritual skills.

## What does NOT live here

- Generic, reusable definitions → [`../library/`](../library/README.md) (L3).
- Product/app code logic (that is the product, not the method).

## The split rule (why most cards are split, not moved)

The 2↔3 cut runs **through** each practice card: today a single file holds both the generic
definition and klartext's evidence. F0 splits each into an L3 stem (generic) and an L2 stem (this
file's tree). A card that wraps an external Resource (e.g. `tdd` over `superpowers`) keeps its
**generic composition declaration in L3** and its **klartext delta here in L2**.

> **Owner:** OE (form + classification) · domain owners ratify their own L2 content on wake ·
> **DevOps** enforces the path check. Decision record:
> [ADR-0013](../../adr/0013-separating-method-from-product.md).
