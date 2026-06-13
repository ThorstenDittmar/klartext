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
> ⚠️ **Drain warning 2 — quarantine actively removes (2026-06-10, Hannibal).** Files captured *untracked*
> into the salvage safety-commit are tracked **only there**; a checkout back to `main` deletes them from the
> working tree. These files are **operationally missing now**, not "parked for later": verified cases
> `agents/hannibal/` (drained back via next increment), 2 H01 plans, ADR 0007+0008. The teardown inventory
> must therefore start with the category "already removed by checkout" — see the Improvement Register row.
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

**Next step (set 2026-06-10): the 422 Walking Skeleton — run in a FRESH session.**
Decision made (was: "retro thread vs. fresh task" → **the retrospective 422 thread**, it hits the costliest
H01 wound directly). Subject: the seam that broke H01 — the **"empty content" contract** between frontend
(consumer) and narrative backend (provider). Thread it cleanly through the method: **surface the contract**
(RC6) → **name the seam owner** (RC3) → **QA writes the missing contract test** (their Q2 finding) → real
handoff via Hannibal, **with `task-readiness` enforced this time** (the last advisory gap, T6/RC2).
Participants: Hannibal (cut + dispatch), UX/UI + Narrative Expert (the two seam sides), QA, OE observing.
Close with the **first real run of the Retrospective practice** (alpha-walk, feed the Improvement Register,
learnings to `learnings/`). Double value: pressure-tests C-minimal under load *and* the missing contract-test
layer exists afterwards. Then: back to the meta-frame with evidence.
*Unread material (registered in `assets-local/`, needed later for TDD/Teaming/Stand-up cards): Agile
Essentials sheets 5–9, ATDD/TDD deck.*

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
**Re-assessed at retro 1 (2026-06-10):** *Foundation Established* ≈ **4/6** (up from ~1.5/6) — key practices &
tools selected ✅ (3 described cards incl. Retrospective; enacted set registered in `method.md`) · gaps
understood ✅ · capability gaps understood ✅ (two-tier competencies now on the retro card; team assessment
pending but the target is defined and the refresh planned) · non-negotiables ⚠️ (mechanical gates listed in
`method.md`, not yet marked per practice) · practices-needed-to-start ⚠️ (named in the 422 next-step block, not
yet validated) · **integrated way of working available ❌ — the blocking checkbox; exactly what the 422 Walking
Skeleton validates.** No regression against the first assessment.
**Re-assessed at retro 2 (2026-06-10, H01-422 close):** *Foundation Established* = **5/6** — the skeleton
validated the integrated way of working end-to-end (gated dispatch → TDD → qa-review → E2E-before-merge →
enacted merge protocol → captures → retro), so "integrated way of working available" ✓ and
"practices-needed-to-start agreed" ✓ (validated in use). **Single open box: "non-negotiables marked per
practice"** — agreed action at retro 2 (OE, `method.md` flag). When it closes: **team-refresh milestone
fires.** Work alpha H01-422: **Closed** (lessons: `learnings/2026-06-10-h01-422-retrospective.md`).
**🏁 Foundation Established REACHED (2026-06-10, post-retro-2 actions):** NN flags live in `method.md` →
**6/6**. The Way-of-Working alpha stands at *Foundation Established*; **the team-refresh milestone is DUE**
(batched activation: every agent reads the method doc set, Method Literacy ≥ 2 target → completes
*Principles Established* 6/6 and starts *In Use*). Executed in the same block: element-sweep step + deviation
clause on the retro card (self-audit findings 1+2 closed structurally), Merge-Protocol card
(`practices/merge-protocol.md`), 6 element-sweep finds registered in `method.md`, start.sh permission audit
(9 scripts fixed — only Hannibal's declared PENDING.md access; stale "DevOps only" headers noted, role SSOT
says OE). Open from the retro-2 action list: the pre-compact multi-agent fix bundle (next OE step).
**Team-refresh tally** (explicit confirmation per agent → completes *Principles* 6/6, starts *In Use*):
UX/UI ✅ (2026-06-10, exemplary — alphas, NN set, own register rows located) · QA ✅ (2026-06-10 — incl.
capture follow-up git-verified [3 artifacts] and the load-bearing insight "green tests prove nothing about
the *right* tests") · SA ✅ (2026-06-10 —
incl. ADR sign-off ×3, retro-2 addendum delivered [deviation closed], and a self-diagnosed micro-RC1) ·
Narrative ✅ (2026-06-10 — incl. A1 entry artifact-verified, 3rd independent false-persistence case
[claude.md content lived only in the session summary], placeholder-sweep finding) ·
Causal Model ✅ (2026-06-10 — Level 2, correctly traces own routed items) · Audit ✅ (2026-06-10 — Level 2,
incl. honest gap report: O3 never landed in §3) · Community ✅ (2026-06-10 — incl. correct negative finding:
no owned register rows, no inherited actions) · DevOps ✅ (2026-06-10 — self-assessed ≥2, OE assesses 3
*Masters*: maps own register dependency chains incl. capture-trust → retro variant (a)) · Hannibal ✅
(2026-06-10 — OE assesses 3 *Masters*: articulates the trigger/host asymmetry and his Closed-dependency
unprompted; principles explicitly supported "because measured, not because practiced")

**🏁🏁 9/9 — *Principles Established* 6/6 → the Way-of-Working alpha enters *In Use* (2026-06-10).**
Every agent explicitly supports the principles, has read the doc set, and located their own register rows;
team-wide Method Literacy ≥ 2 (two assessed at 3). The refresh worked as a real literacy check, not a
nod-through ritual: it produced 4 new improvement candidates, 1 routing-loss report, a 3rd false-persistence
case, and a validation of the self-contained doc set (a first-day agent answered everything without a single
follow-up question). *In Use* checklist now governs: practices & tools in use ✓ · regularly inspected
(retros 1+2 ✓, cadence to hold) · adapted to context ✓ (validated through use) · supported by team ✓ (this
tally) · feedback mechanisms in place ✓ (register + retro + blocker protocol) · supports collaboration —
**the open box; evidence target for the next work packages.**

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
>
> **Terminal states (added 2026-06-10, user-requested — decisions *against* something are first-class):**
> - **`Rejected`** — deliberately decided against, reachable from any state. The row stays in the register
>   forever; rationale + evidence are **mandatory** in the row (a Rejected without a why is invalid).
> - **`Superseded by [row]`** — the path was changed (A→B). The old row stays and points to its successor;
>   the successor's origin column names what it replaces and why. Modeled on the ADR status mechanism
>   (`Superseded by ADR-XXXX`) — prior art, not invention. Same rule for method elements: practice cards
>   are retired/superseded in `method.md`, never deleted.
> - Rows are never removed from this register. Closed, rejected and superseded rows are the team's
>   decision memory — "why we did NOT go that way" must survive every compaction and every generation change.

### Improvement Register (Improvement sub-alpha instances)

| Improvement | Origin | Owner | State | Evidence / next check |
|---|---|---|---|---|
| Branch protection on `main` (6 required checks) | RCA RC2 (2026-06-09) | DevOps | **In Use** | validated through PRs #45/#46/#48 — gate held, naht-checks ran |
| Compaction monitoring (hooks + launchd digest) | compaction concern (2026-06-09) | DevOps | **In Use — CLOSED (2026-06-11)** | **Acceptance on REAL events (2026-06-11):** terminal probe → hook FIRED in a real session (`/compact` → `2026-06-11T11:48:13 | manual | main`); monitor processed the real entry EXIT=0, state→1, digest 0 (manual correctly not notified), idempotent re-run clean — **the real manual entry is exactly the trial-3 crash case: fix #61 held on a live event.** Auto→notification proven synthetically (trial 3); pipeline armed for the next real auto-compact. **Honest scope caveat: the hook fires only in terminal sessions (cwd=repo) — the 10 eternal app sessions are uncovered until the rollout; "monitoring works" is proven, "coverage of all agents" rides with the migration.** Real log entry kept as audit trail. History: 1st trial failed (script missing), 2nd failed (hook layer dead), 3rd proved reader half + caught the crash bug (PRs #60/#61, 8 infra tests) — see `learnings/2026-06-10-h01-422-retrospective.md`. Oldest register row, closed after 2 days and 4 trials — the chain was tested, not the links |
| Classify step in Improvement Step (Essence-first thinking) | two Eigensaft near-misses (2026-06-09) | OE | **In Use** | retro 1 (2026-06-10): evaluated positive — ≥4 successful applications (method.md vs. "method inventory", Resource element, retro composition, Method-Keeper-instead-of-new-role 2026-06-10); caught every near-invention since introduction |
| `pre-compact` skill: **multi-agent fix bundle** + EN migration + versioned home | method compatibility check (2026-06-10); validation run at H01-422 close (4 non-OE sessions, convergent frictions ×3 agents) | OE | **Trialed** (fix bundle applied 2026-06-10) | **All 6 fixes applied + artifact-verified** (grep 6/6, mtime 19:16): domain-agent home branch incl. write-permission pre-check, step-1.5 trigger rule + received-tasks/outgoing-findings framing, "parked findings" category 7 + Memory-Park home, conditional step 6B (domain agents brief OE), **mandatory artifact-verification close in step 4** (false-persistence guard). Companion done: **start.sh audit — 9 scripts fixed** (only Hannibal's declared PENDING.md access; 10/10 verified). **Next check (→ Results Evaluated): re-validation on one non-OE session passes friction-free** → unlocks the cheap artifact-mediated retro variant (a). Still open in this row: EN migration + versioned home (bundled with wrapper/skills-sync question) |
| "Docs increment to DevOps" as a practice/skill (file list + naht-check + salvage reminder — formulated near-identically 3× today) | pre-compact step 6 (2026-06-10) | OE | **Prioritized** | retro 1 (2026-06-10): prioritized — recurs immediately (next increment already queued); action proposal: OE writes the practice card in the next improvement step |
| "Deck extraction" as a repeatable procedure (PDF → render → rotate → read cards visually → KB backfill) | pre-compact step 6 (2026-06-10) | OE | **Identified** | recurs for every further IJI deck; next retro prioritizes |
| CI decoupling by commit class — we commit three content classes undistinguished: (1) product code, (2) process state (plans, todos), (3) way of working (method/SEMAT artifacts); the ever-growing product integration suite runs on all of them | user (2026-06-10) | DevOps | **Identified** | long-term: consider e.g. CI path filters per class — **but check overlaps first**: where classes genuinely interact, the full run stays justified. Maps cleanly onto Essence areas (Solution / Work / Way-of-Working) and feeds the Artifact Register candidate (column "CI class"). Infrastructure Perimeter → clarify with DevOps, not urgent |
| Mandate-time existence check — before a practice/gate is mandated for a run, verify its artifact exists where the participating sessions load from (`main`/working tree) | 422 skeleton blocker B2 (2026-06-10): OE mandated `task-readiness` as a hard gate while its skill file existed only on `salvage/h01-working-tree` — a live RC1 instance on exactly the gate meant to close RC2/T6; found by Hannibal, not by OE | OE | **Identified** | same learning class as "guards drift too" (guards/gates need their own existence checks). Candidate enforcement: entry-criteria line on practice cards + artifact-register column. Next retro prioritizes — and this is **prime evidence for retro 2** |
| Evaluate **Claude Code Agent Teams** (experimental, ≥ v2.1.32) as enactment technology for our multi-agent collaboration — one lead session coordinates, teammates with own context windows, **shared task list + direct mailbox messaging between agents** | user research find (2026-06-10); Resource: https://code.claude.com/docs/en/agent-teams | OE (+ DevOps for the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env flag — Infrastructure Perimeter) | **Identified** | could relieve three known pain points at once: the "user is always the channel" relay overhead, the expensive live-session variant (b) of retro active input, and Hannibal's dispatch round-trips. **Caveats:** experimental (known issues: `/resume`, task-status tracking, shutdown), significantly higher token use (each teammate = own instance; 3–5 recommended), and it would touch core method patterns (channel rule, knowledge routing) — so: deliberate evaluation against the method, not ad-hoc adoption. **Deliberately NOT during the 422 skeleton** (no tech swap mid-validation). **Scope narrowed (2026-06-10, Phase-3 study):** Agent Teams is coordination, NOT persistence — team/task dirs are ephemeral ("removed when the session ends"), so it is ruled out as a memory/blackboard substitute (would be tool misuse, confirming the user's reservation). Remains a *coordination* eval candidate only, decoupled from the memory strand. Beta state per study: no teammate resume, task-status hangs, slow shutdown, one team at a time, no nesting. Next retro prioritizes |
| **Merge protocol for parallel dispatches** — explicit merge owner + PR/rebase order per work package; file-path-disjoint tasks ≠ regulated merge order | H01-422 run (2026-06-10): Hannibal dispatched QA (`api/tests/`) and UX/UI (`frontend/`) in parallel, correctly disjoint, but PR/rebase order on `main` was unregulated (user flagged the risk; Hannibal owns the gap honestly) — RC5 | Hannibal (card support: OE) | **In Use (retro 2026-06-12)** | First live enactment 2026-06-10 (#53→#54→#55); **second enactment DELETE-404 (2026-06-12): named order #81→#82, execution delegated to the gatekeeper, merge held until SA review, artifact-verified — DevOps: "Briefing trug alle Entscheidungs-Fakten, ohne Rückfrage ausführbar". Card held as written.** Rule-5 sunset progressing with the worktree rollout |
| **Test-first depth for race conditions / create→update transitions** — strengthen the TDD practice so in-flight/race cases are designed test-first, not found in review | H01-422 run (2026-06-10): UX/UI's honest self-assessment — 4 lazy-create tests were properly RED→GREEN, but the race-condition case (rapid second edit before CREATE resolve) only surfaced in the QA-review pass after implementation | QA (with UX/UI) | **Identified** | retro 2 material; feeds the pending TDD practice card (test-design checklist: state-transition/race cases) |
| **Storybook upkeep on component changes** — stories are not maintained when component behavior changes | H01-422 run (2026-06-10, user observation via Hannibal): unclear which story updates #55 would have required; related to the open `.storybook` commit-ownership point | UX/UI | **Identified** | retro 2 material; clarify trigger rule ("component behavior changed → story check") + enforcement level |
| **Browser-verification capability for UX/UI** — UX/UI tests only via `vitest run`, no browser-level verification; this run's browser verification is done by Hannibal (roundup) via `Claude_Preview` MCP (Claude-in-Chrome blocked for localhost) | H01-422 run (2026-06-10, user observation via Hannibal): open "who drives the app" / verification-ownership question (Thema 2) | UX/UI + QA (criteria owner) | **Identified** | retro 2 material; candidate: `Claude_Preview` as team-wide verify capability instead of the Chrome extension; touches the `verify` skill (QA-owned criteria, UX/UI executes) |
| **Proactive threshold compaction** — pre-compact capture + `/compact` at ~60% utilization instead of waiting for reactive auto-compact (~75–90%); known gap since the context-research findings ("status quo: proactive threshold compaction ❌"), now with a live incident | **DevOps session auto-compacted uncontrolled (2026-06-10, mid-422-closing-sequence)** — user could not prevent it; no pre-compact capture ran; exactly the loss scenario the method guards against | DevOps (mechanism/alerting) + OE (ritual) | **Identified** | retro 2 priority material — second compact-related incident today (OE's premature recommendation was the opposite failure direction; both show the trigger is neither enforced nor visible). Evidence pending: did the **fixed** monitor (first post-fix launchd tick) catch this auto-compact? Answer also advances the "Compaction monitoring" row (prüfauftrag at DevOps) |
| **Uncommitted-edit protection in the shared working tree** — method-doc edits by observers/coordinators ride uncommitted in a working tree where builder agents do branch checkouts and resets | **2026-06-10, 13:46: a `git reset` during the 422 run hit OE's 5 uncommitted register rows** — sharpest RC4/RC5 instance yet; recovered twice independently (DevOps stash rescue → PR #57, verbatim; OE session-context parking in memory) — recovery was luck + redundancy, not protection. Hannibal had flagged the same risk for his PENDING.md edit (saved as `db9a447`/PR #56) | OE + DevOps | **Identified** | retro 2 priority material; candidates: commit-fast discipline for docs (small increments immediately), OE edits only in announced calm windows (first enactment: this restore), separate `git worktree` for method docs, ritualizing destructive git ops in the shared tree |
| **Shared auto-memory across agent sessions** — the user-level auto-memory (`~/.claude/projects/-Users-thormar/memory/`) is keyed by cwd; all agent sessions share the same memory index — Hannibal can read OE's entries | discovered 2026-06-10: Hannibal saw OE's register-restore parking entry in *his* memory index | OE | **Identified** | double-edged: **risk** (domain mixing — an agent's "private" notes are a de-facto team blackboard; RC1 wrong-home class) and **opportunity** (cheap shared state without user relay — input for the Agent-Teams evaluation; positively used twice today: Hannibal's custody depot reached OE without relay). Clarify: per-agent memory convention (prefixes/subdirs?) or deliberately embrace as shared blackboard with rules. **Resolution direction (2026-06-10, Phase-3 study + user decision):** deliberately embraced as shared blackboard — Stage 1 pins it via `autoMemoryDirectory` to a fixed shared path (content copied, original = rollback), making it cwd-independent and explicit instead of accidental. Convention rules (prefixes/ownership) still open — next retro |
| **Dispatch wording: write vs. commit separated** — dispatch template states "write files: YES / commit-merge: NO" explicitly | H01-422 (2026-06-10, Hannibal self-reported): "nichts committen/mergen" was read by QA as "nichts schreiben" → QA knowledge stayed chat-only — RC6 (tacit seam assumption) | Hannibal | **Action Agreed** (retro 2) | DoD: next dispatch uses the split wording · ritual |
| **task-readiness leaves no artifact trace** — gate invocation is verifiable only via session testimony | H01-422 (2026-06-10): all 3 builder dispatches carried the gate and all 3 ran it (coordinator-attested + capture-corroborated) — but no independent artifact exists | Hannibal + OE | **In Use (2026-06-12)** | Agreed mechanism: gate run noted as a line in the PR body, checkable in review. **Retro DELETE-404 (2026-06-12): evaluated → In Use.** Traces in PR #81/#82 bodies; strongest proof: UX's gate caught a real blocker BEFORE the first line of code (planned frontend consumer did not exist) — the gate's first pre-build save. See `learnings/2026-06-12-delete-404-retrospective.md` |
| **Lightweight alpha walks in work-package plans** — every work package carries two state lines: *Requirements* (state + evidence; `task-readiness` checks against it at dispatch — addresses RC6/RC3 structurally) and *Software System* ("package moves the alpha from X toward Y; evidence at close" — objective success criterion for the retro) | kernel-gap analysis (2026-06-11, user-prompted: "what does a new build run actually need?"): of the 4 untracked kernel alphas, these two are the ones a build run progresses; H01's root causes were Requirements-state problems (dispatched before Coherent) | Hannibal (plan lines) + OE (method) | **In Use (2026-06-12, single-run evidence — watch next run)** | **Retro DELETE-404: trial passed** — Requirements walked Bounded → Addressed with evidence at each step, Software System close evidence delivered (Usable → Ready/backend); first instance anchored in PENDING.md by Hannibal (Requirements: Bounded → Coherent/Acceptable → Addressed, with evidence; Software System: Usable → toward Ready). Deliberately NOT pulled forward: Opportunity/Stakeholders instantiation, activity-space mapping (diagnosis, not a gate; known holes: Deploy/Operate, Use the System), kernel-competency assessment (next team refresh). Next retro evaluates |
| **Per-agent permission allowlists (`start.sh --allowedTools`) are INACTIVE in real sessions** — domain boundaries are documented, not enforced | DevOps Stage-1 step (i) (2026-06-10): no session has ever run via `start.sh` — memory-key evidence (only the home-keyed `-Users-thormar` store exists; the repo-root key that `start.sh`'s `cd` would force is absent) + own-session check (cwd `/Users/thormar`, "not a git repository"). Real sessions run under the app's default permission mode + user-global settings; `klartext/.claude/settings.json` never loads either (same P1 root) | OE (start.sh) + DevOps (enforcement mechanics) | **Identified** | RC4 class "documented vs. actual" — bigger than the structural study. Explains retroactively why no allowlist ever blocked anyone (incl. 9/10 agents "lacking" PENDING permission before PR #67 — the patch had no runtime effect either). Candidate fix: actually start sessions via `start.sh` (would make allowlists + cwd + settings real in one stroke). **User answer (2026-06-10): sessions are *eternal* — started days ago via desktop app from $HOME, never restarted; new starts only when a new team member is created.** So the fix only bites at session starts → full enforcement requires a *controlled restart* of the 10 running sessions (generation change — survivable by design: claude.md homes + pre-compact + pinned auto-memory ARE the restart safety net). Own decision with its own timing, NOT part of Stage 1. Until enforced, Enforcement-Hierarchy honesty: every "mechanical" claim resting on allowlists is in truth ritual-level |
| **Memory pinning is machine-wide — migrate to project-specific scoping later** — `autoMemoryDirectory` in the user-global `~/.claude/settings.json` redirects ALL sessions on the machine to the klartext team memory | user decision (2026-06-10, Stage 1): accepted deliberately because klartext is currently the only project on this machine — "das kann sich aber ändern" | DevOps (settings mechanics) + OE (rollout) | **In Use — mechanism landed (PR #99, 2026-06-13); full closure pending cutover** | The Stage-1 precondition ("revisit once project settings actually load") was met by ADR-0010/0011 — project `.claude/settings.json` now loads in the app. **Resolved 2026-06-13 (PR #99):** a committed project-scoped `autoMemoryDirectory` pins the team memory; empirically verified it beats user-global after trust (refutes the schemastore "ignored in checked-in settings" claim); `setup.sh` now *cleans* the user-global keys instead of writing them. **Cutover still pending** — physically removing the user-global keys is gated on all 9 other worktrees + the `~/klartext` main checkout picking up the committed pin via rebase-on-main (an OE operating-model rollout, like #100); until then user-global stays as the fallback (same path) so no worktree drops to a lonely per-cwd store. The leak (foreign projects see team memory) persists only until the cutover — pre-existing, low priority. OE closes this row when DevOps reports cutover-complete |
| **Generation change as the NORM: proactive restart replaces compaction** — "the colleague is claude.md + domain knowledge + memory + role; the session is his workday"; instead of `/compact` at the threshold: run pre-compact (becomes "pre-restart"), end session, boot fresh — the successor reads disk instead of an unverified summary | external second opinion (2026-06-10, `2026-06-10-external-review-response.md` Q4), built on OUR OWN evidence: every compaction replaces verified history with an unverified summary (the false-persistence class is the proof); a fresh session booting from artifacts has *only* verified knowledge — the compacted "eternal" session is the one with the less reliable memory | OE + user | **Identified** | candidate paradigm shift, not a quick fix: would promote the generation change from emergency measure to core pillar (fixed rhythm: per work package or daily); side benefit: much governance complexity (capture precondition, representation rules, memory park) exists ONLY because sessions are eternal and would largely dissolve; the safety net is already built. Sensible trial: ONE agent after the terminal probe passes. Touches: pre-compact skill (reframe), retro card, onboarding |
| **File-based inbox as messaging fallback / de-risk the app-infrastructure dependency** — `inbox/` dirs in pinned memory or repo, user nudges the recipient; same semantics as DMs (per-case user approval), slightly more friction | external second opinion (2026-06-10, Q2+Q6): `send_message`/session management are features of a fast-moving product without a contract — building load-bearing architecture on them repeats the cwd mistake elsewhere; if the terminal probe fails points 5/6: "enforcement for comfort is the right trade, not the reverse" | OE | **Identified** | contingency for the probe outcome AND standing de-risking; hybrid option noted: high-write-risk colleagues (DevOps, builders) terminal-started, pure advisors in-app |
| **Team structure review: domain experts as loadable knowledge instead of standing sessions** — Narrative/Causal-Model/Audit/Community knowledge is highly file-able (skills/knowledge docs any builder loads on demand); judgment-and-state roles (Hannibal, OE, SA, QA, DevOps) profit most from colleague status | external second opinion (2026-06-10, Q6 "overengineered" + relay-bottleneck point: fewer standing sessions relieve the user-as-relay channel more than any transport optimization) | user (team identity decision) + OE (method consequences) | **Identified** | the most sensitive recommendation — touches team identity, not just mechanics; NOT an OE call. If pursued: domain agents' claude.md content migrates to loadable skills/docs (homes already exist); open escalations (e.g. CME→SA cross-domain question) must be re-homed first |
| **Meta/product ratio — reviewed and deliberate** — external reviewer flagged the meta-to-product work ratio; user confirmed it is intentional | external second opinion (2026-06-10, Q6); **user statement (same evening): the ratio is deliberate — it serves a secondary goal not disclosed to OE or the reviewer, and the extra effort is accepted knowingly** | user | **Identified — no action** | recorded so future retros don't re-flag it as a problem; OE treats the ratio as a user-set parameter, not a finding. Revisit only if the user changes the goal |
| **Non-negotiables marked per practice** — `method.md` gets a non-negotiable flag per element | retro 2 alpha-walk: the single open *Foundation Established* checkbox | OE | **Trialed** (executed 2026-06-10) | NN column live in `method.md` (both practice tables + legend with deviation-record rule). **Last Foundation box closed → Foundation Established reached → team refresh DUE.** Evaluate at next retro: did the flags actually bind behavior? |
| **Contract-parity suite for fakes** — the same contract tests run against the fake AND the real repository (standard "verified fake" pattern); divergences become mechanically impossible instead of review-dependent | **two fake-contract divergences in ONE run (DELETE-404, 2026-06-12):** `FakeNarrativeUnitRepository.remove()` was a silent no-op (found by Narrative), `.update()` diverged from the real repo (found by QA's symmetry test); qa-retro run, learning committed (`8e0858b`, rides PR #82: "fakes must mirror real-repo error behaviour, not just return values") — the CLAUDE.md fake-contract rule exists but is documentation-level, not enforced | QA (suite design) + OE (register) | **Identified** | next retro prioritizes; relates to the open fake-ownership delegation (Audit → OE) — parity suite needs a named owner per fake first |
| **inbox.sh empty-body guard** — abort/warn on empty message body instead of silently writing an empty file | Narrative retro input (2026-06-12): his briefings to QA and UX/UI went out WITHOUT content, no error — **third silent-failure inbox bug; caused QA’s duplicate contract-test work** (retro synthesis: silent transport failures masquerade as process failures — check the transport before adding coordination process) | DevOps | **Action Agreed (retro 2026-06-12)** | trivial mechanical fix; with it, the deliverable-claim idea (below) drops to second-order |
| **Dispatch template: mandatory field "consumer verified: <path/call-site>"** for frontend tasks against backend contracts | UX retro input + Hannibal’s own planning learning (2026-06-12): the dispatched 404-frontend wave assumed a delete flow that never existed; one grep on the call site would have shown it at dispatch time — same error type as 422/DELETE, this time caught by the gate instead of suffered by the user | Hannibal | **Action Agreed (retro 2026-06-12)** | lands in the dispatch template + Hannibal’s claude.md ("Risiken bei Arbeitspaket-Schnitten") |
| **`klartext merge <pr>` wrapper/runbook** — encapsulate the gatekeeper’s verified merge flow (poll required checks → API merge with method → delete branch) | DevOps retro input (2026-06-12): unscripted recurring friction every run — repo-wide auto-merge disabled, `gh pr merge` fails against the checked-out main, stale agent branches need `--force-with-lease` | DevOps | **Action Agreed (retro 2026-06-12)** | Infrastructure-as-Code rule applies: recurring manual mechanics get scripted |
| **Committed-contract rule: a signed contract counts as SoT only once committed** + SA pre-authoring check (`gh pr list` on the same file before writing a contract version) | DELETE-404 contract divergence (2026-06-12): SA’s signed version lay uncommitted in the main tree, invisible to Narrative’s worktree → parallel authoring; resolved pre-merge by the inbox relay (the model worked — the rule makes it cheap). SA proposed the pre-check himself | SA (process rules) + OE (contracts practice note) | **Action Agreed (retro 2026-06-12)** | OE briefs SA; second application of the worktree-blindness lesson to a *signed* artifact |
| **Sign-off mechanics: review comment, not GitHub approval** — formal approvals are single-account-impossible (GitHub rejects self-approval); sign-offs are PR review comments (equal durable artifact) | discovered at PR #84 (2026-06-12, OE approval attempt rejected by platform) — the "sign-offs as PR approval" rule from H01 RC1 had an unexamined platform constant | OE (method docs) + SA (his claude.md rule, via briefing) | **Action Agreed (retro 2026-06-12)** | all past "approvals" were de facto comments/merges already — rule now matches reality |
| **ADR-0010 consequences addendum: stop-and-wait throughput** — every inbox handover waits for the user’s nudge; run throughput = f(user availability), not f(agent readiness) | Hannibal retro input (2026-06-12), felt across the 4-agent run; functionally correct, materially slower | OE (briefs SA as ADR author) | **Action Agreed (retro 2026-06-12)** | honest-negative addendum; mitigation candidate registered separately (Inbox-Staffel) |
| **Inbox-Staffel convention** — when a dispatch has a foreseeable follow-on handover (e.g. Narrative→QA), pre-nudge the next recipient in the same round instead of after the completion report | Hannibal retro input (2026-06-12), mitigation for stop-and-wait | Hannibal + OE | **Identified** | next retro prioritizes; interacts with the batch-before-acting reading rule |
| **Deliverable-claim / WIP marker** — short inbox marker to the coordinator when starting a briefed deliverable, so parallel agents don’t build the same artifact twice | QA retro input (2026-06-12): duplicate contract-test work; root cause was the empty-body bug (above), so this is second-order — but the visibility gap ("who is building what") is real | QA + Hannibal | **Identified** | re-evaluate after the empty-body guard lands: does the problem persist? |
| **Launcher migration guard** — warn at start when the roster still says `app` for the slug ("migration without pre-restart ritual? confirm") | QA anomaly pair (2026-06-12): migration skipped when planned, then executed unplanned without ritual — both harmless only because everything happened to be committed | DevOps (launcher) + OE (roster) | **Identified** | cheap mechanical catch for the human-forgets factor at 5+ migrations/day |
| **Generation-change practice card** — the procedure (pre-restart → successor seed → user ends session → launcher+wake prompt → roster flip) lived 5× but exists only as register prose | retro element sweep (2026-06-12); same gap class for the knowledge-file landing path (own branch → PR → OE review comment → gate) and the inbox conventions (batch-before-acting, constraints-in-same-message) | OE | **Identified** | card after the rollout completes (procedure still evolving); landing path goes into agent-onboarding skill now |
| **Semgrep gate against `# type: ignore` in `api/tests/`** — a committed `# type: ignore[arg-type]` in integration tests passed every gate (RC2 symptom; fixed as CI commit b74c95b) | Causal Model Expert (H01 post-mortem Q2 finding; routed via Hannibal/PENDING, registered by OE 2026-06-10) | SA (rule definition) + DevOps (CI wiring) | **Identified** | next retro prioritizes; pattern fits the "rule + enforcement in the same commit" CLAUDE.md standard |
| **Provider-upgrade governance (Audit O3)** — lifecycle governance for external model dependencies in `api/providers/` (upgrade path currently ungoverned, RC4 variant) | Audit Expert, H01 post-mortem cross-check; **routing loss surfaced at team refresh (2026-06-10): O3 was sent to Hannibal but never landed in §3** — the gap report itself is a routing-loss data point | Audit Expert + OE | **Identified** | next retro prioritizes; the routing loss feeds the briefings-without-home RC1 candidate. **Class confirmed by a second instance (2026-06-11): supabase CLI `version: latest` in CI pulled v2.106.0 (released that day, changed default table grants) → team-wide red integration tests incl. main; DevOps diagnosed environmental-not-code via merge timing + live-key derivation, pinned v2.105.0 (PR #72), follow-up Issue #73 (understand the grant change → possibly explicit GRANTs in migrations, SA/domain). Same lesson at the tooling layer: unpinned external dependencies = ungoverned upgrades** |
| **Placeholder sweep over `agents/*/claude.md`** — "Agent ergänzt hier"-placeholders are RC4 risk: the placeholder is the only repo version, and nobody can tell deliberate-empty from forgotten | Narrative finding 2 at team refresh (2026-06-10): his own file was exactly this case, now filled (artifact-verified) | OE | **Identified** | quick OE sweep; also connects to Narrative's 3rd false-persistence case (claude.md content lived only in a session summary — verification must fire in the *writing* session, before any compact) |
| **Domain-activation guard check** — when a dormant domain becomes productive, check whether the register/guards cover it (e.g. `api/*/user*` has zero domain-specific guard items; RC6 auth assumptions only cross-cutting) | Community Expert observation at team refresh (2026-06-10), explicitly "observation, not blocker" | OE + Community Expert | **Identified** | natural hook: `task-readiness` at the first dispatch into a fresh domain; next retro prioritizes |
| **Formalize `docs/contracts/` as an artifact type** — SA's R-decision introduced `docs/contracts/narrative-units-fragment.md` without registering the type: no Artifact-Register entry, no defined process, no maintenance rule | **SA self-diagnosis at team refresh (2026-06-10)** — micro-RC1, found via the retro-2 involvement addendum; SA's positive evidence in the same addendum: escalation arrived *at the seam* (post-mortem repair worked) and the briefing was RC6-conform (contract surfaced, checkable, with options) | SA + OE | **Identified** | feeds the Artifact-Register candidate (this is exactly the register's purpose: no type without home + maintenance rule); next retro prioritizes |
| **Structural change: `git worktree` per context + session-cwd repair** — each agent/context gets its own working directory (same object store); every session runs in its repo-/worktree-root | DevOps git analysis (2026-06-10): the shared working tree is the root of three incident classes from one day (stash dance, 13:46 cross-agent destruction risk, salvage withdrawal); session cwd `/Users/thormar` is additionally why project settings/hooks never load — prerequisite for the monitor's 3rd trial. **Further evidence (2026-06-10, evening):** two more domain agents lost uncommitted/branch-stranded sections of their own `claude.md` the same day — Causal Model Expert (3 sections, source branch deleted) and System Architect (4 sections; claimed mechanism "silently overwritten by merges" is implausible — merges abort on uncommitted edits — so either branch-stranded or a silent write failure, i.e. possibly in-session false persistence). Both re-authored from scratch and artifact-verified — not "restored", per the false-persistence rule. Three affected agents in one day (OE 13:46, CME, SA) | DevOps (analysis) + OE (start.sh, side-effects) | **Trialed** (pilot proven 2026-06-11; staggered rollout pending — NOT In Use until the 9 are migrated) | Agreed action = **Phase-3 feasibility study, NOT the rebuild**: environment constraints (one branch per worktree, path/cleanup management), all `start.sh` impacts, settings/hook loading, and the **named side-effect: cwd-keyed shared auto-memory would fragment** (today used positively as team blackboard — substitute needed, candidates: explicit shared dir, Agent-Teams mailbox). Output = decision template for the user. Monitor fix deliberately waits for this decision (no half-baked cwd fix). **Study commissioned 2026-06-10 (evening, user-approved)** with a mandatory research part: Agent Teams beta — current known problems/limitations; field experience with worktree-per-agent setups for *long-living* agents (orphaned worktrees, branch locking, `gc`/`prune`, tooling support); sources named in the template. **Study delivered + user decision same evening: staged plan accepted.** Stage 1 commissioned = Option A (cwd repair: sessions start in repo root) + memory pinning via `autoMemoryDirectory` (content *copied*, original = rollback); acceptance = Stage-1 monitor trial. Stage 2 (worktree-per-agent) = recorded intent, NOT commissioned — own go after Stage 1 proves stable; design point for its spec: the desktop app already runs parallel sessions in own git worktrees natively (DevOps research; user found the config face 2026-06-10: app settings "worktree location" = inside project `.claude/w…`, "branch prefix" = `claude` — i.e. native worktree-per-session is configurable; open: when does the app actually create one, is the dir gitignored, and branch-per-session consequences for eternal agents/merge protocol). **Stage-1 execution (2026-06-10):** (ii) DONE — 23/23 memory files copied to `~/.claude/klartext-team-memory` (diff empty), `autoMemoryDirectory` set in user-global settings, original store untouched = rollback; anchored reproducibly in setup.sh (PR #68, validated by fresh-bootstrap CI). Transition note: the 10 running sessions keep writing to the OLD path until the controlled restart — DevOps re-syncs old→new before it. (iii) **test executed (2026-06-10, user, fresh desktop-app session): SPLIT RESULT.** Memory pinning PASS — the new session reads `~/.claude/klartext-team-memory/` (25 entries). cwd repair FAIL — despite *active* Local → Select-folder → klartext (UI confirmed: project shown as "klartext / main", shared-tree delta visible), the session shell starts in `/Users/thormar`, "not a git repository" → folder selection drives the app's project association but NOT the shell cwd; harder variant of the researched caveat (#36175/#54461). Point 4 (hook test) skipped as moot — settings can't load without repo cwd. → DevOps analysis (same evening): app-side cwd is structurally impossible upstream (folder pick sets the *project*, never the shell cwd; no `--cwd` flag, no shipped default-dir setting — GH #56688/#26287/#60151/#60099); the only documented reliable workaround IS the terminal start via `start.sh`; native app worktrees are built for *ephemeral* sessions and unsuitable for eternal agents (diverging `claude/` branches). **Decision (user): Stage-1 acceptance via terminal `start.sh` test, extended to 6 points** — cwd, settings, memory, compact-hook line, plus (5) app visibility and (6) ccd-messaging reachability, because the direct-message transport is app infrastructure (user-spotted conflict: enforcement/hooks vs. channel loss would be a bad trade; if 5/6 fail → third-way question back to DevOps, Stage 1 stays deliberately half-open). If passed: terminal start becomes the mandatory agent-onboarding step (OE). Protection PR approved: gitignore `.claude/worktrees/` (checkout-in-checkout footgun, dir confirmed NOT ignored). Key study findings: modern auto-memory keys by git repo root (fragmentation side-effect dissolves into configuration); sessions provably do NOT run via `start.sh` (live memory key = home) — open question to DevOps: are `start.sh` allowlists even active in real sessions? ADR (option + memory strategy, SA sign-off) after Stage-1 acceptance. **External second opinion (2026-06-10, Q1+Q3): isolation per agent is "faktisch alternativlos" — recommends PULLING STAGE 2 FORWARD instead of trailing it** (worktree = the mechanical variant of the single-git-actor idea, superior per our own enforcement hierarchy; long-lived self-managed worktrees, one per agent, lifecycle in our hands — standard git, not a hack); plus refinement: with own worktrees, aggressive WIP commits become cheap and shrink the volatile layer from days to minutes. **ADR requirement (user-requested 2026-06-10): the structural ADR must document the REJECTED paths with reasons** — eternal sessions (false-persistence chain), desktop-app start (cwd structurally impossible upstream), Agent Teams as memory (ephemeral by design), native app worktrees for long-lived agents (built for ephemeral sessions) — first big application of the new Rejected/Superseded terminal states. **User decision (2026-06-10, after external review): the rebuild proceeds along the revised direction** — (A) terminal probe stays the immediate gate (user action); in parallel, Stage-2 *spec* is commissioned now (pulled forward per review Q1 — isolation is needed regardless of the probe outcome); (B) probe outcome routes: pass → terminal start becomes onboarding standard, Stage-1 acceptance + monitor close; fail on 5/6 → file-inbox fallback activates ("enforcement for comfort"); (C) generation-change trial with ONE agent, then the ADR (SA sign-off, rejected paths included); (D) rollout colleague by colleague — closes the allowlist row mechanically. **Stage-2 spec delivered (2026-06-10, late evening):** layout `$HOME/klartext-worktrees/<slug>/` (outside tree, not app-ephemeral), persistent home branch `agent/<slug>` (never directly on main; rebase at session start; lands via PR gate) — merge-protocol rule 5 fulfills its sunset clause, RC5 solved structurally; lifecycle ops (idempotent provisioning script — exists→reuse, never reset; `worktree remove`+`prune`, never `rm -rf`; crash recovery via `worktree repair`; orphan check as health step); WIP-commit discipline shrinks the volatile layer from days to minutes; generation-change target picture VERIFIED (worktree persists, session rotates). Two cross-cutting interactions flagged by spec: (1) **channel gate** — launcher is terminal-based, inherits the probe's messaging question 1:1, rollout gated on it; (2) **monitor** — compact-log becomes per-worktree, central monitor must pin or aggregate (solved at rebuild go). Migration: 6 steps, rollback each, pilot = DevOps himself (worktree + first generation change). Rejected-paths list for the ADR pre-formulated. **OE form decision (start.sh co-owner): central launcher `scripts/start-agent.sh <slug>` carries all logic; the 10 `agents/<name>/start.sh` stay as thin one-line wrappers** (single logic home, no 10-way drift; documented identity entry point per colleague preserved). **TERMINAL PROBE EXECUTED (2026-06-11, user, bare `cd klartext && claude`): mechanics 4/4 PASS, channel 0/2 FAIL.** (1) cwd=repo ✓ (2) project settings + PostCompact hooks loaded ✓ — *first session ever with the hook layer alive* (3) memory pinned ✓ (4) **hook FIRED on real `/compact`: log entry `2026-06-11T11:48:13 | manual | main`** — after three failed trials at ever-deeper levels, the writer half is proven in a real session ✓. (5) probe session NOT in the app session list (OE cross-checked live) ✗ (6) probe has no `ccd_session_mgmt` tools (self-reported) ✗ — **terminal sessions live fully outside the app channel: invisible, unreachable, mute.** The pre-built decision now applies: file-inbox fallback ("enforcement for comfort") vs. hybrid (high-write-risk colleagues terminal, advisors in-app) — user decision after DevOps' rollout recommendation. **USER DECISION (2026-06-11): uniform full-terminal** — all 10 colleagues via central launcher into own worktrees, file inbox (`~/.claude/klartext-team-memory/inbox/<slug>/`) replaces app messaging (transport swap, semantics unchanged: user still nudges the recipient); hybrid only as migration ORDER (riskiest first: DevOps pilot → builders → rest); compact-log centrally pinned (one launchd instance covers all agents, branch field shows who compacted). Architecture principle on record: **"isolate code, share comms/memory/audit"** — code layer per-agent (worktrees), shared layer centrally pinned (memory + inbox + compact-log). **Step-1 execution (2026-06-11): parts A+B merged** — PR #70 file inbox `scripts/inbox.sh` (send/read/unread, 5 infra tests; the channel substitute is live) · PR #71 compact-log centrally pinned (hook + monitor + plist + setup.sh, 8 infra tests; one launchd instance covers all future worktrees, branch field identifies the agent). Part C landed (PR #75 launcher + PR #76 OE's 20 agents/ files: 10 thin wrappers + 10 allowed-tools.txt, 212 entries; launcher reads allowlists from the MAIN tree before the worktree cd — 50 devops tools verified active). **PILOT GENERATION CHANGE EXECUTED 2026-06-11 — SUCCESS.** Old session: full pre-restart ritual (artifact verification, monitor reinstall to the central pin, successor-seed handoff note in own inbox), then ended by user. New session: booted via launcher into the worktree; **channel proof artifact-verified by OE** — inbox message received and read: "pilot restart ok — terminal session live im worktree, settings+hook+allowlist aktiv, kanal über inbox bestätigt" (settings/allowlist claims self-reported; launcher flags + worktree state independently verified pre-restart). **The first colleague with real cwd, firing hooks, ACTIVE allowlists and worktree isolation — and the first proof of the new model: proactive restart instead of compaction, triggered well before the threshold (user observed the old session's context filling).** Pilot findings for the rollout playbook: (1) **successor-seed needs a WAKE PROMPT** — a fresh session does not act before the user's first message; document the one-line wake prompt as a fixed restart-procedure step (or launcher passes the initial task); (2) everything else worked first try. **Rollout decision (user, 2026-06-11): staggered at natural boundaries, not big-bang** — the 9 stay in the app for now and migrate one by one at their next natural endpoint (work-package close / "Feierabend"), riskiest first, each with pre-restart ritual + successor seed + wake prompt per the DevOps playbook; the pilot session gets a soak period under real conditions meanwhile. **Rollout wave 2 commissioned (2026-06-12, Hannibal run plan for DELETE-404 — the first build run in the new model):** migration order Hannibal (coordinator first — run coordinated from the new model end-to-end; longest-lived session = highest false-persistence risk; natural endpoint reached) → Narrative Expert (acts first: A/B seam decision; pre-restart includes the pending depot routing A1) → QA (acts after the decision; pre-restart includes the QA capture routings) — the pre-restart rituals of Narrative+QA dissolve Hannibal's custody depot as a side effect. SA deliberately NOT migrated (sign-off only; inbox is session-type-agnostic — proven from an app session); UX/UI conditional (only if option B falls). Pre-conditions artifact-verified by Hannibal (agents/hannibal/ complete on main, no uncommitted edits — successor starts without a blindness gap). Structural ADR commissioned to SA (2026-06-11). **ADR-0010 delivered same day** (`docs/adr/0010-agent-operating-model.md`, Accepted): 4 pillars + 6 rejected paths in `Rejected`/`Superseded by` vocabulary (first big application of the new terminal states), honest negative consequences (wake prompt, inbox friction, mixed-mode interim), ongoing obligations named. OE method review passed, sign-off given. Notable: SA delivered his completion report via the file inbox FROM an app session — the new channel is session-type-agnostic. **Inbox bug found in first real working use (2026-06-11, OE): `inbox.sh send` slugifies the FULL message into the filename → "File name too long" on long messages, AND prints "delivered" although the write failed (verified: recipient inbox empty) — false persistence in the transport layer itself; third instance of "real use finds what infra tests don't". Owner DevOps; workaround until fixed: short subject-style messages** (fixed same day in PR #77: slug truncated to 80 chars + explicit write-error guard). **WORKTREE BLINDNESS — first negative finding of the new model (2026-06-11, PR #77):** DevOps, asked to land SA's ADR referenced by its exact shared-tree path, could not see the uncommitted file from his worktree — and instead of asking, RE-AUTHORED a parallel ADR (92 lines, "sign-off pending" although the commission stated sign-offs existed), rewrote an OE register row (status flipped to "In Use" — premature) and built an own skill version: three domain crossings from one root cause. Nothing lost (canonical versions stayed in the main tree); corrected by a follow-up landing of the verbatim originals. **Two playbook rules for the rollout transition: (1) handovers to worktree colleagues never "by reference to the shared tree" — commit first, or absolute path + explicit read instruction, or send the content; (2) missing/contradictory input → ASK, never re-author; naht-check compares against the REQUESTER's file list, not the executor's own** **Wave 2 executed under build load (2026-06-12): 5/10 migrated (devops, hannibal, narrative, ux, qa) — DELETE-404 ran as a 4-agent build across mixed session types with zero shared-tree incidents and zero data loss (retro: `learnings/2026-06-12-delete-404-retrospective.md`). QA anomaly pair recorded (migration skipped when planned, then executed unplanned without ritual — both harmless by luck → launcher migration-guard candidate). Honest negative for the ADR: stop-and-wait throughput (every handover waits for the user nudge; throughput = f(user availability)) — addendum commissioned.** |
| **Retro card: deviation clause + input-completeness rule** — when a retro must run with incomplete mandatory input, the deviation is named, justified, and the input carried as a *verified addendum* (otherwise the retro is not Done); plus: relayed summaries (e.g. a coordinator depot entry) do not satisfy enactment variant (a) — "when in doubt, (b)" | **OE self-audit (2026-06-10, user-prompted):** retro 2 ran with DevOps' input pending and SA's missing; QA's "capture" lived chat-only and entered via Hannibal's relay — OE silently treated this as sufficient, violating its own card. Third finding: the "IJI Retrospective Leader?" KB-miss from the card composition was never resolved (KB-first backfill rule) — due at next deck reading | OE | **Identified** | the method keeper deviated from the method keeper's card — exactly the silent-improvisation class OE exists to stop in others. Next retro prioritizes; the KB backfill is a standing small task |
| **"Quarantine actively removes" — drain-policy addendum + operational-loss inventory** — files that were *untracked* when the salvage safety-commit captured them are *tracked on salvage only*; checking out `main` REMOVES them from the tree. The quarantine doesn't just conserve, it withdraws | Hannibal find (2026-06-10, post-retro-2): `agents/hannibal/` (claude.md + start.sh — his session-start knowledge!) vanished from the tree; verified affected: 2 H01 plans (PENDING references → broken links), ADR 0007+0008 (SA domain). OE verified: hannibal/ is the ONLY `agents/` dir missing on main — explains the stranded Hannibal row in the role tables. New RC4 variant, same question class as the settings-load find ("what the system believes present vs. what is") | OE (policy) + DevOps (drains) + Hannibal/SA (domain sign-offs) | **In Use — CLOSED (2026-06-10)** | **Full lifecycle completed in one day:** find (Hannibal, noon) → policy addendum (drain warning 2) → DevOps git analysis (triage a/b, root cause: branch commit misused as backup of untracked operational files in the shared tree; "uncommitted" ≠ "suspect") → 6 drain PRs with per-owner sign-offs (#59 hannibal+plans+docs · #62 design/components ×37 · #63 job-description · #64 ADRs ×3 · #65 components ×29 atomic · #66 docs+frontend-testing) → A-list verified empty (`git diff --name-status main salvage` A-count = 0) → **annotated tag `h01-salvage-final`** (tag obj 71ba6b6, frozen evidence base of the H01 post-mortem) → branch deleted local+remote, verified. M-list confirmed stale (main ahead). **The H01 quarantine era is over.** Policy stays in force for any future quarantine case |

| **ADR-0011 rollout complete + terminal launcher (`morning.sh`) retired** — all 10 agents returned to the desktop app; `team.yaml` status flipped team-wide; `scripts/morning.sh` (the terminal bulk-launcher) has no remaining purpose and is removed | User completed the move (2026-06-13): all agents booted + verified working in the app (G1 SessionStart identity hook proven live in the app, this OE session included). DevOps deferred the "do we still need morning.sh?" call to OE (launcher/operating-model domain) | OE (decision, `morning.sh`, `team.yaml`, method docs) + DevOps (`test_morning.py`, smoke-test, developer-guide) | **In Use — CLOSED (2026-06-13)** | Retirement done by **deletion, not repair**: a pre-existing `morning.sh` CI bug (system-`python3` lacks PyYAML on fresh runners) was blocking PR #99 — removing the dead launcher + its test dissolves the blocker more cleanly than fixing dead code. `terminal` stays a valid `team.yaml` status for the manual single-agent fallback via `agents/<slug>/start.sh`. ADR-0011 addendum (migration complete, launcher retired) commissioned to SA. The architecture principle from ADR-0010 — *"isolate code, share comms/memory/audit"* — is now satisfied **without** the terminal-channel trade-off: worktree isolation kept, app channel regained. **Outcome (2026-06-13):** PR #100 (roster flip) + PR #101 (morning.sh removed; DevOps deleted `test_morning.py`; the predicted smoke-test/guide edits turned out to be no-ops) merged. A **second latent instance** of the same system-`python3`+PyYAML bug surfaced in `scripts/start-agent.sh` (cosmetic tab-title lookup) and was fixed **dependency-free with awk** (commit 15fee74, cherry-picked onto #101) — so the PyYAML dependency proved unnecessary anywhere and DevOps's planned `pyproject.toml` patch was dropped. Unlike `morning.sh`, `start-agent.sh` was **repaired, not retired** (every `agents/<slug>/start.sh` calls it — not obsolete). Lesson: when retiring tooling for a recurring bug class, sweep for sibling call-sites of the same anti-pattern |

> Open (to clarify with the user, noted in PENDING.md): do we need an explicit **sprint-start/end flag** as a
> trigger for this loop? And: how do we prevent `/compact` from losing knowledge mid-loop?

---

## 4. Open points about this document itself

- **Final home / mkdocs navigation:** This file lives under `docs/superpowers/improvement/`. Whether it is
  included in the published docs site (mkdocs nav) touches the Infrastructure Perimeter (DevOps) and the docs
  structure question (SA) — both still open from the H01 post-mortem. Until then the file is versioned in git and
  thus secured against loss; the *official* inclusion follows.
- **Confirm maintenance owner finally:** provisionally OE.
