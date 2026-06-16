# Anchor — Session Safeguard

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** durable entries for every unsaved insight (at its agreed home) · routed knowledge briefings (or "none") · (on restart) a successor-seed handoff note · a short capture summary
> **Activity / Activity Space:** provisional — no kernel Activity Space (Way-of-Working-meta); Activity-Space extension deferred per Plan §4.1 → secure volatile session knowledge to durable storage before a context reset
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓ (North Star: no insight lost)
> **Status:** living (supersedes the former `pre-compact` practice — renamed because the ritual is no longer tied to `/compact`)  ·  **Owner:** OE
> **Enacted as:** the `anchor` skill

## Purpose

Before a context reset destroys it, **secure everything that lives only in the conversation** — decisions,
rationale, verbal instructions, open TODOs, work status, parked findings — to durable storage, so **no
insight is ever lost**. The "anchor" image: fasten the volatile chat knowledge to solid ground (disk), and
on a generation change drop a second anchor the successor session re-attaches to. Guards the
context-loss failure mode and its dangerous variant **False Persistence**: a summary that *claims* something
was saved when it never was.

## Definition / delta

**Determine the mode first** — the whole run branches on it:
- **Restart** (generation change: a `/clear` follows and a successor takes over) → all steps **including the
  successor seed**.
- **Checkpoint** (mid-session safeguard, work continues) → **skip** the successor seed (a stale handoff note
  in the mailbox is worse than none).

Then:

1. **Know what survives a reset.** Anything already on disk (the standing rules, the method document set,
   delegation tracking, memory files, code/comments/commit messages, issues, skill files) is safe. The blind
   spot is **everything that exists only in the conversation** — a `/clear` discards it, a `/compact`
   lossily summarizes it.
2. **Scan the conversation** for candidates across fixed categories: architecture decisions, rule changes,
   rationale (the *why*), verbal instructions, open TODOs, work status, parked findings. Collect
   generously — one item too many beats one missed.
3. **Persistence check.** For each candidate, decide **already saved** vs. **not yet saved** by actually
   looking at the durable home — never trust memory that it was saved.
4. **Route knowledge that isn't yours.** Each not-yet-saved item is classified: own-domain → save normally;
   anything belonging to another owner → a knowledge briefing for the relay (this is the **knowledge-routing**
   practice running inside anchor).
5. **Walk through with the decision-owner** — present what is already saved, then propose each new entry (own
   knowledge) and each briefing (others' knowledge); **never auto-save, always wait for explicit confirmation**.
6. **Save confirmed items, then verify the artifact (mandatory False-Persistence guard).** After all writes,
   inspect the actual changed files (e.g. version-control status / a directory listing) and reconcile them
   against the intended saves. **Trust the artifact, not the summary.**
7. **(Restart only) Successor seed.** Leave a handoff note where the successor will find it: current status
   (with references), open threads/parked findings/waiting briefings, and a concrete **wake prompt** (a fresh
   session does not act on its own until prompted). Verify this note exists and is non-empty — the seed is the
   loss insurance; it must not itself fall to False Persistence.
8. **Summarize**, then point to the next step. **Never run `/clear` or `/compact` yourself** — wait for the
   owner to trigger it. Prefer `/clear` (forces real prior persistence — exactly this ritual) over `/compact`
   (lossy, False-Persistence-prone).

**Completion (Done):** mode determined · conversation scanned across all categories · every candidate marked
saved/not-saved against its real home · not-own knowledge routed as briefings (or "none") · each new entry
confirmed by the owner before saving (no auto-save) · **artifact verified against the intended saves** · (on
restart) successor seed written **and** verified non-empty · summary given; the reset left to the owner.

**Enforcement note (generic).** A ritual, user-triggered. Its hardest core is non-negotiable: the
**artifact-verification** step (the False-Persistence guard) and, on a restart, a **verified** successor seed.
The knowledge-routing step is the embedded sibling practice. Mechanizable in parts (an audit hook can detect
an imminent reset; it cannot judge what is worth saving).

## Related

- klartext enactment: [`../../enactment/practices/anchor.md`](../../enactment/practices/anchor.md)
- The embedded routing step: [`knowledge-routing.md`](knowledge-routing.md) · the evaluation home for parked
  improvement candidates: [`retrospective.md`](retrospective.md).
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
