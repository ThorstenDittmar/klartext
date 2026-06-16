# Environment Knowledge — klartext enactment

> **Scope.** klartext's enactment of the **Environment Knowledge** practice: our environment Resources, the
> Work Product home, the four-eyes ownership split, and the flagship non-scriptable case.
> **Out of scope.** The generic definition and the six steps — see the L3 card. Knowledge about the *product*
> we build (lives in code, ADRs, domain docs); the external reference assets themselves (those are
> **Resources** — home `assets-local/`).
> **Anti-pattern guarded.** A recorded environment fact silently drifting out of date (**RC4**). Live
> instance: ADR-0010's *"cwd strukturell unmöglich"* premise outlived the app version it was true for and
> drove the entire terminal migration.
> **Language.** English — documentation-language rule.
>
> **L3 definition:** [`../../library/practices/environment-knowledge.md`](../../library/practices/environment-knowledge.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Way of Working · **NN:** ✓ (before an env-fact-dependent decision; after a tool update)

## klartext bindings

- **Our environment Resources:** the Claude Code app/CLI, git/GitHub, Supabase, macOS — the tools we *use*
  but do not *build*.
- **Work Product home:** `docs/method/enactment/environment/` (one file per Resource or coherent
  fact-cluster), plus a registered entry in `method.md`.
- **Four-eyes ownership:** the agent who ran the test owns/verifies the empirical content (typically
  **DevOps**); **OE** owns the form and the home.
- **H01 guiding principle:** operationalizes *"Before implementing: check feasibility against the
  environment"* (`../continuous-improvement.md` §0).
- **Source check:** Essence — a Practice that produces a Work Product about a Resource; both elements already
  in our meta-language (`../../library/semat-definition.md` §3). Pure composition, no Kernel change.

## Enforcement (klartext)

**Ritual (Enforcement Hierarchy level 2) — and mechanical is genuinely impossible for the flagship case.**
The Claude Code desktop app **cannot be scripted**, so its Canary cannot be a CI check; it is a **manual
post-update checklist** a human runs. (That non-scriptability is itself an environment fact — and part of why
this card exists.) Where the subject is a **scriptable** tool (git, Supabase, a CLI), the Canary **should** be
promoted to a mechanical check per the Architectural-Linting rule.

## Evidence / learnings

- **First enactment = retroactive formalization (2026-06-13).** DevOps + user had already played through the
  full check on the Claude app (cwd via the working-directory picker, `settings.json`/hooks via `/compact`,
  `/clear` reset, Canary a/b/c, dependency chain, version-binding v1.12603.1) — only the card was missing.
  The first Work Product (`../environment/claude-code-app.md`) lifts that existing learning into the repo.
  Mirrors how the Improvement Step card was validated by self-application.
