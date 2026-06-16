# Agent Provenance

> **Essence type:** Pattern
> **Advances Alpha:** Team (one identity rendered across every substrate)  ·  **Work Products:** none (a provenance trailer attached to existing artifacts — commits, memory entries)
> **External dependencies (referenced Resources):** none
> **Enforcement:** mechanical (target: commit-msg hook + CI check) — ritual until the hook lands  ·  **NN:** ✓ (every method/agent commit)
> **Status:** living  ·  **Owner:** System Architect (rule, per ADR-0014) · DevOps (mechanism)

## Purpose

A klartext colleague has **one identity** rendered across every substrate it touches — inbox, team-memory,
and git. This pattern records that identity on the substrate where it was missing: the **git commit**, via
an `Agent:` trailer. Guards the attribution-gap failure mode: every agent commits under the single GitHub
identity `ThorstenDittmar`, so without the trailer a commit does not record *which* agent authored it.

## Definition / delta

Record agent provenance as a standard git **commit trailer**, in the message footer alongside the mandated
`Co-Authored-By:` line (additive, does not replace it):

1. **Base form** — `Agent: <slug>`, where `<slug>` is the `agents/<name>/` directory name. That directory
   name is the **SSOT** for identity — `team.yaml` carries metadata only and must not be the source.
2. **Spawn-aware form** — when a lead has spawned a sub-agent to do the work:
   `Agent: <lead> (spawned <task>)`. The **accountable identity is the lead**; the spawn is made visible.
   This fits the lead-and-spawn execution model (ADR-0012 / ADR-0013).
3. **Same identity everywhere** — the slug is the same one already rendered in the inbox `from`/`to` fields
   and in team-memory last-edited-by (contract clause **C5**). This pattern generalises C5 to git, closing
   the one substrate where the single GitHub identity hid the author.

**Completion (Done):** the commit footer carries a well-formed `Agent:` trailer · the slug is the
`agents/<name>/` directory name (not derived from `team.yaml`) · spawned work uses the
`Agent: <lead> (spawned <task>)` form · the trailer sits alongside `Co-Authored-By:`.

**Enforcement note (generic).** **Mechanical by design** (the most strongly enforceable rendering of the
one-identity model): a commit-msg hook adds/validates the trailer and a CI check rejects a method/agent
commit lacking it. Until the hook lands it is a **ritual** convention and will be applied unevenly. The
hook + CI touch the Infrastructure Perimeter and require the DevOps Briefing in ADR-0014. Open questions
(deferred to ADR-0014): exact CI scope (all commits vs method/agent paths), the non-agent bypass form, and
whether a helper lives in `api/cli.py` or purely in the hook.

## Related

- [ADR-0014](../../../adr/0014-agent-provenance-trailer.md) (the decision) · team-memory contract clause C5 ·
  [[four-eyes]] (identity is what makes executor/criteria-owner distinguishable) ·
  [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
