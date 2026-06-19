# Seed Manifest

> **Essence type:** Work Product
> **External dependencies (referenced Resources):** none (it *references* the declared-not-shipped resources — see the prerequisites contract below — but owns no external material itself)
> **Enforcement:** mechanical (the assembly step reads it; a completeness check asserts every shipped path is listed exactly once)  ·  **NN:** ✓ (a seed without a manifest is not assemblable)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** `seed/MANIFEST.toml` (klartext's worked instance) + the assembly step that reads it

## Purpose

The **authoritative inventory of a method seed** — and, under the manifest-driven assembly model, its
**keystone**: the single list the assembly step reads to produce a consumable bundle. Every part of the seed
appears here exactly once, tagged with **how** it travels (verbatim, rendered, generated, or merely declared).
Two failure modes drive it: a seed assembled from an **implicit** file set (whatever happens to be in a
directory — unlistable, uncheckable, the RC1 anti-pattern at bundle scale), and a seed that silently **carries
product content** because nothing enumerated what is in vs. out. The manifest makes both **derivable**: the
inventory is the completeness contract.

It pairs with two siblings: [`practices/method-isolation.md`](practices/method-isolation.md) produces the cut
(what is method vs. product); the manifest **records** that cut as a checkable inventory;
[`practices/project-onboarding.md`](practices/project-onboarding.md) consumes the assembled bundle.

## Definition / delta

### Disposition taxonomy

Every entry carries exactly one **disposition**, mapping the export plan's five categories (§1) onto an assembly
action:

| Disposition | Category | Assembly action |
|---|---|---|
| `as_is` | ① As-is | pulled **verbatim** from the live repo at `path` (no stored copy — single source of truth) |
| `template` | ② / ③ | rendered from the config source (`seed.toml`) to `target` |
| `config_source` | ③ | the `seed.toml` itself — the consumer **fills** it; everything else reads from it |
| `generated` | new | produced by the assembly step (e.g. the render mechanism's output, the bundle tree) |
| `declared` | ④ | a **prerequisite the importer provides** — never shipped, never vendored (see contract) |
| `exclude` | ⑤ | product *Fachlichkeit* — never travels (listed so the boundary is explicit, not silent) |

### Manifest format (the concrete instance)

The worked instance is `seed/MANIFEST.toml` — one table per entry:

```toml
[[entry]]
path        = "docs/method/library/**"   # source in the live repo (or the template path)
disposition = "as_is"                     # one of the taxonomy values
target      = "docs/method/library/"      # where it lands in the assembled bundle (template/generated)
note        = "the L3 practice library"   # optional
```

The assembly step iterates the entries: `as_is` → copy from live `path`; `template` → render to `target`;
`declared`/`exclude` → never copied (recorded for the completeness check only).

### Prerequisites contract (the `declared` entries)

What the importer must already have for the assembled bundle to run — declared, **never vendored**:
Claude Code (desktop app + hooks), git, gh CLI, a Python 3.x runtime, a per-project memory directory, the
**`superpowers`** plugin (see [`resources/superpowers.md`](resources/superpowers.md)) and the **Essence
baseline** (the pinned meta-language, see [`resources/essence.md`](resources/essence.md)). A missing
prerequisite is a stop, not a workaround (cf. `project-onboarding` step 1).

### Completeness rule

Every path the seed ships appears in the manifest **exactly once**. The mechanizable core: an assembly-time
check that (a) every `as_is` source resolves in the live repo, (b) every `template` renders, and (c) no shipped
path is unlisted — the RC1 "implicit/unlisted, cannot be checked" guard, applied to the bundle. This is the
manifest's enforcement; without it the inventory is documentation, not a contract (cf.
[`standards-charter.md`](standards-charter.md) §1).

## Related

- [`practices/method-isolation.md`](practices/method-isolation.md) — produces the cut the manifest records.
- [`practices/project-onboarding.md`](practices/project-onboarding.md) — consumes the assembled bundle.
- [`standards-charter.md`](standards-charter.md) — the "rule + check" the completeness rule applies.
- `enactment/method-seed-export-plan.md` §1 (the five categories), §2 (seed anatomy), §7 (the build/assembly
  phases) — klartext's worked example.
