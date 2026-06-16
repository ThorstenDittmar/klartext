# Agent Onboarding

> **Essence type:** Practice
> **Advances Alpha:** Team  ·  **Work Products:** the new agent's directory (start wrapper + tool allowlist + knowledge file) · a roster entry · a roles-table entry · a handoff message
> **Activity / Activity Space:** Support the Team → integrate a new specialist member into the multi-agent team with a defined domain
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (when adding an agent)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** the `agent-onboarding` skill

## Purpose

Integrate a new specialist agent into a multi-agent team **with a clearly bounded domain**, such that the
agent can start working without colliding with existing members and without a coordination bottleneck.
Guards two failure modes: an agent whose write-domain overlaps an existing one (silent contention), and an
agent that exists in conversation but is invisible to the team's start/coordination tooling (no roster entry,
no roles entry).

## Definition / delta

Onboarding proceeds top-down — **define the domain before touching any file** — in six steps:

1. **Clarify the domain.** Name the agent; fix its **write domain** (which paths it owns), its **read-only**
   needs, and check for **overlap** with an existing agent. Narrow domains are safer. The domain is the
   single decision that drives every later artifact — do not start creating files until it is settled.
2. **Create the agent's home.** A directory per agent holding three artifacts: a **thin start wrapper**
   (delegates to the central launcher — no logic duplicated per agent), a **tool allowlist** (one grant per
   line, read by the launcher; mandatory entries for the shared delegation-tracking work product), and the
   slot for the knowledge file. These must reach the integration branch *before* the first session, because
   the launcher reads them at start.
3. **Register the role.** Add the agent to the team's **roles/boundaries table** so its domain is part of the
   single source of truth every other member reads.
4. **Write the knowledge file.** The agent's own durable identity: role, write-domain (paths + rationale),
   read-only domain, domain-specific standards, its skills, the briefing protocol, and an open section the
   agent extends itself. Auto-loaded at session start — no explicit read needed.
5. **Commit together.** Directory + roles entry + skills land as one change — a partial onboarding (domain
   declared but tooling missing) is the failure mode this step closes.
6. **Hand off.** Send the new agent a self-contained welcome: how it is started, where its files live, how
   cross-agent messages travel (always via the relay — no agent writes into another's files), what it may do
   without asking, and how it routes knowledge that belongs to others.

**Completion (Done):** domain named and checked for overlap before any file is touched · start wrapper +
allowlist + knowledge file exist and are on the integration branch before first start · the agent is in the
roles table **and** the team roster · everything committed in one change (no partial onboarding) · a
self-contained handoff message was sent.

**Enforcement note (generic).** A ritual owned by the team-formation role. Mechanizable in parts (a lint that
every roster/roles/allowlist trio is consistent for each agent directory). The roster + roles entry are the
non-negotiable core — an agent the start tooling cannot see is not onboarded.

## Related

- The team roster Work Product · the roles/boundaries table (the role SSOT).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.

> *No klartext L2 sibling: the skill is generic add-an-agent guidance; the klartext-specific bindings it
> references (launcher path, worktree layout, `team.yaml`, the roles table in `CLAUDE.md`, the inbox relay)
> live in their own homes — they are not a separate enactment of this practice. If a klartext-only onboarding
> rule emerges that is not already carried by those homes, add an `enactment/practices/agent-onboarding.md`
> sibling then.*
