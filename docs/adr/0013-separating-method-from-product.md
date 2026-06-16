# 0013 — Separating the Collaboration Method from the Product: Layer Architecture, Path-Based Classification, and Distribution

**Status:** Accepted — ratified and owned by System Architect (2026-06-16). Planning decision; the extraction itself is executed later under a separate frozen plan (see *Execution context*).
**Decided by:** User (direction, 2026-06-15).
**Author / Sign-off:** System Architect. Drafted by an OE-spawned SA sub-agent from the converged OE↔DevOps planning thread, independently ratified-with-corrections, OE-confirmed on method grounding and skill classification; **finalised and owned by the System Architect** here.
**Extends:** ADR-0010 §2/§4, [ADR-0011](0011-return-to-desktop-app-session-start.md), [ADR-0012](0012-worktree-convergence-model.md) (+ its Controlled-Method-Rollout addendum). Builds on them; supersedes none.
**Method grounding:** `semat-definition.md` §3 (Library vs Method-in-use) + §5 (Kernel/Language = referenced Resource, never vendored); `practices/controlled-method-rollout.md`; `contracts/memory-substrate.md`.
**Spin-out:** the Agent-Provenance git-trailer mechanism is split into [ADR-0014](0014-agent-provenance-trailer.md) (see Decision (c)).
**Coordination source:** converged OE↔DevOps planning thread (2026-06-15). This ADR records the **architecture/classification** decisions; the sequencing/coordination lives in a separate frozen plan under `docs/superpowers/plans/` (OE+DevOps).

## Context

klartext's collaboration method (the Essence/SEMAT way of working — `agents/`, skills, hooks, `converge`, the file inbox, the method docs tree) is interleaved with the product/app code in one repo. They have different lifecycles, different owners, and now different consumers → separate them.

**Red thread: this is Essence's *own* architecture.** Essence distinguishes a **LIBRARY** (a stock of separately-describable, composable practice **definitions**) from a **METHOD-in-use** plus its **ENACTMENT** (the running record of a specific endeavour). The Essence **Kernel and Language** are the external OMG standard — a **referenced Resource, never owned or vendored** (`semat-definition.md` §5); we own only our self-contained summary that references it.

**Three layers:**
- **L1 Product** — klartext app code. Out of scope except as the thing we separate from.
- **L2 Method instances / Enactment** — klartext's runs: register, retros, friction, lived Alpha-states, klartext-specific cards, evidence, environment facts.
- **L3 Generic meta-framework / Practice Library** — generic practice **definitions**, the enactment machinery (skills/hooks/`converge`/inbox/the converge-part of the CLI), and our self-contained Essence summary. Kernel/Language stay an external referenced Resource.

**semAIt relationship = PROVIDER/CONSUMER of a product, NOT co-use of a method.** semAIt is a product project: a generic essence-driven multi-agent environment for many projects. klartext is a field/reference user; our contribution is experience/evidence (flows **up**). semAIt is **not** implied to work like us (one definition, many enactments). semAIt seeds **once** from a copy of our **post-cut** state, then diverges — no co-maintained shared repo. We model only: an evidence channel up (now) and a later optional product-consumption channel down (future, one consumer among many). semAIt holds **no** copied/diverged method today (DevOps-confirmed) → the seed is clean; no consolidation-before-extraction required.

## Decision

### (a) Distribution = Direction C (plugin/package), phased

Target: **L3 as an installable Claude-Code plugin/package** (precedent: superpowers). The version boundary carries the **contract surface** that protects consumers against future update streams. **Interim = no machinery**: the semAIt seed is a one-time `git clone`/copy of the post-cut state. Ratify C as the **target**; implement phased. **Phase-2 trigger** = the first real consumption of semAIt's product **or** third-party consumers. Package name proposed; SA/OE finalise at Phase-2.

### (b) Path-based layer classification — the core; the F0 acceptance criterion of the cut

The 2↔3 cut runs **through** each practice card (definition + klartext evidence currently live in one file) → **card-wise splitting, not lift-and-shift**. To make classification machine-checkable, each card is **physically split by path** into an L3 stem (generic definition) and an L2 stem (klartext enactment). One path-match then serves **three** purposes: (i) classification, (ii) CI path-scoping selector, (iii) `git filter-repo` selector for the extraction. **Mechanism = path convention, not a frontmatter field** — a path cannot lie; frontmatter could drift and leave mixed files.

**Stems (ratified):**
- **L3** = `scripts/`, the converge-part of `api/cli.py`, method-related `.github/workflows/`, hooks; **`docs/method/library/`** (generic definitions, the Essence summary/grounding, generic skills).
- **L2** = **`docs/method/enactment/`** (klartext runs/evidence/friction/`continuous-improvement`/register/learnings/environment); klartext-specific skills.
- `docs/superpowers/skills/` is classified per file (table below).
- The current `docs/superpowers/improvement/` tree migrates onto `docs/method/{library,enactment}/`.

**Naming rationale:** a top-level `docs/method/` boundary, **not** re-stemming under `docs/superpowers/` (that is the distribution-plugin name); this avoids conflating the method layer with the upstream framework and gives an unambiguous `filter-repo` root.

**Semantic criterion (OE/SA):** L3 = holds for **any** endeavour that uses the practice; L2 = specific to klartext's runs/decisions/evidence/product. OE/SA classify **once**; a CI check (DevOps) enforces it permanently, rejecting (i) any method-content file outside the L3/L2 stems and (ii) any still-"mixed" card.

**F0 acceptance criterion:** the cut is **done** only when every object is automatically classifiable (a machine-checkable path rule).

**Elegant consequence:** because classification = path is automatic, the extraction (`git filter-repo --path` on the L3 stems, history preserved) runs **mechanically** without per-object judgment → it can be carried by the lead-and-spawn rotation in execution.

### (c) Agent-Provenance trailer — recorded direction; spun out to ADR-0014

**One identity:** the SSOT is the `agents/<name>/` directory name; `team.yaml` is metadata only. Rendered across substrates: inbox `from`/`to`; team-memory last-edited-by (= contract clause **C5**); a **git commit trailer `Agent: <slug>`** (commit-msg hook + CI check; spawn-aware `Agent: <lead> (spawned <task>)`). This generalises C5 to git. **Not ratified here** — it is separable, touches the **Infrastructure Perimeter** (commit-msg hook, CI), and needs a DevOps Briefing. It ships as **[ADR-0014](0014-agent-provenance-trailer.md)** (SA-owned + DevOps Briefing). Per-agent real GitHub identities are deferred (confirmed).

## Rejected / deferred alternatives

| Alternative | Verdict | Reason |
|---|---|---|
| **Frontmatter-field classification** | Rejected | Can drift; leaves mixed-content files. A path cannot lie and doubles as the CI + `filter-repo` selector. |
| **Re-stemming under `docs/superpowers/library\|enactment/`** | Rejected | Conflates the method layer with the distribution-plugin name; top-level `docs/method/{library,enactment}/` chosen instead. |
| **Submodule/subtree distribution** | Deferred/Rejected | Couples repos, no version semantics; unnecessary given the one-time copy seed; not a stepping stone to the plugin. |
| **Co-maintained shared library** | Rejected | Contradicts the provider/consumer relationship; semAIt copies once and diverges. |
| **Seeding semAIt pre-cut** | Rejected (User) | The post-cut machine-classified state is the best field material; pre-cut hands over the entangled mess. The start-time cost is accepted — the cut **is** F0. |
| **Distribution machinery now** | Deferred | Premature distribution is a documented Essence-adoption pitfall; build it at the Phase-2 trigger. |
| **Vendoring the Essence Kernel/Language** | Rejected | External referenced Resource; we own only our summary that references it. |
| **Bundling the Agent-Provenance trailer into 0013** | Rejected | Separable, Infrastructure-Perimeter, independently landable → ADR-0014. |

## Consequences

**Positive**
- Realises the Essence Library-vs-Method-in-use distinction concretely; Kernel/Language stay a referenced Resource (no vendoring drift — an RC4 class).
- Classification is mechanical (path = classification = CI selector = extraction selector) → a history-preserving extraction without per-object judgment, carryable by lead-and-spawn.
- A permanent CI guard prevents re-entanglement.
- The L3 plugin version boundary gives a real contract surface.
- One agent identity across inbox/memory/git (via ADR-0014) closes the attribution gap on git, enforceably.
- The semAIt seed is clean.

**Negative / Risks**
- **Autonomy vs coherence (named).** L3 shared = more coherence, less local autonomy; the **contract** is the negotiated boundary (what L3 promises, what a consumer may rely on). While we are our own L3 source (State A, now), this does **not** bind us — we keep evolving `converge`/hooks/gates/CLI freely; the "don't locally edit L3 definitions" rule is a **consumption-state (State B)** rule.
- Card-wise splitting is real work; the CI "mixed card" check will initially fail for many files — **that failing state is the F0 to-do list.**
- The per-card 2↔3 split of `practices/` + `contracts/` (line-by-line generic definition vs klartext evidence) is iterative architecture work, scoped to execution **under SA review**, not pre-decided here.
- A wrong stem path is expensive to undo after `filter-repo` → stems are settled here (top-level `docs/method/`).

**History separation (decided):** full git history via `git filter-repo --path` for our source-of-record L3; a squash/snapshot is acceptable for the one-time semAIt seed (it diverges, no co-maintenance).

**Execution context (recorded, not decided here):** the refactoring is a **breaking way-of-working change** → executed under the Controlled Method Rollout practice in **BARRIER mode** (Stabilise & Halt → Update → Resync & Verify), coordinated by OE+DevOps via lead-and-spawn (fresh spawns read laid-down state; drift = 0), **not** the steady-state long-lived+inbox model (unchanged). Hard preconditions (three gates): a test-coverage audit (DevOps+QA, `qa-review`-gated); a first-pass contract audit (the contract set = the 2↔3 interface from the protection side); a tested out-of-band backup/restore of the non-versioned substrate (`~/.claude/klartext-team-memory` = memory + inbox + `.read`; `~/.claude` user-state; `.env` confidential; per-worktree WIP as git-stash bundles) to a **local external timestamped path**, restore verified via the C4 index-integrity check (an un-replayed backup is False Persistence). The [ADR-0012](0012-worktree-convergence-model.md) Point-D non-blocking guarantee is unchanged; the barrier is a bounded, declared, land-time event.

## Skill classification (OE-confirmed, with OE's refinement on knowledge-routing + task-readiness)

| Skill | Layer | Reason |
|---|---|---|
| `agent-onboarding` | L3 | Generic add-an-agent practice (OE-owned). |
| `anchor` | L3 core + L2 refs | Generic secure-before-context-loss ritual; klartext path/`converge`/team-memory bindings → L2. |
| `knowledge-routing` | L3 core + L2 bindings | Generic = channel policy #108 ("inbox is the floor"), user-is-the-channel, C5 provenance convention, route-to-owning-domain (all reusable L3); L2 = klartext domain-agent map. Not wholesale L2. |
| `task-readiness` | L3 core + L2 bindings | Generic readiness-gate-before-a-dispatched-task = L3; klartext checklist (fake-contract, Hannibal, `qa-review`, SA-escalation) = L2. More L2-coupled than knowledge-routing, but not wholesale L2. |
| `job-description` | L3 pattern + L2 content | Self-describe-role pattern generic; the descriptions are klartext-specific. |
| `frontend` | L2 | klartext frontend (ADR-0004 inline-styles, API contract). |
| `frontend-testing` | L2 | klartext frontend completeness criteria. |
| `verify` | L2 | Hardcodes the klartext app (ports, Supabase, run flow). |
| `qa-review` (+ `qa-categories`, `report-format`) | L3 skeleton + L2 rules | Dispatch-QA-subagent practice generic; the domain-composition rules (Wirkgefüge) → L2. |
| `qa-retro` | L3 | Generic missed-bug → retro + missing test + learning; the learnings it emits are L2. |

**Pattern (consistent):** most ritual skills = an L3 generic core + L2 klartext bindings — exactly the card-wise split the F0 criterion forces.

## Open questions remaining (SA-owned)

1. **Package/plugin name** for the L3 distribution (Decision (a)) — at the Phase-2 trigger; not blocking the cut.
2. **ADR-0014 authoring** (Agent-Provenance trailer) — SA draft + DevOps Briefing for the commit-msg-hook/CI half. *(Drafted alongside this ADR.)*

*Resolved in ratification:* stem naming → top-level `docs/method/{library,enactment}/`; semAIt prior-method → none (clean seed); history → full for L3, squash for the seed; provenance → ADR-0014; skill table → OE-confirmed with the knowledge-routing/task-readiness refinement.
