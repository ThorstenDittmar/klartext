# Project Onboarding

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** a filled `seed.toml` (the single config source) · the rendered configuration (settings, hooks, gates, inbox, CLI defaults) · the agent-team framework (`agents/` + roster) with the baseline roles · the wired memory + inbox directories · a first convergence · a passing bootstrap smoke-test
> **Activity / Activity Space:** Support the Team → stand up a new endeavour's operating system — its way of working, agent-team framework, collaboration fabric and configuration — from the method seed
> **External dependencies (referenced Resources):** the **method seed** bundle + its declared prerequisites — Claude Code (app + hooks), git, gh, a Python runtime, the `superpowers` plugin and the **Essence** baseline (both *declared-not-vendored*, see `../resources/`)
> **Enforcement:** ritual  ·  **NN:** ✓ (when standing up a new endeavour from the seed)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** the seed's bootstrap procedure (a `project-onboarding` skill is a candidate once the seed is built)

## Purpose

Stand up a **new endeavour's operating system** — its way of working, agent-team framework, collaboration
fabric and configuration — **from the method seed**, such that the new project can run the improvement loop
without re-deriving the method. This is the project-level sibling of [`agent-onboarding.md`](agent-onboarding.md):
that one integrates *an agent into an existing system*; this one **creates the system from nothing**.

Guards three failure modes: a project that **copies** the source endeavour (a fork) instead of *parameterizing*
it; a project de-source-ified by **global find-replace** (fragile — a literal missed anywhere breaks silently);
and a **half-stood-up** operating system (the method is imported but the hooks/gates are not wired, so nothing
is actually enforced — the RC2 "documentation, not a standard" failure, at project scale).

## Definition / delta

Onboarding proceeds **parameterize-before-render** — fill the single config source *before* touching any
template — in seven steps:

1. **Verify the prerequisites.** The seed is *referenced-not-vendored*: confirm the consumer environment has
   what the seed declares but does not ship — Claude Code (app + hooks), git, gh, a Python runtime, the
   `superpowers` plugin (at its pinned version), and the **Essence baseline** (the pinned meta-language the L3
   library stands on). A missing prerequisite is a stop, not a workaround.
2. **Fill the config source (`seed.toml`).** One file carries every endeavour-specific literal — project name,
   env prefix, memory/inbox directory, repo slug, worktree base, identity preamble, interpreter, product domain,
   the product CLI the gate watches, and the **WoW-CLI invocation name** (how the team invokes `<cmd> converge`,
   kept distinct from the project name). The authoritative key set is the renderer's `REQUIRED_KEYS` /
   `REQUIRED_LISTS` — they fail loud on a missing key, and `seed.toml` self-documents each one inline, so this
   prose stays illustrative, not a second source to drift. This is the
   **single decision** that drives every later artifact; nothing downstream is edited by hand. (The anti-pattern
   this closes: de-source-ification as a global `sed`.)
3. **Render the configuration from `seed.toml`.** Generate the parameterized artifacts — session settings +
   hooks, the pre-commit config, the way-of-working CI gates + their scripts, the inbox fabric, the CLI
   defaults — reading every literal from the config source, never re-typing it.
4. **Create the agent-team framework.** A directory per agent (start wrapper + tool allowlist + knowledge file)
   plus the roster, seeded with the **baseline roles** (a method/organisation role, an infrastructure role, an
   architecture role, a quality role, a coordination/product-owner role, and one cloneable domain-expert
   template). The consumer's own domain agents are added later via `agent-onboarding`.
5. **Wire the fabric.** Install the session-start identity + freshness hooks, the way-of-working gates and the
   pre-commit hooks; create the memory and inbox directories. Until this step lands, the imported method is
   documentation, not an operating system.
6. **First convergence + handoff.** Run the first `converge`; hand off to the new team: read the L3 library,
   fill the L2 enactment from the shipped skeleton + worked example, and define the domain agents via
   `agent-onboarding`.
7. **Verify against the DoD.** Run the **bootstrap smoke-test**: from the seed + a filled `seed.toml`, a fresh
   project stands up where the identity/freshness hooks fire, the gates run, the inbox works, a baseline agent
   is onboardable, and a first `converge` succeeds — with **zero source-endeavour literal** remaining in the
   **rendered + config outputs** (grep-checkable). That scope is deliberate: it targets the global-`sed`
   anti-pattern. As-is **method-library content legitimately cites the source endeavour as its worked example**
   (the L3 cards illustrate with the originating project) and is **out of this scope** — scrubbing it would
   destroy the worked example. The project is not "stood up" until this passes.

**Completion (Done):** prerequisites verified (or the stop is explicit) · `seed.toml` filled as the single
source — no by-hand literal edits downstream · configuration rendered from it · the agent-team framework exists
with the baseline roles · hooks + gates + memory/inbox wired · a first `converge` succeeded · the bootstrap
smoke-test is green with **zero source-endeavour literal** remaining in the rendered + config outputs (worked-example
citations in as-is method content excepted, per step 7).

**Enforcement note (generic).** A ritual owned by the team-formation / method role. Its non-negotiable core is
mechanizable as the **bootstrap smoke-test** (step 7): a fresh project stands up *and* carries no source-literal.
A project whose gates are not wired (step 5 skipped) is not onboarded — the method runs on top of nothing, the
project-scale form of "a rule without enforcement is documentation."

## Related

- [`agent-onboarding.md`](agent-onboarding.md) — the per-agent sibling (integrate into an existing system).
- The **method seed** bundle + its config source (`seed.toml`) and prerequisites contract.
- [`../resources/superpowers.md`](../resources/superpowers.md) + [`../resources/essence.md`](../resources/essence.md) — the *declared-not-vendored* dependencies a consumer must provide.
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.

> *No klartext L2 sibling: this is generic stand-up-a-project-from-the-seed guidance. klartext did not onboard
> itself from a seed (the seed is klartext's **export**); the seed and its `seed.toml` values live in their own
> home (the method-seed bundle), not as a separate enactment of this practice.*
