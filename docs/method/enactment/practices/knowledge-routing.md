# Knowledge Routing — klartext enactment

> **Scope.** klartext's enactment of the **Knowledge Routing** practice: the domain-agent map, the concrete
> channels (file inbox + app DM), and the C5 memory-provenance binding.
> **Out of scope.** The generic definition (channel policy, user-is-the-channel, self-stamp convention, the
> three-step run) — see the L3 card. The host ritual (`anchor` enactment); domain roles (`CLAUDE.md`).
> **Anti-pattern guarded.** Cross-domain knowledge stranded in the session it appeared in, or carried only on
> the ephemeral channel and missed by the recipient (RC2 / the #108 mis-addressing incident).
> **Language.** English — documentation-language rule (the skill body is German).
>
> **L3 definition:** [`../../library/practices/knowledge-routing.md`](../../library/practices/knowledge-routing.md)
> **Status:** living (ritual) · **Owner:** OE · **Advances Alpha:** Team, Way of Working · **NN:** ✓ (runs within anchor)

## klartext bindings

- **Domain-agent map (who owns what).** The classification routes to the agent who owns the topic, per the
  roles table in `CLAUDE.md § Agent Roles & Boundaries`:

  | Agent | Domain (routing target for…) |
  |---|---|
  | OE | multi-agent structure, onboarding, collaboration, the method (`agents/`, cross-agent skills) — **also the home for all organizational knowledge** |
  | Hannibal | project leadership, planning, coordination of large work packages |
  | DevOps | infrastructure, CI/CD, tooling (gatekeeper) |
  | System Architect | architecture decisions, coding standards (`CLAUDE.md`, `docs/adr/`, arch Semgrep rules) |
  | UX/UI | React components, frontend (`frontend/src/`) |
  | QA | tests, coverage, frontend criteria (`api/tests/`, qa Semgrep rules, `verify.md`) |
  | Narrative Expert | narrative domain backend (`api/*/narrative*`) |
  | Causal Model Expert | Wirkgefüge backend (`api/*/causal_model*`) |
  | Audit Expert | verification procedures, claim extraction (`api/providers/`) |
  | Community Expert | user/community backend (`api/*/user*`) |

  Authority is **expertise**, not file-ownership: e.g. a gap in the verification criteria routes to QA even
  though the file is named `verify.md` and the topic "sounds frontend."

- **Channels.** File inbox = `scripts/inbox.sh send/read` (the floor of record); app DM via
  `ccd_session_mgmt` (the doorbell). Action-relevant items go to the correct recipient's **inbox**.

## Memory-provenance binding (C5)

Shared memory lives at `~/.claude/klartext-team-memory/` (unversioned, one write identity). Every edit
self-stamps the file frontmatter `metadata` (`last-edited-by: <slug>`, `last-edited-at: <YYYY-MM-DD>`). It is
a ritual convention (memory is not in CI); a health check warns on an un-stamped change. Contract clause:
`../contracts/memory-substrate.md` (C5 — self-stamp; mechanical detection deferred, mtime unreliable).

## Enforcement (klartext)

A **ritual** (Enforcement Hierarchy level 2), embedded in the `anchor` ritual. The C5 self-stamp is backed by
a warn-only health check.

## Evidence / learnings

- #108 (2026-06-14): an action-relevant gate item ("#111 needs OE-gate + merge") never reached OE's inbox —
  it was mis-addressed to DevOps and reached OE only via the verbal relay. Lesson encoded in the channel
  policy: verify the recipient slug; the inbox is the binding floor.
