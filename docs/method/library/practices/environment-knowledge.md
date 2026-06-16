# Environment Knowledge

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** one environment Work Product per Resource (fact(s) + status tags + version-binding + Canary + dependency chain); a registered entry in the method register
> **Activity / Activity Space:** Support the Team → keep the team's operating model anchored to the actual environment
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual  ·  **NN:** ✓
> **Status:** living  ·  **Owner:** OE
> **Enacted as:** — (ritual; manual Canary where the tool is non-scriptable, mechanical Canary where it is)

## Purpose

Hold knowledge about the **development environment** — the tools a team *uses* but does not *build* — as
**version-bound, falsifiable** Work Products, so that no operating or architecture decision rests on an
environment assumption that has quietly gone stale. Gives every feasibility check a **shelf life**: the
version it was true for, a way to detect when it expires, and a list of what breaks when it does. Guards the
failure mode where a recorded environment fact silently drifts out of date and then drives a decision as if
still true.

## Definition / delta

An environment fact is a Work Product **about a Resource** (the tool). The practice runs when a load-bearing
fact is discovered/changes/refuted, after an environment update (run the Canary of every affected Work
Product), and before any decision that rests on an environment fact (confirm the version-binding still holds).

1. **Name the Resource & the fact** — which tool, which specific behaviour, as an empirical claim not an
   inference. Tag each fact **tested / observed-untested / inferred**; never let an untested claim pass as
   tested.
2. **Version-bind** — record the exact tool version/build the fact was verified against, plus date and
   verifier. A fact with no version-binding is **not a finished Work Product**.
3. **Write the Canary** — a concrete check that re-proves or breaks the fact. When the Canary breaks, the
   fact is **presumed invalid until re-verified**. Manual where the tool cannot be scripted.
4. **Map the dependency chain** — list the operating/architecture decisions that hang on this fact, so a
   broken Canary immediately shows the blast radius.
5. **Land & register** — write the Work Product at its repo home and register it. **Four-eyes:** the agent
   who ran the test owns/verifies the empirical content; the form/home owner is distinct.
6. **On refutation, supersede — never delete** — a refuted fact is marked *superseded* with rationale and
   its successor. A decision *against* an environment belief is method knowledge of equal rank to one *for* it.

**Completion (Done):** every fact names its Resource and is status-tagged · the Work Product is version-bound
(version + build + date + verifier) · a Canary exists that would break if the fact went stale · the
dependency chain is listed · empirical content carries a four-eyes sign-off · registered, and any refuted
predecessor marked *superseded* (not deleted).

**Enforcement note (generic).** Ritual — and mechanical is genuinely impossible where the subject tool
cannot be scripted (its Canary cannot be a CI check; it is a manual post-update checklist). Where the subject
is a scriptable tool, the Canary **should** be promoted to a mechanical check. The card must **never promise
automation the environment cannot deliver** — naming that honestly is the point.

## Related

- klartext enactment: [`../../enactment/practices/environment-knowledge.md`](../../enactment/practices/environment-knowledge.md)
- Produces Work Products of the kind catalogued under `enactment/environment/`.
- [`_card-template.md`](../_card-template.md) · the method register row in `enactment/method.md`.
