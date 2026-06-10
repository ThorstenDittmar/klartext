# Continuous Improvement Process — Way of Working of the klartext Multi-Agent System

> **Scope.** The single versioned home for our **way of working and its continuous improvement** — purpose,
> Definition of Done, project plan (phases), root-cause analysis, decisions + rationale, and the improvement loop.
> **Out of scope.** The meta-language reference (`semat-definition.md`), our term list (`semat-glossary.md`),
> individual Practice cards (`practices/`), and the raw post-mortem / inventory data
> (`docs/superpowers/plans/PENDING.md`). This document *references* those; it does not duplicate them.
> **Anti-pattern guarded.** Lost knowledge / advisory-only process living in chat (see §0 and RC1/RC2).
> **Language.** English — documentation-language rule.

> **Status:** Phase 1 complete · Phase 2 (Methodology Foundation) in progress · **Last updated:** 2026-06-09 ·
> **Maintenance owner:** OE (provisional)
>
> **This is a living document.** It is the *one* versioned place where we capture our way of working and its
> improvement — so it does not become the next point of loss. Not a one-off step: it culminates in a
> permanent improvement loop (§ 3).

---

## 0. Purpose and scope

After the first sprint (H01) we found that our way of working has systematic weaknesses. Before taking
measures, we want to proceed **structurally and completely** — instead of reacting ad hoc.

**Three risks this document guards against** (named by the user):
1. **Tangling (Verhäddern)** — we lose the overview of parallel measures and their dependencies.
2. **Side-effects** — a measure improves A and damages B without us noticing.
3. **Eigensaft** ("cooking in our own juice") — we reinvent procedures that are long established and proven
   in the field.

**Guiding principles** (derived from the H01 post-mortem):
- **Not everything at once.** Phases instead of simultaneity (this was a core H01 mistake).
- **Every step has a checkable DoD.** "Done" is a detectable state, not a feeling.
- **Before implementing: check feasibility against the environment.** Our tools (Claude Code, git, Supabase)
  constrain us — ideas must be mirrored against them.
- **Continuous, not one-off.** The process keeps improving itself.

**Data basis:** The findings from the H01 post-mortem, the storage inventory and the open decisions live in
`docs/superpowers/plans/PENDING.md` (sections "Post-Mortem H01 — Coverage-Tracker", "Inventur-Befund",
"Stand 2026-06-08"). This document builds on them.

---

## 1. Definition of Done (tree-shaped)

The DoD is hierarchical: the overall goal is reached when all phase DoDs are met; each phase DoD is met when
its criteria are met. This structure also forms the outline of the project plan (§ 2).

- [ ] **ROOT — The multi-agent system reliably improves itself.** *(North Star, 2026-06-09)*
  Load-bearing pillar: **no insight is ever lost** — every learning is captured, *without anyone having to
  remember to do it*. Loss-freeness, traceability and flow are **fruits** of this loop, not separate goals.

  > **Cross-cutting principle — Enforcement Hierarchy (applies to EVERY measure/rule):**
  > (1) **mechanical** enforcement where possible (hook, pre-commit, CI, branch protection) → (2) otherwise
  > anchored as a **fixed ritual** in a defined workflow (not left to memory) → (3) **never advisory-only**
  > (= the H01 mistake).

  - [ ] **The loop runs** (not "exists on paper") and is hardened against **capture loss**: every insight is
    captured **mechanically OR ritually** — never advisory-only.
  - [ ] Every decided measure is anchored per the Enforcement Hierarchy (mechanical / ritual / never advisory-only).
  - [ ] This document has a fixed maintenance owner and is updated after every sprint (= part of the loop, see § 3).
  - [ ] **Phase 1 — Problem & root-cause analysis (RCA) complete** *(scaffold)*
    - [ ] All problems from H01 captured and categorized (source: post-mortem + inventory)
    - [ ] Cause–effect chains captured explicitly (cause → effect → damage), not just a symptom list
    - [ ] Every documented symptom is mapped to exactly one RC OR explicitly marked *unexplained* (detectable —
      no gap stays silent)
    - [ ] The discipline confirmation is recorded (per discipline), not only done in chat
  - [ ] **Phase 2 — Target way of working defined (PM level)** *(scaffold)*
    - [ ] Desired target way of working described (how we *want* to work) — incl. the loop itself + the
      Enforcement Hierarchy
    - [ ] Comparison with established, highly-structured PM methods documented (at least FDD, V-Model; more as needed)
    - [ ] Comparison with modern approaches from the vibe-coding / AI-agent field documented
    - [ ] Synthesis: what we adopt, what we discard, **with rationale** (no Eigensaft, no blind adoption)
    - [ ] For every rule of the target way of working, the enforcement level is named (mechanical / ritual) —
      none stays advisory-only
    - [ ] The capture mechanism itself is defined as a concrete ritual or mechanically (not "we'll just write it down")
  - [ ] **Phase 3 — Feasibility checked** *(scaffold)*
    - [ ] Implementation plan for the target way of working exists
    - [ ] Feasibility checked against environment constraints (Claude Code, git/GitHub, Supabase, hooks, permissions)
    - [ ] Where the environment constrains: adaptation documented (what cannot be done 1:1, what is the substitute)
    - [ ] Side-effects named per measure (what could this measure break elsewhere)
    - [ ] Per measure, confirmed which enforcement level the environment *actually* allows; where the highest is
      not possible, the fallback is documented (cf. PreCompact hook: mechanical impossible → ritual)
  - [ ] **Phase 4 — Sequencing fixed** *(scaffold)*
    - [ ] Order / roadmap exists: what we tackle when
    - [ ] No "everything at once" bundles; dependencies explicit
    - [ ] Per step: owner + checkable DoD
    - [ ] The order respects the root-cause dependencies — e.g. artifact home first (RC1), then the gate on it (RC2)

---

## 2. Project plan (phases)

We work the phases **sequentially**. Only when a phase's DoD is met does the next begin. Each phase states:
goal, input (what we need), output (what is produced), owner candidates.

**Current roadmap (2026-06-09, user-confirmed):**
1. Branch protection on `main` + `ANTHROPIC_API_KEY` secret — *now* (DevOps).
2. Safety commit of today's work layer onto the salvage branch — *now*, just secure it (DevOps).
3. **Phase 2 (target way of working)** — the next big step.
4. **Salvage teardown deliberately AFTER Phase 2** — artifacts are placed into the structure *newly defined
   there* (once cleanly instead of twice). Rationale (user): the "right homes" are only known after Phase 2,
   because RC1/RC3 are solved there — placing earlier would mean sorting by the old/broken model.

> **Salvage branch policy (clarified 2026-06-09).** `salvage/h01-working-tree` is a **quarantine branch,
> never a merge candidate** — we do not merge it onto `main` (that would dump the broken H01 state). We
> **drain it artifact by artifact** into the right homes and then **discard the empty branch** (the teardown
> above, after Phase 2). Crucial distinction: today's method-foundation work is **forward work**, not salvage
> content — it belongs on `main` now and must not stay on the quarantine branch (where it accumulated only
> because that was the checked-out branch — a live instance of RC4/RC5). DevOps is coordinating the move to
> `main`; other forward work likely also stranded on salvage (compaction-monitoring scripts, ADR 0009) is the
> same class of problem and is flagged to DevOps.
>
> ⚠️ **Drain warning — `agents/oe/CLAUDE.md` diverged (2026-06-09).** `main`'s version received a forward
> edit (Method Keeper section) while the H01-era updates of the agent knowledge files (incl. the Hannibal row)
> remain on salvage, deliberately deferred. The future drain of `agents/*/claude.md` must **merge, not
> overwrite** — otherwise the Method Keeper section is lost (RC4-style loss at the seam).

### Phase 1 — Problem & root-cause analysis (RCA)  ·  *Status: complete*
> **Terminology:** In *our* (process) context this analysis is called **problem / root-cause analysis (RCA)** —
> deliberately NOT "Wirkmodell" or "Wirkzusammenhang", to avoid confusion with the *product's* Wirkgefüge /
> Wirkmodell.
- **Goal:** Understand the problem completely and as a cause–effect web — not just as a symptom list.
- **Input:** H01 post-mortem, storage inventory, agent feedback (all in PENDING.md).
- **Output:** A consolidated problem map. Each problem with: cause → effect → damage, and links to the others
  (which problems reinforce each other).
- **Owner candidates:** OE (consolidation) + all disciplines (confirmation). Content-wise possibly Hannibal.
- **Note:** Much is already gathered — this phase is mainly *consolidation + root-cause analysis + gap check*.

#### Problem map — RCA first draft (2026-06-09)

> **STATUS: Phase 1 complete (2026-06-09).** Six root causes (RC1–RC6), user-validated and confirmed across
> **all nine domain disciplines, recorded per discipline** — eight H01 participants plus the Community Expert
> as a **validated exclusion** (not a sprint participant; the RC model was checked against its domain
> retroactively and fits). The cross-check produced: RC6 new (tacit assumptions), RC4 + RC5 extended
> (lifecycle / observability), RC3 sharpened (shared interfaces) — no *unexplained* symptom. Parked as forward
> questions (not faults): DevOps↔UX channel, Technical Writer, B2 schema check. **All four Phase-1 DoD criteria
> met.**
>
> **Correction (2026-06-09) — a silent gap in our own RCA, caught and closed.** The cross-check was first
> labelled "8/8" but silently omitted the Community Expert (the 9th domain). Community had been dormant since
> 2026-06-06 (pre-sprint) — a non-participant — but that was never made *explicit*: it was dropped, not
> decided. A live instance of exactly what this initiative fights: a silent completeness gap + an unsurfaced
> assumption (RC6 / the DoD rule "no gap stays silent"). The user caught it. **Closed (2026-06-09):** Community
> queried directly, responded — confirms all six RCs against its domain, no unexplained symptom, recorded as an
> explicit validated exclusion (9th row below). *(Deeper remediation: a maintained team list makes such
> completeness mechanically checkable — see Phase 2, "Team list = Artifact Register pilot".)*

Data basis: Coverage-Tracker T1–T6, inventory categories A–F, triage findings (all in `PENDING.md`). Goal:
not to manage ~30 symptoms but to find the *few* drivers beneath them.

**Six root causes (RC):** *(RC6 + RC4/RC5 extensions from the discipline cross-check, 2026-06-09)*

- **RC1 — Key artifacts without a home.** *Cause:* no binding place/format for contracts, sign-offs, the
  process layer. → *Effect:* decisions live in chat / uncommitted / nowhere. → *Damage:* not checkable, not
  traceable, almost lost. *Explains:* T1, inventory-C, "process layer never committed", sign-offs only in chat.
- **RC2 — Rules advisory instead of enforced.** *Cause:* good rules as text/skill, but no gate at the point of
  action. → *Effect:* forgotten/skipped under pressure. → *Damage:* the same mistakes repeat. *Explains:* T6
  (task-readiness never invoked), T2 (no integration gate), T3 (no QA gate), branch protection off, negative
  constraints only in memory.
- **RC3 — Owner model incomplete.** *Cause:* the model assigns *file paths*, not *content/interfaces*;
  cross-cutting concerns + seams without owner; **shared/bidirectional interfaces without a defined owner**
  (consumer defines *what*, provider *how* — the seam between belongs to no one). → *Effect:* things fall
  between owners; role boundaries are not felt. → *Damage:* uncoordinated changes, no one maintains it, boundary
  crossings. *Explains:* "file owner ≠ interface owner" (fakes, `.storybook`, `debug.py`, cross-domain fakes),
  cross-domain port never escalated, audit test file on a foreign branch, `.semgrep` flat (no owner per rule
  group), **Hannibal too deep (role clear, but the boundary is not felt/enforced → also RC2)**.
- **RC4 — "Active" drifts against "recorded" + artifacts/dependencies without a lifecycle.** *Cause:* no sync
  trigger between running state (session/DB/installation) and the repo state; **artifact/dependency types have
  no validity/expiry/upgrade concept** (created, but no "becomes invalid when …"). → *Effect:* the active state
  silently diverges from the recorded one; artifacts age unnoticed. → *Damage:* stale permissions, lost skills,
  schema drift, stale plans, model upgrade without governance. *Explains:* C1, wrapper re-install, Supabase
  drift, token→CSS sync, `~/.claude` outside the repo, **plan documents without an expiry rule (UX/UI),
  provider model upgrade without a process (Audit)**. *(Remediation link: artifact register with lifecycle columns.)*
- **RC5 — Process/workflow not orchestrated (incl. missing shared situational picture).** *Cause:* no binding
  dispatch/dependency/merge process; roles/gates (QA, SA) not planned *by design* but bolted on afterwards;
  plans not verified against reality before dispatch; **no shared, verified actual state of the agents
  (observability) — coordination via mental models instead of CI/branch/PR status**. → *Effect:* parallel work
  collides, quality/architecture criteria arise too late, plans factually wrong, blind dispatch. → *Damage:*
  deadlocks, 5 duplicate commits, salvage needed. *Explains:* T5, T3 (QA as afterthought), T4 (plan stale/wrong),
  no merge owner, **cross-agent state observability missing (DevOps — Hannibal dispatches on assumptions instead
  of verified state; CI as shared source of truth)**.
- **RC6 — Tacit assumptions/contracts at seams are never SURFACED.** *Cause:* the step *before* recording is
  missing — implicit input assumptions at the domain seams are not pulled out and laid on the table as explicit,
  checkable candidates *before* building. *(Distinct from RC1: RC1 assumes the artifact was conceived and merely
  has no home — RC6 is "unborn", not "homeless".)* → *Effect:* no one checks an assumption that was never spoken.
  → *Damage:* **the 422** (the frontend assumed "the API accepts empty content" — never articulated); missing
  contract-test layer (you don't test a contract you never named). *Explains:* 422 core (Hannibal), "gate without
  a question grid" (SA — reviews don't surface the assumptions), "contract-test layer missing" (QA). *Owner of
  the missing step:* Hannibal (cuts the work packages, sees the seams).

**Worked example — the 422 was no accident:** intersection of **RC6** (the assumption "the API accepts empty
content" was never spoken) × **RC3** (the seam had no owner) × **RC5** (no process step "read the backend schema
before implementing", no gate). The validation rule even *existed* in the Pydantic schema (so not primarily RC1)
— it was just never *surfaced*, *owned* or *checked* as a contract. Had *one* of the three not held, it would
have surfaced while writing instead of at the user after 1 minute.

**Reinforcing loops:**
- RC1 → RC2: You cannot gate what is not an artifact (no contract → no contract check). **Order when fixing:
  artifact first, then gate.**
- RC3 → RC5: Unclear owners → coordination breaks at the seams.
- RC1 ‖ RC4: Siblings — "the real thing is not in the reliable record" (RC1: never recorded · RC4: recorded but
  drifting).

**Common root beneath the root:** *Implicit/convention instead of explicit/enforced/versioned.* The operating
model was built as documentation + good will, not as owned, durable, checkable machinery. All **six** RCs are a
variant of this. **The cross-check confirmed it twice over:** the three question-2 findings are themselves
further variants — implicit *assumptions* (RC6), implicit *validity* (RC4 lifecycle), implicit *state* (RC5
observability). Three disciplines deepened the root independently.

**Gap check:**
- Weakly mapped: "Hannibal too deep" = RC2 (role boundary advisory) + coordination vacuum (RC5); deliberately double.
- Not RCA but forward questions (parked): "Technical Writer yes/no", "DevOps↔UX direct channel" — "do we need
  X?", not "why did Y break?".
- Open for cross-check: is there a symptom that *none* of the RCs explains? *(Answered: none — see status above.)*

**Discipline cross-check (Phase-1 DoD: "recorded per discipline") — started 2026-06-09:**

| Discipline | Status | Objection / missing symptom |
|---|---|---|
| DevOps | ✅ RCs (with correction) | Correction: `.semgrep` flat → **RC3** (owner model), *not* RC4. **Q2 finding:** *cross-agent state observability* — no shared verified picture; Hannibal dispatches on assumptions instead of CI/branch state. Observability, not orchestration design (RC5). Candidate; CI as shared source of truth. |
| System Architect | ✅ RCs confirmed | **Q2 finding:** sign-off was timely, but **scope too narrow** — no enforced question grid for reviews (depth depends on Hannibal's ad-hoc question, not a standard). Candidate: extend RC2 (gate *without question grid*) or RC6. |
| QA | ✅ RCs confirmed | T3→RC5 shared. **Q2 finding:** *missing contract-test layer* between frontend unit (all mocked) and E2E (doesn't exist) — no test layer checks the contract. Missing *concept* (contract / consumer-driven tests), not just owner/process. |
| UX/UI | ✅ RCs confirmed | **Q2 finding:** plan documents **without a lifecycle/expiry rule** (plan stale at the Phase-1 merge, no one notices) — missing artifact-lifecycle concept. Refinement: 422 more RC5+RC3 than RC1/RC3 (the contract *existed* in the schema, was just unreferenced / without owner). |
| Narrative | ✅ RCs confirmed | **Q2:** no gap — all symptoms explained. Branch contamination → RC5 (path overlap). Side finding: the Semgrep gate caught `try/except`, but only at commit instead of at planning (gate at the wrong point). |
| Causal Model | ✅ RCs confirmed | **Q2:** no gap. **RC3 sharpening:** *shared/bidirectional* interface ownership — who owns the interface *between* consumer (CM) and provider (Audit)? No one; RC3 may explain it too weakly (more than "file path ≠ interface"). Extra symptom RC2: committed `# type: ignore` without a blocking gate. |
| Audit | ✅ RCs confirmed | Correction: model ID in **4** files (not 5). **Q2 finding:** *external-dependency lifecycle without a process* — who decides when/by what criteria provider models are upgraded? No owner/test/sign-off. Lifecycle, not drift. |
| Hannibal | ✅ RCs (with correction) | Correction: "Hannibal too deep" → **RC3** (role/owner discipline, boundary not felt → also RC2), *not* RC5. **Q2 finding (strong):** *tacit assumptions at seams are never SURFACED* — the 422 assumption was "unborn", not homeless. RC1 presupposes existence; here the step BEFORE is missing (make assumptions explicit + checkable before building). Candidate RC6. |
| Community | ✅ RCs confirmed (validated exclusion) | **Not a H01 participant** (last active 2026-06-06, pre-sprint) — no direct experience base; recorded as an *explicit, validated exclusion*, not a gap. Reviewed the six RCs retroactively against its domain (`api/*/user*`) and confirms all six; **no unexplained symptom**. Domain note: **RC6 hits hardest** — the auth flow carries many tacit assumptions (required registration fields, expected frontend error codes, session handling), none formulated as an explicit contract. |

### Phase 2 — Target way of working + method comparison  ·  *Status: in progress*
- **Goal:** Define how we *want* to work (PM level), and mirror it against proven methods.
- **Input:** Problem model from Phase 1.
- **Output:**
  - Description of the target way of working.
  - Comparison with **established, highly-structured PM methods** — e.g. FDD (Feature-Driven Development),
    V-Model, more by relevance (Scrum/Kanban, SAFe, Shape Up …).
  - Comparison with **modern approaches from the vibe-coding / AI-agent field** (market research — explicitly
    against Eigensaft).
  - **Synthesis with rationale:** what to adopt, what not, why.
- **Owner candidates:** OE + Hannibal (PM methodology). Research possibly with web-research support.

#### Phase 2 — Methodology Foundation (started 2026-06-09)

**Decision — our meta-language: Essence/SEMAT, used as-is (not modified).**
We adopt **Essence** (the OMG standard from SEMAT) as the *meta-language* for forging our way of working:
its fixed **Kernel** (seven Alphas, activity spaces) and its language for describing **Practices** and
composing them into a **Method**. We **use it as-is and only extend it** (our own Practices, our own tracked
things on top) — we never modify the standard. What we change *with* Essence is our PM process, not Essence
itself. This operationalizes Cockburn's *methodology per project*: forge a method from reusable Practices
instead of inventing one — explicitly against the **Eigensaft** risk (§0). Working hypothesis: if Essence
actively fights us in use, we revisit it **openly**, rather than quietly bending the meta for convenience.
Reference: `semat-definition.md`.

**Decision — we do NOT adopt Essence jargon wholesale; our own SEMAT glossary is the SSOT.**
Per DDD's **Ubiquitous Language**, shared meaning comes from one small authoritative glossary, not from
importing academic terms. We keep `semat-glossary.md` (English) and import from Essence only what earns its
keep — most valuably the idea **"Alpha = a thing with a defined state lifecycle"** (directly addresses RC4).
Two glossaries are kept **separate**: this *process/method* glossary (English) vs. the *product* ubiquitous
language (partly German domain terms like *Wirkgefüge*).

**Decision — documentation language (scoped).**
Technical/process/method documentation is written in **English only** (skills, practices, the SEMAT glossary,
this master document). Conversation with the user stays **German** (with English technical terms). Scope:
development/method documentation — **NOT** product-facing content, which deliberately carries German domain
terms. Recorded in memory (`feedback-code-language`).

**Decision — sequencing: thin top-down + one bottom-up thread, then back to the meta.**
Neither pure top-down (a meta-frame validated only against itself = our own anti-pattern RC2) nor pure
bottom-up (orphaned artifacts = RC1). Instead: (1) a deliberately **minimal** meta-frame (C-minimal),
(2) **one real Walking Skeleton / Tracer Bullet** (Cockburn) that threads the workflow (A) and one real
handoff (B) together — because A and B are coupled **at the seam**, (3) **return to the meta-frame with
evidence**. "Instantiate through use" (SEMAT / Gall's Law / learning organization).

**First Practice defined — Improvement Step** (`practices/improvement-step.md`).
The atomic continuous-improvement practice: *Pick up → Clarify & decide → Record → Route → Set next step.*
In Essence terms a Practice that advances the **Way-of-Working Alpha**; cross-checked against the standard.
Currently enforced as a **ritual**; promotion to a **Skill** deferred until after the first real run.
**This very decision block was produced by running the Improvement Step for the first time** (self-application).

**Refinements adopted (from the Essence cross-check):**
- Practices live as **separately-describable, composable units** (Practice Library under `practices/`), not as
  prose — so future practices (Walking Skeleton, Four-Eyes, Handoff) sit beside Improvement Step as peers.
- The Way-of-Working Alpha will get an **explicit state lifecycle** (the RC4 import) — deliberately deferred,
  not forgotten.
- The **seven Essence Alphas remain the skeleton we fill**; the glossary is seeded lean (from real runs), but
  the Kernel is not re-invented.

**Method survey (raw material, 2026-06-09).** Internet research produced a candidate pool mapped to our root
causes: Spec-Kit workflow skeleton (`Constitution → Spec → Plan → Tasks → Implement` + gates), the V-Model
principle (every artifact born with its verification counterpart), FDD's six per-feature milestones, XP's
"only one changes at a time" + CI/TDD, DDD (bounded contexts, context map, anti-corruption layer, ubiquitous
language) for the seam/ownership layer (RC3/RC6), Conway's Law as OE's design lever, SSOT/README-driven
development for homes (RC1), BDD/Specification-by-Example for surfacing contracts (RC6), Fail-fast against
deadlocks, and the orchestration primitives (handoff protocol, state checkpointing, failure recovery) for
RC5. These are **candidates to compose**, not methods to adopt wholesale.

**Method survey addendum — IJI Essence Practice Library contents (verified via browser, 2026-06-09).**
The free IJI hub publishes ready-made **Essence practice card decks** — i.e. established practices already
expressed in our meta-language. Available: **Alpha State Cards** (the Kernel itself; explicitly recommended to
"facilitate retrospectives" — candidate instrument for our retro: walk the Alpha states as the health grid) ·
**Scrum** (Foundations / Essentials / Accelerator) · **Scrum@Scale** (Scrum-of-Scrums, Executive) · **Agile
Essentials** (7 practices incl. **Agile Retrospective Essentials** — template for our missing retro card —
plus Product Ownership, Product Backlog, Agile Teaming, Daily Stand-up, Agile Development, Agile Timeboxing) ·
**Agile at Scale Essentials** · **Kanban** (Foundations, Team Kanban Essentials) · **BDD/ATDD cards**
(→ directly relevant to RC6 contract surfacing) · **User Story Essentials** (Cohn) · **Story Mapping**
(Patton) · **Use Case 2.0** · **Spotify Model Essentials** (org patterns — OE/Conway-relevant) · SAFe
principle decks · Method-Agnostic Agility cards. Decks are form-gated PDF downloads — deep content needs a
manual download by the user (the site blocks automated fetches).

**Minimal document set (English) + Document Scoping convention.**
The method now has a minimal, self-contained document set under `docs/superpowers/improvement/`:
`semat-definition.md` (self-contained meta-language reference — independent of the external SEMAT site, RC4),
`semat-glossary.md` (our terms), `practices/improvement-step.md` + `practices/document-scoping.md`, and this
master document. **New convention (a Practice):** every document opens with a **scope header**
(scope · out-of-scope + link · anti-pattern guarded → RC catalog / §0 · language). Recorded in
`practices/document-scoping.md`; applied across the set. The meta-language is referenced from `CLAUDE.md`
(§ Agent Roles, OE-owned) so agents read it on session start.

**Decision — integration vs. activation decoupled (2026-06-09).**
We integrate (merge to `main`) in **small, frequent increments** (XP/CI; keeps the trunk fresh, avoids a
long-lived branch that would regenerate RC4/RC5 drift), but we **batch activation** (the team agent-refresh)
to a **defined Way-of-Working milestone** (candidate state: *Foundation Established*). Rationale: merging to
`main` does not activate anything for agents — they load docs at session start — so work lands safely and
*dormant*; the expensive, coordination-heavy step is the refresh (C1), which we trigger once at a coherent
status rather than after every merge. This honors both small-batch integration **and** the user's instinct
"activate at a defined status" — applied to the right lever (activation, not integration).

**Deferred (queued, not lost):** (1) ~~SA briefing — documentation-language rule into `CLAUDE.md`
§ Language~~ **done (SA, commit `4445ae1` on salvage)**; (2) ~~migrate the German body to English~~
**done 2026-06-09**; (3) **land the method foundation on `main`** (forward work, not salvage content) via
DevOps (feature branch `docs/h01-method-foundation` → PR → CI → merge; **Go given 2026-06-09**, with a
diff-verification gate) — **decoupled** from the team refresh; (4) **team refresh batched to a Way-of-Working
milestone** (candidate: *Foundation Established*, after the Walking Skeleton); (5) the Walking Skeleton.

**Open / next:** run the **Walking Skeleton** (decide: retrospective H01 thread vs. fresh small task) to
pressure-test C-minimal, then expand the meta-frame with evidence.

**Instrument candidate — artifact register** *(user, 2026-06-09):*
A *continuously maintained* list of **artifact types** with metadata — distinct from the one-off storage
inventory (a problem snapshot). Columns: artifact type · storage location · volume · owner · consumer · change
frequency · rituals/processes that use it · *(candidates:)* versioned? (yes/no/where) · enforcement level of the
storage.
**Effect:** addresses RC1 (every type has a documented place), RC3 (owner + consumer explicit → "file owner ≠
interface owner"), supports RC2 (where does the guard attach?) and RC4 (where is a drift check worthwhile). →
a potential **central instrument**, not a side list. Established pattern (asset register / data catalog /
CMDB-lite).
**Open:** columns final · location · who maintains · update ritual (the register itself must be hardened against
"stale" — otherwise it drifts, RC4 on itself).

**Team list = pilot of the Artifact Register** *(decided 2026-06-09):*
A dedicated, OE-maintained **team roster** (agent · domain · owner · session-id · status [active/dormant/
offboarded] · `start.sh`/`claude.md` paths), used by all for **broadcasting and expert search**, updated as the
**on/offboarding ritual** (integrates with the `agent-onboarding` skill). In Essence terms it is the work
product of the **Team Alpha**.
**Effect:** addresses RC1 (the "team truth" had no checkable home — that is *why* the Community Expert slipped
through), RC4 (reconciles the *declared* roster in `CLAUDE.md` against the *running* state in `list_sessions` —
the two drift, as the dormant Community session showed), RC3 (domain→owner for routing).
**Why it matters here:** the roster is **Artifact-Register-shaped** (type/home/owner/consumer/lifecycle/ritual)
→ designated the **pilot** that validates the register design, and a strong **Walking Skeleton candidate**
(small, real, produces an artifact, exercises the on/offboarding ritual). **Build deferred to Phase 2 with the
register** — not now, to avoid pre-empting the register and to avoid parallel-thread tangling (risk #1).

**Decision — `method.md` (our Essence Method document) + Library/Method distinction** *(2026-06-09):*
Trigger: inventorying the existing "mischmasch" (skills, rituals, briefings, gates) to map it into Essence
logic. We nearly invented a new concept ("method inventory") — a check against the standard (anti-Eigensaft)
showed Essence already defines both halves: a **Method** is "the composition of a kernel and a set of practices
to fulfill a specific purpose"; a **Library** is the catalog of practices from which methods are composed.
Consequence: created **`method.md`** as our Method document — the *permanent* register of our method's elements
(element · Essence type · Alpha · enforcement · card status); `practices/` is our **Practice Library**; the
card-status column is the only *temporary* (migration-diagnostic) part. **SSOT sharpened:** the glossary defines
terms only; `method.md` lists elements; cards hold content. **Maintenance ritual:** `method.md` is updated in
the same Improvement Step that adds/changes/retires an element. **Side find:** our own reference
(`semat-definition.md`) lacked the Library element → backfilled in the same step (a knowledge-base gap is
closed the moment it is found). Key diagnostic from the initial fill: most lived practices are
*enacted-but-not-described* (the inverse of RC1), and `task-readiness` is the one remaining **advisory-only**
skill (T6/RC2).

**Decision — anchoring Essence-thinking** *(2026-06-09):*
"Always think in the meta-language when process is discussed" cannot be enforced mechanically — so it is
anchored at the chokepoints every process conversation passes through, and the anchoring is itself **described
in the meta-language**: (1) **Activity** — the Improvement Step practice gained a mandatory **Classify** step
(locate the topic in Essence terms + KB-first standard check *before* solutioning; would have caught both
near-inventions of this session automatically); (2) **Pattern** — OE's knowledge file gained a **Method
Keeper** role section (loads at every OE session start → survives sessions and compaction); (3) **Competency
(kernel extension)** — **Method Literacy**, levels per Essence (1 *Assists* … 5 *Innovates*); gives onboarding
and the team refresh a *measurable* target (every agent ≥ level 2 *Applies*) instead of a vague "everyone
should know it". Context: the standard-check discipline had come from the **user** twice in one session — the
goal of these anchors is that the check comes from the structure, not from the user's vigilance. Agents are
covered via `CLAUDE.md` § Way of Working (activation at the team refresh).

**Way-of-Working Alpha instantiated** *(2026-06-10):*
The full kernel state checklists are now in our KB — **`alpha-states.md`**, extracted from the IJI Alpha
State Cards (`assets-local/alpha_state_cards_ecards.pdf`; checkpoint content **CC BY 4.0 SEMAT Inc.**, read
visually from the image-only PDF). This delivers the formerly deferred item "WoW state lifecycle".
**First assessment (honest):**
- ***Principles Established* = 5/6.** Stakeholders agree ✅ (user drove and approved the principles) · tool
  needs agreed ✅ · approach recommended ✅ (Essence + practice composition + enforcement hierarchy) ·
  operational context understood ✅ (RCA 9/9) · practice & tool constraints known ✅ (C1, hook limits, TCC …).
  **Pending: "team actively support principles"** — the 9 other agents haven't been activated yet; completes
  with the team refresh.
- ***Foundation Established* = in progress (~1.5/6).** Gaps understood ✅ (`method.md` known-gaps + RCA) ·
  key practices & tools selected ⚠️ partial (2 cards, 10 enacted-uncarded, survey pool; retro card missing) ·
  practices-needed-to-start agreed ❌ · non-negotiables ⚠️ not marked per practice · capability gaps ⚠️
  (Method Literacy defined, not assessed) · integrated way of working available ❌.
**Consequence:** the team-refresh milestone (*Foundation Established*) is now **checklist-checkable** instead
of a feeling; the refresh completes the last *Principles* checkbox and starts *In Use*. The open *Foundation*
checkboxes are, in effect, the remaining Phase-2 to-do list.

**Decision — Retrospective practice composed (2026-06-10).**
Built by **comparative selection** (user rule: not the first option, the best-fitting one), from the
downloaded IJI decks (`assets-local/`): **adopted** from *Agile Retrospective Essentials* — the activity
skeleton (*evaluate previous actions first* → identify → prioritize → agree actions) and, verbatim, the
**Improvement sub-alpha** (*Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use*)
— this closes the "check effectiveness" gap (RC2): unverified measures now stay visibly stuck in the register.
**Replaced:** *Mad/Sad/Glad* (emotion-based, human-specific) by an **alpha-walk** over the state checklists
(`alpha-states.md`) — evidence-based, fits an agent team; IJI itself recommends the alpha cards for retros.
**Added (both gaps from `method.md`):** a defined **learnings home** (`learnings/`, mirror of `qa-learnings/`)
and the **Improvement Register** (§3). **Trigger rule:** event-based (work-package end / milestone /
significant incident), never wall-clock. Relation: `qa-retro` stays as the incident-triggered sibling.
Card: `practices/retrospective.md`. **This unblocks the 422 Walking Skeleton** (retro readiness was the
prerequisite).

**Pulled-forward findings (2026-06-09) — context / memory management:**
From a first market research (Anthropic "Effective context engineering"; JetBrains Research; Claude Code
docs/guides), triggered by the compaction concern:
- **Three established techniques** (Anthropic): (1) **structured note-taking / external memory** = continuously
  writing to durable files (our PENDING.md/claude.md) — the *primary* loss-protection technique; CLAUDE.md
  survives compaction (re-read from disk). (2) **Proactive compaction at a threshold** (~60% utilization, with
  preservation instructions) instead of reactive auto-compact (~75–90%). (3) **Sub-agent architecture** =
  isolate context, return only the distillate.
- **Important clarification:** *pre-compact ≠ compaction.* Note-taking **secures** knowledge but does not shrink
  context; compaction **shrinks**. The two belong paired (secure first, then shrink).
- **Trigger always utilization-/turn-based, never wall-clock-based.** Too-aggressive compression costs more in
  the end (re-acquisition).
- **Status quo for us:** note-taking ✅ (strong), sub-agents only partly (peer sessions isolate domain context,
  but the OE chat itself offloads little), proactive threshold compaction ❌ (missing).

**Open question for the target way of working (user, 2026-06-09):**
Sub-agents save context (leaner OE chat, less frequent compaction) **but cost user visibility** and can lose
real session context (cf. "simulated Hannibal" — deliberately discarded). → Define: **where** visibility in the
chat matters vs. **where** lean context via sub-agent (result only) matters more. Candidate rule of thumb:
sub-agent for closed, context-light tasks (research, broad search, "read X → return the conclusion"); chat for
anything where oversight / real context matters.

**Constraint questions for DevOps (for Phase 3 — feasibility) + findings (2026-06-09):**
- **Context-% threshold:** ❌/⚠️ UNCLEAR. No documented %-trigger. `autoCompactWindow` (integer 100K–1M) exists,
  but the docs don't say whether it is the *trigger* threshold or the *target size* after compaction → only
  experiment, no reliable auto-trigger.
- **PreCompact hook:** snapshot ✅ · **inject context/instructions into compaction ❌ (not possible)** ·
  block+turn return ⚠️ only via `exit 2` (error feedback to Claude, *not* a clean curation turn). `matcher: auto`
  vs. `manual` separable.
- **Auto-persist:** technically feasible (headless shell hook writes files), but as a skill rebuild / parallel
  track = **OE-domain decision**.
- **Conclusion:** A "golden" automatic curation gate before compaction is **not buildable** in this environment.
  Primary protection stays **note-taking**; available quick win = snapshot/audit hook (backstop + visibility);
  proactive compaction stays **discipline** (no native auto-trigger).

**Decided (2026-06-09) — compaction monitoring (feedback mechanism, not protection):**
- **Hook** (DevOps, live 2026-06-09): writes per compaction `auto`/`manual` + branch + ISO time to
  `.claude/compact-log.txt` (gitignored, local). Plus a PreCompact transcript snapshot for `auto` events →
  `.claude/compact-snapshots/` (heuristic, low risk). Team-wide via `.claude/settings.json` → captures all
  sessions; also shows *which* session runs to the edge most often.
- **Evaluation: local cron job (DevOps).** Checks the log at a slow cadence for new `| auto |` entries and
  alerts on a find; then hands off to OE + user for the measures discussion. = KVP loop step 4 (check
  effectiveness). Frequent auto-compacts = indicator that we don't compact proactively often enough.
  **Trailing signal — it measures, it does not prevent.**

**Why a local cron (rationale — deliberately documented):**
- **Not a cloud schedule:** the log is project-local + gitignored → a remote/cloud schedule (which only clones
  the repo) cannot see the file.
- **Not an OE session-start ritual:** a cron runs *independently of any open session* → catches auto-compacts
  even when no OE session is active (e.g. other agent sessions compact while OE sleeps). More robust than a
  session-dependent ritual.
- **Role separation:** the cron *detects + alerts* (script); *evaluation + measures* stay with OE + user.
- **IaC obligation:** the cron definition belongs in the repo as code + installation via `setup.sh` — **no
  manual crontab edit**, otherwise the cron itself would be a new untracked drift point (cf. C1 / wrapper
  re-install: "running state vs. repo state").

**Concrete implementation (DevOps — live since 2026-06-09, launchctl loaded):**
- **launchd** instead of cron (cron deprecated on macOS, skips sleep cycles). Agent:
  `~/Library/LaunchAgents/com.klartext.compact-monitor.plist`.
- **Cadence:** hourly (`StartInterval 3600`).
- **Alert:** macOS notification (`osascript`) **+** digest file `.claude/compact-monitor-digest.txt`
  (gitignored) — push + pull; OE can additionally read the digest at session start.
- **State:** line counter in `.claude/compact-log-lastcheck` (gitignored), `wc -l` diff → grep on `| auto |`.
- **IaC:** `scripts/check-compact-log.sh` + `scripts/com.klartext.compact-monitor.plist.template`
  (`@@REPO_DIR@@` placeholder) + `setup.sh` installation (`launchctl load`).
- **Notification framing:** trailing signal ("too late, compact proactively earlier next time"), not "compact now".
- **Known limitation:** **macOS-only** — launchd does not exist in Codespace/Linux; the monitor does not run
  there. Accepted.

**TODO (open, 2026-06-09) — pre-compact as a process step:**
- *When* should pre-compact (note-taking securing) fire automatically? Candidates: good-night / end-of-day
  message, after a retro, after a commit/merge, at natural break points.
- *How* do we design this **safely without prompting the user** (unattended auto-persist: writing files without
  `AskUserQuestion`)? Touches the pre-compact skill = OE domain; linked to DevOps finding Q3 (auto-persist mode).

### Phase 3 — Implementation plan + feasibility/constraints  ·  *Status: planned*
- **Goal:** Check whether the target way of working is implementable in *our* environment, and where it must be adapted.
- **Input:** Target way of working from Phase 2.
- **Output:**
  - Implementation plan.
  - Feasibility check against environment constraints (Claude Code: skills/hooks/sub-agents/cross-session;
    git/GitHub: branch protection/PR/CI; Supabase; permissions).
  - Documented adaptations where the environment constrains.
  - Side-effect analysis per measure.
- **Owner candidates:** DevOps (environment feasibility) + SA (architecture compatibility) + OE.

#### Known constraints & required operational mechanisms (growing list)

**C1 — Agent refresh after a skill / `start.sh` change** *(user, 2026-06-09)*
- **Constraint:** Changes to skills (`docs/superpowers/skills/`, `~/.claude/skills/`) or to start scripts
  (`agents/*/start.sh`) only take effect after a **restart of the affected agent session** — `claude.md`,
  permissions and skills are loaded at session start. A running session keeps working with the old state.
- **Risk:** The refresh is forgotten after a change → an agent keeps working with stale permissions/knowledge
  without noticing. Recurs reliably.
- **Required mechanism (to establish):** ensure the refresh is triggered/reminded after such a change.
  Candidates: (a) a fixed part of the change DoD ("skill/`start.sh` changed → restart affected agents");
  (b) a guard/hint that flags the needed refresh when writing to these paths; (c) tracking which sessions are
  affected. Related to the maintenance hook "wrapper re-install / `klartext skills sync`" (repo capability,
  PENDING.md) — both are "running state vs. repo state drifts". Owner: OE (process) + DevOps (technical
  reminder/hook if any).

### Phase 4 — Sequencing / roadmap  ·  *Status: planned*
- **Goal:** Decide *when* we tackle *what* — deliberately staggered.
- **Input:** Implementation plan + feasibility from Phase 3.
- **Output:** Roadmap with order, dependencies, owner and a checkable DoD per step.
- **Owner candidates:** Hannibal (planning) + OE.

---

## 3. KVP loop (permanent)

This process does not end with Phase 4. The improvement itself becomes a recurring cadence:

- **Trigger:** sprint end (or a defined milestone).
- **Step 1 — Retro:** what went well/badly? (Data basis: concrete incidents, not impressions.)
- **Step 2 — Feed in:** findings flow back into this document (the problem model § Phase 1 grows).
- **Step 3 — Adapt:** the target way of working / roadmap are adjusted where needed.
- **Step 4 — Check effectiveness:** did an earlier measure *really* fix the problem? (If not, back into the loop.)
- **Owner:** OE maintains the loop; all disciplines provide input.

> **Enacted (2026-06-10):** this loop is now operationalized by the **Retrospective practice**
> (`practices/retrospective.md`). Step 4 is mechanized via the **Improvement sub-alpha** (adopted from IJI:
> *Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use*) — tracked in the register
> below. Learnings home: `learnings/`.

### Improvement Register (Improvement sub-alpha instances)

| Improvement | Origin | Owner | State | Evidence / next check |
|---|---|---|---|---|
| Branch protection on `main` (6 required checks) | RCA RC2 (2026-06-09) | DevOps | **In Use** | validated through PRs #45/#46/#48 — gate held, naht-checks ran |
| Compaction monitoring (hooks + launchd digest) | compaction concern (2026-06-09) | DevOps | **Trialed** | live; evaluate at next retro: were auto-compacts caught early? |
| Classify step in Improvement Step (Essence-first thinking) | two Eigensaft near-misses (2026-06-09) | OE | **Trialed** | applied since introduction; evaluate after a few more runs |

> Open (to clarify with the user, noted in PENDING.md): do we need an explicit **sprint-start/end flag** as a
> trigger for this loop? And: how do we prevent `/compact` from losing knowledge mid-loop?

---

## 4. Open points about this document itself

- **Final home / mkdocs navigation:** This file lives under `docs/superpowers/improvement/`. Whether it is
  included in the published docs site (mkdocs nav) touches the Infrastructure Perimeter (DevOps) and the docs
  structure question (SA) — both still open from the H01 post-mortem. Until then the file is versioned in git and
  thus secured against loss; the *official* inclusion follows.
- **Confirm maintenance owner finally:** provisionally OE.
