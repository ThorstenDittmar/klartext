# ADR Mechanism

> **Scope.** The generic, transferable **mechanism** for recording significant decisions as **Architecture/method
> Decision Records (ADRs)** — the template, the numbering, the Proposed→Accepted lifecycle, the gate, and
> supersession-with-provenance. A seed artefact: a consumer adopts the *mechanism* and fills it with *their own*
> decisions.
> **Out of scope.** Any specific endeavour's ADR *content* — those are example fillings, not normative (§4). The
> generic Essence meta-language (`semat-definition.md`); the collaboration gate this lifecycle invokes (its rule
> lives with the roles/landing-path).
> **Anti-pattern guarded.** Consequential decisions that live in chat / uncommitted / nowhere (RC1); a decision
> silently overwritten so its predecessor and the reason for the change are lost (RC4 at the decision layer).
> **Language.** English — documentation-language rule.

## 1. What an ADR is

An **ADR** is a numbered, ratified, durable record of one significant decision — its **context**, the
**decision**, and its **consequences**. It is the mechanism by which a team makes a consequential choice
**explicit, checkable and traceable** instead of letting it live in conversation. This document defines the
mechanism; it is **transferable as-is**. The endeavour that ships this seed has its own ADRs — those travel only
as **worked examples** (§4), never as decisions a consumer must adopt.

A decision earns an ADR when it is **consequential and not easily reversed** — an architectural choice, an
operating-model rule, a cross-cutting convention. Small, local, reversible choices do not need one.

## 2. The template

Every ADR is a file `NNNN-kebab-title.md` (a monotonically increasing number + a short title) carrying:

- **Status** — `Proposed` · `Accepted` · `Superseded by NNNN` (the lifecycle state, §3).
- **Decided by** — the **decision-owner / ratifier** (who has the authority to ratify).
- **Author / Sign-off** — who drafted it · who **reviewed** it (the gate, §3).
- **Relates to / Supersedes / Superseded by** — provenance links to sibling and predecessor ADRs.
- **Context** — the forces and the problem; *why* a decision is needed now.
- **Decision** — what was decided, stated plainly.
- **Consequences** — what follows, **positive *and* negative/risks** (an ADR with no named downside is usually
  incomplete).

## 3. The lifecycle

1. **Proposed.** The author (typically the domain owner of the decision) drafts the ADR with status `Proposed`.
2. **Gate / review.** A designated reviewer signs off as a **persistent review comment** on the change — never
   chat-only (a review comment is forgotten under pressure; a recorded artefact is not). In an environment where
   all authors share one platform identity (so platform self-approval is blocked), the **review comment itself is
   the conformant sign-off artefact** — the formal "approve" button is not required.
3. **Ratified → Accepted.** The **decision-owner ratifies**; the status flips `Proposed → Accepted`. Author,
   reviewer and ratifier are distinct roles even when the same person sometimes fills two of them.
4. **Supersession with provenance.** An accepted ADR is **never silently overwritten or deleted**. When it is
   replaced, a **later ADR supersedes it**: the old one's status becomes `Superseded by NNNN`, the new one
   carries `Supersedes NNNN` and **states what changed and why**. The decision history stays reconstructable.

## 4. Transferable mechanism vs example fillings

This is the same cut as the method/product separation (the generic mechanism travels; the lived content does
not):

- **Transferable (adopt as-is):** the template (§2), the numbering, the `Proposed → Accepted` lifecycle, the
  review-comment gate, and the supersession-with-provenance rule (§3). A consumer wires these to its own
  reviewer/ratifier roles.
- **Example fillings (read as models, not adopt):** the source endeavour's actual ADRs — typically the
  **operating-model** decisions (the agent operating model, the method/product cut, the agent-provenance trailer,
  the convergence model) — ship as **worked examples** that show the mechanism in use. A **supersession pair**
  (one ADR superseding an earlier one, with the provenance link intact) is the most valuable example to ship,
  because it demonstrates the one rule that is hardest to infer from a template alone.

## 5. Related

- The **method/product cut** ADR is itself the keystone worked example — it both *uses* this mechanism and
  *defines* the generic-vs-lived cut this section applies.
- The **roles / landing-path** — the gate in §3 (review-comment sign-off, decision-owner ratifies) is wired to a
  team's reviewer roles; a consumer binds it to its own.
- [`_card-template.md`](_card-template.md) · referenced from the method register `enactment/method.md` (a top-level reference doc, like `semat-definition.md` — no Practices/Patterns row).
