# Dependency Contract (instance): superpowers plugin

> **What this is.** The klartext-specific **Dependency Contract** for the `superpowers` plugin — the
> concrete clauses S1–S4 below. For *what a Dependency Contract is* (the generic element: when to forge
> one, the clause / blast-radius / falsifiable-check structure, the relation to Environment Knowledge's
> dependency chain), see the L3 element card:
> [`../../library/dependency-contract.md`](../../library/dependency-contract.md).
> **The dependency.** The `superpowers` Claude Code plugin (marketplace `claude-plugins-official`,
> pinned **5.1.0**) — the upstream home of the disciplines our `tdd` and `systematic-debugging` practices
> wrap. For provenance, the version pin, and the *referenced-never-vendored* rule see the L3 Resource
> card: [`../../library/resources/superpowers.md`](../../library/resources/superpowers.md).
> **Why a contract here.** This is a **seam**, like the memory substrate — but tilted toward the
> *external* face: we **own** the thin wrapper skills (`docs/superpowers/skills/tdd/`,
> `systematic-debugging/`) that *invoke* `superpowers:*`, but we **do not own** the disciplines those
> skills load. A wrapper card is written against a specific upstream invariant ("all rules apply without
> exception"); if that invariant shifts under us (plugin update, skill rename, content drift), the wrapper
> silently becomes a paraphrase of something that no longer exists. The contract turns that silent drift
> into a caught failure.
> **Language.** English — documentation-language rule.
>
> **Status:** draft v1 (2026-06-16) · **Owner:** OE (contract form + clauses) · DevOps (install + version
> pin in the environment) · QA (S2's wrapped-discipline accuracy, systematic-debugging) · **Advances
> Alpha:** Way of Working

## The seam — three parts

| Face | What | Modeled as | Owner |
|---|---|---|---|
| **Uncontrolled** (external) | the `superpowers` plugin itself — its skill *content*, skill *names*, the marketplace install, the version available | the **Resource card** (`../../library/resources/superpowers.md`) + the version pin; an upstream change is observed, not authored by us | DevOps (install/pin) + upstream (content) |
| **Controlled** (our artifact) | the thin wrapper skills `docs/superpowers/skills/tdd/SKILL.md` + `systematic-debugging/SKILL.md` that `invoke` the upstream skill, and the klartext delta they add (test pyramid, qa-review, qa-retro tail) | our own skill files + the L3/L2 wrapper cards | OE (cards) / QA (systematic-debugging accuracy) / DevOps (skill install mechanism) |
| **The seam** | the invariants below — *whichever* side provides them | **this Dependency Contract** | OE |

## The contract — invariants

Each clause states what must hold, its **blast radius** if violated, and its **falsifiable check** (the
mechanization that makes it checkable, or — where mechanization is not yet built — the explicitly-named
ritual that stands in).

| # | Invariant | Blast radius if violated | Falsifiable check | Holds today? |
|---|---|---|---|---|
| **S1** | The plugin **resolves at the pinned version** — `superpowers` 5.1.0 is installed and loadable in the consumer's Claude Code environment. | Both wrapper practices break: `tdd` Step 1 and `systematic-debugging` Step 1 invoke a skill that cannot load → the klartext deltas run on top of *nothing* → the Iron Law / root-cause discipline silently vanishes. | The plugin dir exists at the pinned path (`~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/`) **and** its `plugin.json` reports `"version": "5.1.0"`. Candidate for the session-health hook (DevOps); ritual until then. | ⚠️ **Aspirational** — install confirmed manually (5.1.0 present); not yet a hook check |
| **S2** | The **wrapped skills exist under the names our cards declare** — `superpowers:test-driven-development` and `superpowers:systematic-debugging` are present and carry their core discipline (TDD's *NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST*; debugging's *NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST*). | A rename or content gutting upstream means our wrapper invokes a skill that no longer loads (rename) or no longer enforces the invariant the klartext delta assumes (content drift) — the wrapper card becomes a paraphrase of a discipline that is gone (RC4 by omission). | `skills/test-driven-development/SKILL.md` and `skills/systematic-debugging/SKILL.md` exist under the pinned install **and** each still states its Iron Law. QA ratifies the systematic-debugging half (QA-owned discipline). Ritual today; mechanizable as a grep against the pinned install. | ⚠️ **Aspirational (ritual)** — verified by reading the pinned 5.1.0 install; QA-ratification pending for S2/debugging |
| **S3** | **Skill-invocation is the consumption seam** — our wrappers *load* the upstream skill (`invoke superpowers:<skill>`); they never *copy* its text. | If a wrapper inlines upstream content, we hold a second source of truth that drifts independently of the plugin (vendoring-by-paraphrase, RC4) — the contract can no longer tell whether "what we say TDD is" matches "what superpowers says TDD is". | The wrapper skill files and the wrapper cards contain a `superpowers:<skill>` invocation/declaration and **no restatement** of the upstream rules — only the klartext delta. Reviewable; candidate for a vendoring lint (SA). | ✅ (by construction — the current `tdd`/`systematic-debugging` skills are thin loaders) |
| **S4** | A **version bump is a deliberate, reviewed event**, not an automatic float — the pin (5.1.0) only moves when someone re-reads the wrapped disciplines and confirms the klartext deltas still compose. | An auto-updating plugin can change the wrapped discipline *under us* between sessions; the wrapper cards silently describe the wrong upstream. This is exactly the **Controlled Method Rollout** "breaking for a drifted consumer" case. | The version pin lives in the Resource card + this contract; bumping it requires re-ratifying S2 (the wrapped invariants still hold at the new version) and updating both wrapper cards in the same change. Convention today (no auto-update configured). | ✅ (convention — pin is explicit; no float configured) |

**S1/S2 — why a check and not just trust.** The plugin is consumer-installed (same class as the Essence
Kernel): on a fresh environment, or after a marketplace update, the version that resolves is *not*
guaranteed to be 5.1.0. S1 catches "not installed / wrong version"; S2 catches "installed, but the
discipline the wrapper assumes has moved." Both are silent at change-time — the wrapper still *runs*, it
just runs on top of something other than what its card declares. That silence is exactly the seam
condition the L3 element describes.

**S2 — QA ratification flag.** The `systematic-debugging` discipline is **QA-owned** (the
`qa-retro` tail composes on it). This sub-agent ratified S2's accuracy *as if QA* against the pinned
5.1.0 install (the Iron Law *NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST* is present; the four-phase
structure is present). **Real QA ratifies on wake** — until then S2's debugging half is provisional.

## Why a contract here (the lever this seam gives us)

Because we **own** the inner face (the wrapper skills + cards), the contract reveals a **design lever**,
not just risk to watch: with a purely external tool we could only observe + Canary; here we *build* the
wrapper to declare-not-restate (S3) and to pin-not-float (S4), so a violation on **either** side — an
upstream rename *or* a wrapper that drifted into paraphrase — is caught against the **same** clauses.
(The generic form of this lever is in the L3 element card.)

## Relationship to other elements

- **Dependency Contract (L3 element)** (`../../library/dependency-contract.md`) — the generic definition this file is an instance of.
- **superpowers Resource card** (`../../library/resources/superpowers.md`) — the referenced material, its provenance and version pin; this contract states what we *require* of it.
- **`tdd` / `systematic-debugging` wrapper practices** ([`../practices/tdd.md`](../practices/tdd.md), [`../../library/practices/systematic-debugging.md`](../../library/practices/systematic-debugging.md)) — the consumers whose blast radius the clauses name.
- **Controlled Method Rollout** — an upstream change that violates S2/S4 for a *drifted* consumer is **breaking** → barrier mode. This contract feeds that classification.
- **Memory-substrate contract** ([`memory-substrate.md`](memory-substrate.md)) — the sibling L2 instance; same clause/blast-radius/check shape, but tilted toward the *controlled* face (we build most of the substrate) where this one is tilted toward the *external* face (we build only the wrapper).

## Status & open

- **S1** (version resolves) — ⚠️ aspirational; install confirmed manually, hook check is a DevOps candidate.
- **S2** (wrapped skills exist + carry their Iron Law) — ⚠️ aspirational (ritual); verified against the pinned 5.1.0 install. **QA-ratification pending** for the systematic-debugging half.
- **S3** (load, never copy) — ✅ by construction.
- **S4** (pin is deliberate) — ✅ convention; no auto-float.
- **Open (OE/DevOps):** whether S1/S2 graduate from ritual to a session-health check that asserts the pinned install + greps the two skills for their Iron Law. Non-blocking; tracked as a candidate Improvement Step.
