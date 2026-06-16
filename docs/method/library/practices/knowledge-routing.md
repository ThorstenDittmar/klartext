# Knowledge Routing

> **Essence type:** Practice
> **Advances Alpha:** Team (also advances Way of Working)  ·  **Work Products:** a classification of each unsaved insight by ownership · one knowledge briefing per not-own item (or an explicit "none") · self-stamped provenance on any shared-memory edit
> **Activity / Activity Space:** Support the Team → deliver knowledge that emerged in one member's session to its rightful owner
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (runs within every anchor)
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** the `knowledge-routing` skill (runs inside the `anchor` ritual)

## Purpose

Ensure that knowledge surfacing in **one member's session** lands with its **rightful owner** — even when it
appeared in the wrong domain context — without any member writing directly into another's files. Guards the
failure mode where a cross-domain insight is saved into (or lost from) the session where it happened to
appear, instead of reaching the domain that has authority over it.

## Definition / delta

Three load-bearing conventions plus a three-step run.

**Channel policy — "inbox is the floor, the doorbell is optional."** When there are two transport paths
between members (a durable file inbox and an ephemeral live ping), **one is the channel of record**:
- **Inbox = the floor (binding, durable).** Everything **action-relevant or persistent** — briefings,
  approval requests, handoffs, decisions — **must** land in the *recipient's* inbox. If it counts, it is on
  the floor.
- **Ping = the doorbell (optional, ephemeral).** Allowed only as an immediate nudge *in addition to* the
  inbox entry, or for pure action-free clarification. **Never the sole carrier** of an action-relevant item.
- **Reconciliation runs over the inbox.** A recipient works their inbox; reading it can **never** miss
  action-relevant work. Corollary: when sending, verify the **recipient slug** — a correctly-worded item in
  the wrong inbox is the same failure as no item.

**The user (relay) is always the channel.** No member writes directly into another member's files. Every
knowledge briefing goes through the relay, who decides and forwards.

**Memory-provenance self-stamp.** When the shared team memory is unversioned and all members write under one
identity, **whoever edits a memory file stamps themselves** (last-editor + date in the file's metadata) — the
only way to recover *who* last changed a shared, unversioned artifact.

**The run (inside anchor):**
1. **Classify each candidate** by the question *"is this in my domain, or am I just the session it appeared
   in?"* → **own knowledge** (normal save), **foreign** (belongs wholly to another), **boundary** (touches two
   members), **organizational** (touches team structure/collaboration).
2. **Formulate a briefing** for every not-own item (one per affected member for boundary knowledge;
   organizational knowledge → the team-method owner): from/to, type, context, content, and a concrete
   placement recommendation.
3. **Present to the relay**, separated from own-save proposals: show each briefing in full, ask
   forward / adjust / skip — **never forward or save without explicit confirmation**.

**Completion (Done):** every unsaved candidate classified by ownership · a briefing exists for each
not-own item (or an explicit "none affected") · action-relevant items addressed to the correct recipient
inbox (slug verified) · nothing forwarded or written into another member's files without confirmation · any
shared-memory edit self-stamped.

**Enforcement note (generic).** A ritual embedded in `anchor`. Mechanizable in parts (a health check can warn
on an un-stamped memory edit); the classification and the relay step stay human-judged.

## Related

- klartext enactment: [`../../enactment/practices/knowledge-routing.md`](../../enactment/practices/knowledge-routing.md)
- The host ritual: [`anchor.md`](anchor.md).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
