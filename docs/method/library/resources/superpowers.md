# superpowers

> **Essence type:** Resource
> **Advances Alpha:** — (a Resource is referenced material, not a Practice — it advances no Alpha on its own; the practices that *wrap* it do)
> **Work Products:** none (a Resource produces no Work Product — it is consumed, not authored, by us)
> **Activity / Activity Space:** — (not an Activity; it is the material a wrapping Practice draws on)
> **External dependencies (referenced Resources):** none — **this card *is* the external thing**; it declares the dependency rather than depending further
> **Enforcement:** convention (the install + version pin is a convention; the wrapping practices carry their own enforcement)
> **NN:** —
> **Status:** living  ·  **Owner:** OE (the Resource-card form + the reference rule); DevOps (the install mechanism + version pin in the environment)
> **Enacted as:** the installed Claude Code plugin (marketplace `claude-plugins-official`, plugin `superpowers`, pinned **5.1.0**); the `superpowers:*` skills it ships

## Purpose

`superpowers` is an **external skills plugin** for Claude Code — the upstream home of the generic
disciplines our way of working composes on top of (TDD, systematic debugging, brainstorming, plan
writing, code review, git worktrees, …). It is the same *class* of object as the **Essence
Kernel/Language**: material we **reference but do not own and do not produce**.

This card exists so the dependency is **declared, not vendored**. The plugin's content lives upstream
(`github.com/obra/superpowers`, installed under `~/.claude/plugins/cache/…/superpowers/5.1.0/`); our
repo holds only this *pointer* to it and the klartext **delta** cards that wrap it. Restating the
plugin's skill content inside our repo would be vendoring-by-paraphrase (RC4 — a second source of
truth) and is forbidden.

## The reference rule — referenced, never vendored, never extracted

`superpowers` is governed by the L3 Resource rule (`_card-template.md`, Type-specific notes):

- **Referenced** — our practice cards name `superpowers:<skill>` as an *External dependency*; they do
  not copy its text.
- **Never vendored** — the plugin's skill files are not committed into the klartext repo. (Our
  `docs/superpowers/skills/` holds *our own wrapper skills* — the thin `tdd` / `systematic-debugging`
  loaders that invoke the upstream skill — not the upstream skills themselves.)
- **Never extracted into L3** — when the L3 Library is extracted (`filter-repo`) to travel to another
  endeavour, the **referenced material does not travel** (a consumer installs the plugin themselves,
  exactly as they install the Essence Kernel themselves). **This card, however, does travel** — it is a
  normal L3 object; the extraction author must *not* exclude Resource cards from the L3 stem
  (SA ratification, PR #137).
- **A consumer installs it themselves** — same contract as the Essence Kernel/Language: the dependency
  is satisfied in the *consumer's environment*, not by shipping a copy.

## Provenance & version binding

| Field | Value |
|---|---|
| **Marketplace** | `claude-plugins-official` |
| **Plugin** | `superpowers` |
| **Upstream** | `github.com/obra/superpowers` (author Jesse Vincent, MIT) |
| **Version pin** | **5.1.0** (the version our wrapper cards are written against) |
| **Install location** | `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/` (consumer-local; not in the klartext repo) |
| **Surface we consume** | the `superpowers:*` skills (e.g. `superpowers:test-driven-development`, `superpowers:systematic-debugging`) |

The version pin is what the **L2 Dependency-Contract instance** checks against: a wrapping practice is
written against a specific upstream discipline, so an upstream change *under us* is a contract concern,
not a silent drift. See [`../enactment/contracts/superpowers.md`](../enactment/contracts/superpowers.md).

## Which of our practices depend on it

| klartext practice | wraps |
|---|---|
| [`practices/tdd.md`](practices/tdd.md) | `superpowers:test-driven-development` |
| [`practices/systematic-debugging.md`](practices/systematic-debugging.md) | `superpowers:systematic-debugging` |

(Other `superpowers:*` skills — brainstorming, writing-plans, requesting-code-review, using-git-worktrees,
… — are available in the environment and used directly without a klartext wrapper; only those we
*extend* get a wrapper card. New wrappers add a row here.)

## Related

- [`../_card-template.md`](../_card-template.md) — the Resource-card type note + the wrapper rule.
- L2 contract instance: [`../enactment/contracts/superpowers.md`](../enactment/contracts/superpowers.md) — the invariants our way of working relies on *from* superpowers.
- L3 element card the contract instances of: [`../dependency-contract.md`](../dependency-contract.md).
- [ADR-0013](../../adr/0013-separating-method-from-product.md) — method/product separation (why a referenced Resource is declared, never extracted into the product).
