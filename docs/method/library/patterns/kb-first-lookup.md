# KB-First Lookup

> **Essence type:** Pattern
> **Advances Alpha:** Way of Working (keeps the team's own reference authoritative)  ·  **Work Products:** none (a lookup discipline; may trigger a backfill into an existing reference)
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** —
> **Status:** living  ·  **Owner:** OE (pattern form)

## Purpose

Answer a method/reference question by consulting the **team's own reference first**, the **web only on a
miss**, and **backfilling the gap in the same step**. Guards two failure modes at once: reinventing concepts
the team already defined (web-first drift), and leaving the reference permanently incomplete after a miss.

## Definition / delta

For a question the team's own knowledge base might already answer:

1. **Own reference first** — consult the team's own reference (method document set, glossary, ADRs) before
   any external source. If it answers, stop — no external lookup needed.
2. **Web on a miss** — only when the own reference does not answer, consult the external standard / web.
3. **Backfill the gap in the same step** — when the external lookup fills a gap the own reference *should*
   have covered, record the answer back into the own reference immediately, so the next lookup hits it.
   A miss without a backfill leaves the gap open for the next reader.

**Completion (Done):** the own reference was consulted first · the web was consulted only after a miss ·
any gap found on the miss was backfilled into the own reference in the same step (or explicitly judged
out of the reference's scope).

**Enforcement note (generic).** Ritual; the lookup order resists mechanization, but the backfill step is
checkable (a recorded miss should leave a reference edit). Invoked inside the **Improvement Step** practice
(step 2, Classify) when locating a topic in the meta-language.

## Related

- [[method-keeper]] (who locates the topic before solutioning) ·
  [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
