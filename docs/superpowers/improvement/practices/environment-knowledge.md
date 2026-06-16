# Practice: Environment Knowledge

> **Scope.** This document defines the **Environment Knowledge** practice — the repeatable way we hold
> knowledge about our **development environment** (the tools we *use* but do not *build*: the Claude Code
> app/CLI, git/GitHub, Supabase, macOS) as **version-bound, falsifiable** Work Products.
> **Out of scope.** Knowledge about the *product* we build (lives in code, ADRs, domain docs); the external
> reference assets themselves (those are **Resources** — home `assets-local/`). This practice governs our
> *documented understanding* of those tools, not the tools.
> **Anti-pattern guarded.** A recorded environment fact silently drifting out of date as the environment
> changes — and then driving a decision as if still true (**RC4**). Live instance: ADR-0010's
> *"cwd strukturell unmöglich"* premise outlived the app version it was true for and drove the entire
> terminal migration.
> **Language.** English — documentation-language rule.
>
> **Status:** active (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working
> **Source check:** Essence — a Practice that produces a **Work Product** about a **Resource**; both elements
> already in our meta-language (`semat-definition.md` §3). Pure composition, no Kernel change (no Eigensaft).

## Goal

Keep every load-bearing fact about our development environment **trustworthy over time** — so that no
operating or architecture decision rests on an environment assumption that has quietly gone stale.
Operationalizes the H01 guiding principle *"Before implementing: check feasibility against the environment"*
(`continuous-improvement.md` §0) by giving each such check a **shelf life**: the version it was true for, a
way to detect when it expires, and a list of what breaks when it does.

## Advances Alpha

**Way of Working** — each environment Work Product produced or refreshed keeps the team's operating model
anchored to the *actual* environment, not a remembered one.

## When to run

- A load-bearing environment fact is **discovered, changes, or is refuted** (the ADR-0010 class).
- After an environment **update** (app/CLI/tool version bump) → run the **Canary** of every affected Work Product.
- **Before any decision** that rests on an environment fact → confirm the fact's version-binding still holds.

## Steps

1. **Name the Resource & the fact.** Which tool (the Resource), which specific behaviour — an empirical claim,
   not an inference. Tag each fact **tested / observed-untested / inferred**; never let an untested claim pass
   as tested (that was the ADR-0010 error).
2. **Version-bind.** Record the exact tool version/build the fact was verified against, plus the date and who
   verified it. A fact with no version-binding is **not a finished Work Product**.
3. **Write the Canary.** A concrete check that re-proves — or breaks — the fact. When the Canary breaks, the
   fact is **presumed invalid until re-verified**. Manual where the tool cannot be scripted (see Enforcement).
4. **Map the dependency chain.** List the operating/architecture decisions that hang on this fact, so a broken
   Canary immediately shows the blast radius.
5. **Land & register.** Write the Work Product at its repo home (`environment/`) and register it in
   `method.md`. **Four-eyes:** the agent who ran the test owns/verifies the empirical content (typically
   DevOps); OE owns the form and the home.
6. **On refutation, supersede — never delete.** A refuted fact is marked *superseded* with rationale and its
   successor (mirrors the ADR + `method.md` retirement rule). A decision *against* an environment belief is
   method knowledge of equal rank to one *for* it.

## Work Products

- One **environment Work Product** per Resource (or coherent fact-cluster), carrying: the fact(s), their
  **status tags**, the **version-binding**, the **Canary** checklist, and the **dependency chain**.
  Home: `docs/method/enactment/environment/`.
- A registered row / entry in `method.md`.

## Completion Checklist (Done)

- [ ] Every fact names its Resource and is tagged tested / observed-untested / inferred.
- [ ] The Work Product is version-bound (tool version + build + date + verifier).
- [ ] A Canary exists that would break if the fact went stale.
- [ ] The dependency chain (what relies on the fact) is listed.
- [ ] Empirical content carries a four-eyes sign-off from the agent who verified it.
- [ ] Registered in `method.md`; any refuted predecessor marked *superseded* (not deleted).

## Enforcement

**Ritual (Enforcement Hierarchy level 2) — and mechanical is genuinely impossible for the flagship case.**
The Claude Code desktop app **cannot be scripted**, so its Canary cannot be a CI check; it is a **manual
post-update checklist** a human runs. (That non-scriptability is itself an environment fact — and part of why
this card exists.) Where the subject is a **scriptable** tool (git, Supabase, a CLI), the Canary **should** be
promoted to a mechanical check per the Architectural-Linting rule. The card must **never promise automation the
environment cannot deliver** — naming that honestly is the point.

## Notes

- **First enactment = retroactive formalization (2026-06-13).** DevOps + user had already played through the
  full check on the Claude app (cwd via the working-directory picker, `settings.json`/hooks via `/compact`,
  `/clear` reset, Canary a/b/c, dependency chain, version-binding v1.12603.1) — only the card was missing.
  The first Work Product (`environment/claude-code-app.md`) lifts that existing learning into the repo.
  Mirrors how the Improvement Step card was validated by self-application.
