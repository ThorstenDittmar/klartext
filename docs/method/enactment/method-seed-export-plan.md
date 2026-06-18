# Method-Seed Export — Plan / Spec

> **Scope.** klartext's plan for producing an exportable **method seed**: an abstracted, parameterized dump
> of klartext's *way of working* (the operating-system layer) that semAIt and future projects **import and
> adapt** to stand up their own running agent-team project — own repo, own agent team, own Essence enactment.
> **Out of scope.** klartext's domain *Fachlichkeit* (Narrative / Wirkgefüge / Claims / domain agents, product
> backend/frontend, Supabase schema) — never ships. The actual *build* of the seed (this is the plan; building
> happens when the user drives it, per DevOps' deferral).
> **Anti-pattern guarded.** *Copy-fork* (shipping klartext content as normative instead of as a worked example);
> *find-replace fragility* (de-klartext-ification as a global `sed` instead of one config source); *silent Essence
> divergence* (no pinned meta-language baseline).
> **Language.** English (this plan). The seed itself ships **bilingual** governance/L2 templates (§6, decision 1).
>
> **Status:** plan — scoping complete, build deferred to user pacing · **Owner:** OE (cross-project transfer hub)
> · **Reviewers:** SA (structural peer, per the #171 rule) · DevOps (Infrastructure Perimeter) · QA (test substance)
> · **Origin:** user task 2026-06-18 (reverse of the F0–F3 isolation); memory `project-method-seed-export`.

---

## §1 Leitlinse & the cut

**Transferable = the generic _mechanism_; klartext content = a _worked example_.** This is the ADR-0013
method/product cut (L3 generic vs L2 enactment), applied *for export*. semAIt inherits the *way* we set
standards, make decisions and run the team — and **re-decides its own content**. The seed is a **parameterized
scaffold / starter-kit, not a fork** of klartext.

All three owners (DevOps, SA, QA) independently converged on this line (2026-06-18). Every artefact is sorted
into one of five categories:

| # | Category | Meaning | Example |
|---|---|---|---|
| ① | **As-is** | generic, transfers unchanged | L3 library cards |
| ② | **Template** | structure transfers, klartext content → placeholder/example | agent `claude.md`, role table, L2 cards |
| ③ | **Config (parameterize)** | transfers but needs path/name abstraction | `settings.json`, `inbox.sh`, CI gates |
| ④ | **Declared-not-shipped** | external dependency the importer provides; **never vendored** | superpowers, Claude Code, git, gh, Essence |
| ⑤ | **EXCLUDE** | klartext domain Fachlichkeit | `api/` domain code, domain agents |

---

## §2 Seed anatomy — what the bundle contains

| Part | Category | Notes |
|---|---|---|
| `seed.toml` — the **config source** | ③ | the keystone; everything else templates from it (§4) |
| **L3 Practice Library** (`docs/method/library/**`) | ① | already in the prior seed `~/klartext-method-seed/`; ships as-is |
| **Essence baseline** (pin + dependency-contract) | ④ + ① | see §3 — the meta-language our L3 stands on |
| **L2 enactment skeletons + one worked example per practice** | ② | empty stem + one `EXAMPLE — replace with yours` model (§6, decision 2) |
| **Agent-team framework** — `agents/<slug>/{start.sh, allowed-tools.txt, claude.md}` + `team.yaml` | ② | baseline roles only (§6, decision 3) |
| **Collaboration fabric** — `inbox.sh`, identity/health hooks, the 4 WoW gates, the gated landing path, freshness warning | ③ | generic mechanisms, parameterized |
| **Standards-Charter** (stack-neutral) | ② | OE-authored from SA's input (§5); spine = enforcement philosophy |
| **ADR-Mechanism template** | ② | the lifecycle/gate/supersession/sign-off — *not* klartext's ADRs |
| **QA substance** — 4 principles + 2 de-cored rituals + helper-ownership rule | ① / ② | per QA's verdict (§6); only coverage-invariant-1 ships as (parameterized) code |
| **Bootstrap procedure** — "stand up the OS from zero" | new | the key missing artefact (§8) |
| **MANIFEST + prerequisites contract** | ④ | what the importer must already have (§3, §8) |

---

## §3 Essence baseline — pinned + declared as a Dependency-Contract

**Why this exists (user catch, 2026-06-18):** the seed only works if the importer stands on the same Essence
meta-language we do. We deliberately keep a **self-contained** rendition (`docs/method/library/semat-definition.md`
— "kept self-contained on purpose, so we stay independent of the external site", RC4 medicine). So the **good
news**: the seed *carries* our Essence baseline (it ships in the L3 library); the importer **inherits our
version** and does **not** fetch the live OMG site — they cannot accidentally build on a divergent upstream.

**The gap (verified):** our rendition *names* "OMG Essence — Kernel and Language for Software Engineering
Methods" but **pins no edition/version, no rendering date, no deviation list**. There is no `resources/essence.md`.
So divergence is **not derivable** — neither against upstream OMG nor (more importantly for the bidirectional
hub) against semAIt's *future adapted* copy. This is the RC4 class "dependency without a validity/version
concept"; we already have the pattern (`dependency-contract.md` Work-Product type + `resources/superpowers.md`)
but never applied it to Essence itself.

**The fix (two parts, both fit the existing pattern):**
1. **Pin the Essence baseline** — in `semat-definition.md` (or a new `resources/essence.md`): which **OMG Essence
   edition** we summarized (verify against the OMG formal spec — do **not** assert from memory), the **rendering
   date**, and our **deviations/extensions** (the klartext additions on top of the Kernel).
2. **Declare Essence as a Resource + Dependency-Contract instance** (exactly like `superpowers.md`) so
   update-impact is derivable: "if OMG Essence moves to vX → re-check Y". This is what lets OE (the transfer
   hub) later reconcile our rendition with semAIt's diverged one.

**Precursor fix (klartext RC4-hygiene, independent of the seed):** the version-pin belongs in our
`semat-definition.md` regardless — flagged as a small separate OE PR before/independent of the seed build.

---

## §4 The `seed.toml` config source (DevOps-built, §5)

One file replaces the global find-replace of klartext literals. Keys (from DevOps' verdict):

```toml
project_name      = "klartext"                         # the slug everywhere
env_prefix        = "KLARTEXT_"                         # env-var prefix
memory_dir        = "klartext-team-memory"             # ~/.claude/<memory_dir>/ (memory + inbox)
product_domain    = "klartext.jetzt"                   # help strings
repo_slug         = "ThorstenDittmar/klartext"         # gh/CI
worktree_base     = "$HOME/klartext-worktrees"         # launcher
identity_preamble = "the klartext multi-agent system"  # load_agent_identity.py
interpreter       = "api/.venv/bin/python3"            # portable interpreter (§7, Gap 2)
# path lists (TRIGGER_PATTERNS etc.) — SA-semantics, DevOps-mechanism (§9)
```

Everything downstream (`settings.json`, `.pre-commit-config.yaml`, the workflows, the CLI defaults,
`classify_gate.py`'s `TRIGGER_PATTERNS`, `inbox.sh`'s paths, the identity preamble) reads from this single
source. Without it, import = fragile global `sed`.

---

## §5 Division of labor — OE = cross-project transfer hub

The **bidirectional** methodology transfer (export → semAIt **and** later inbound updates from semAIt) always
routes through **OE** (user decision 2026-06-18). Authorship is therefore not fragmented:

| Who | Owns |
|---|---|
| **OE** (hub) | seed composition + the method-content artefacts: structure, Standards-Charter + ADR-Mechanism template (authored from SA's cut), bootstrap procedure, fabric parameterization scope, L2 skeletons+examples, MANIFEST, the Essence baseline pin/contract |
| **DevOps** (perimeter) | the mechanism: `seed.toml`, artefact templating, portable interpreter, WoW-CLI extraction |
| **SA** | input (delivered) + **structural peer-review** (#171) on the seed PRs + the `TRIGGER_PATTERNS`/workflows semantics (§9) |
| **QA** | input (delivered) + review of the test substance |

*Candidate:* "OE = transfer hub" later as a `CLAUDE.md § Agent Roles` entry (which would then itself trigger
SA peer-review). Not done in this plan.

---

## §6 Baked-in decisions

**OE judgment calls (user-ratified 2026-06-18):**
1. **Language: bilingual** — L3 stays EN; governance/L2 templates DE+EN.
2. **L2: skeleton + one worked example** per practice, marked `EXAMPLE — replace with yours`.
3. **Baseline roles:** OE · DevOps · SA · QA · **Hannibal = "Product Owner"** · one generic **"Domain-Expert"
   template** (cloned per importer domain).
4. **Strip war-stories to clean rules** — dated klartext incidents (#108, F0→F3, the SA-peer ratification) out;
   the rule stays, the provenance goes.

**Owner verdicts:**
- **QA:** ships as *code* only **coverage-invariant 1** (source→test, parameterized: `SOURCE_DIRS`/`EXCLUDED_FILES`
  are config). Everything else = documented pattern + reference example. Seed substance = **4 generic principles**
  (fake-no-silent-default · fake-behaviour-parity · complex-query→integration-test · failing-test>review-comment)
  + 2 de-cored rituals (review/retro — keep categories Coverage/Edge-Cases/Fake-Parity/Domain-Composition) + the
  helper-ownership rule (**rides with the role model** — collapses without a multi-vertical structure).
- **SA:** Standards-Charter spine = the **enforcement philosophy** ("a standard is a rule *with* an automated
  check; unenforced = documentation" + "pattern + check in the same commit" = ADR-0006) + TDD-first +
  enforce-by-test + "a schema/contract change updates its consumers in the same commit" (generalized API-contract
  rule). The **ADR-mechanism itself** is the transferable artefact (template + numbering + Proposed→Accepted +
  OE-gate + supersession-with-provenance + sign-off-as-review-comment); operating-model ADRs are example fillings:
  **templates** 0006/0008/0012/0013(keystone)/0014; 0010+0011 as a **supersession demo** (strip app/terminal
  specifics, keep worktree-isolation + generational-sessions + shared-layer); 0002/0003 only if a Pattern/Testing
  annex exists; **out:** 0001/0004/0005/0007/0009.

---

## §7 Build sequence (DevOps' 4 phases + where OE content slots)

1. **Config source** (`seed.toml`) — DevOps. Foundation; everything templates from it. Highest priority.
2. **Portable interpreter** — DevOps. Small, rides on phase 1. `settings.json` hooks are already portable
   (`python3` + `$CLAUDE_PROJECT_DIR`); the venv coupling is only in `.pre-commit-config.yaml` + the CLI call →
   `interpreter` config value + a thin `bin/` shim.
3. **Artefact templating** — DevOps consumes phase 1 to parameterize `settings.json`, `.pre-commit-config.yaml`
   (linters → a named slot), the 3 WoW workflows + their `scripts/*.py` + infra tests, `inbox.sh`.
   **In parallel, OE authors** the content artefacts: Standards-Charter, ADR-Mechanism template, the L2
   skeletons+examples, the Essence baseline pin/contract, the agent-framework templates (baseline roles), the
   bootstrap procedure (§8), the MANIFEST.
4. **WoW-CLI extraction** — DevOps, **last, strict TDD**. `converge`/`landed`/`merge`/`skills sync` → a
   standalone stack-neutral package (git + gh only). **Mitigation against klartext regression:** klartext
   **re-exports** the WoW commands, keeping its single `klartext` entrypoint; the seed ships only the standalone
   CLI.

---

## §8 Bootstrap procedure — stand up the OS from zero (the key missing artefact)

Today `agent-onboarding` adds an agent to an **existing** system; there is **no** "create the operating system
from nothing" procedure. The seed must ship one — the project-level sibling of `agent-onboarding`. Sketch:

1. **Fill `seed.toml`** (project name, repo, memory dir, interpreter, …).
2. **Render the templates** from `seed.toml` (settings, pre-commit, workflows, scripts, inbox, CLI defaults).
3. **Create `agents/` + `team.yaml`** with the baseline roles (OE/DevOps/SA/QA/PO + one Domain-Expert template).
4. **Wire the hooks + pre-commit + the 3 WoW gates**; create the memory + inbox directories.
5. **Declare prerequisites** (§ below) and verify they are present.
6. **First `converge`** + handoff: the new team reads its L3 library, fills its L2 enactment (skeleton+example),
   defines its own domain agents via `agent-onboarding`.

**Prerequisites contract (Category ④, declared-not-shipped):** Claude Code (desktop app + hooks), git, gh CLI,
a Python 3.x runtime for the hook/gate scripts, a per-project memory directory, and **superpowers** (the external
plugin — declared via `resources/superpowers.md`, never vendored). Plus the **Essence baseline** (§3).

---

## §9 Open coordination & risks

- **SA ↔ DevOps (must align before phase 3):** the `classify_gate.py` `TRIGGER_PATTERNS` list mixes generic-WoW
  paths with product paths → which paths are generic-WoW is **SA semantics**, the templating is **DevOps
  mechanism**. Also the open question (raised at #172): take `.github/workflows/**` itself as a WoW surface? —
  SA decides. OE triggers this coordination when the build starts.
- **WoW-CLI regression risk** — mitigated by the re-export approach (§7.4); guarded by strict TDD.
- **Bilingual rendering effort** — every governance/L2 template ships DE+EN; non-trivial but decided.
- **`inbox.sh` parameterization** is OE's to scope (the collaboration fabric is OE-owned); DevOps only flags it.

---

## §10 Verification / DoD

The seed is "done / working" when a **fresh throwaway project can be stood up from it** and runs the loop —
not when the files are merely copied. Concretely: a **bootstrap smoke-test** (sibling of `setup-smoke-test.yml`)
that, from `seed.toml` + the bundle, produces a project where: the identity/health hooks fire, the 3 WoW gates
run, `inbox.sh` works, a baseline agent can be onboarded, and a first `converge` succeeds — on a stack the
importer chose, with **zero** `klartext` literal remaining (grep-checkable). Each build phase (§7) carries its
own checkable DoD; the Essence baseline (§3) ships with a derivable update-impact contract.

---

## §11 Prior art & references

- `~/klartext-method-seed/` — the one-time **L3-library** snapshot (MANIFEST + bundle) from the F0–F3 isolation;
  this plan is the broader **operating-system** seed that adds the framework, fabric, config and bootstrap on top.
- Memory: `project-method-seed-export` (decisions + owner verdicts), `project-cross-project-methodology-updates`
  (the parked thread this realizes), `project-methode-app-trennung-refactoring` (the F0 cut + the prior seed),
  `project-semait-methodology-contracts`, `project-superpowers-external-dependency` (declared-not-vendored).
- ADR-0013 (method/product cut), the `dependency-contract.md` + `document-scoping.md` L3 practices.
