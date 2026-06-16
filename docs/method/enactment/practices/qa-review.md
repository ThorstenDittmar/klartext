# QA Review — klartext enactment

> **Scope.** klartext's enactment of the **qa-review** practice: the five concrete check categories, the
> Wirkgefüge domain-composition trigger, the report format, the test layers the fresh sub-agent reviews
> against, and the `tdd` Step-3 binding.
> **Out of scope.** The generic fresh-eyes principle and the run — see the L3 card. The TDD discipline
> itself (`tdd`); the incident-triggered test-gap retro (`qa-retro`).
> **Language.** English — documentation-language rule.
> **Seeded by an OE-spawned sub-agent (F0.2-P-C); awaits real-QA ratification on wake.**
>
> **L3 definition:** [`../../library/practices/qa-review.md`](../../library/practices/qa-review.md)
> **Status:** living (ritual) · **Owner:** QA · **Advances Alpha:** Software System · **NN:** ✓
> **Enacted as:** the `qa-review` skill (`docs/superpowers/skills/qa-review/` — SKILL.md + qa-categories.md + report-format.md + domain-composition-rules.md)

## klartext bindings

### The five check categories

The fresh sub-agent works every diff through these five (source: `qa-review/qa-categories.md`):

1. **Test completeness** — every new class/method in `models/`, `services/`, `repositories/`, `routers/` has
   the relevant layers: Domain (no mocks), Service (FakeRepository), Repository (`@pytest.mark.integration`),
   Router (`AsyncClient`).
2. **Edge & error cases** — `XNotFoundError`, invalid input (422 at router / DomainError at domain), empty
   collections, duplicate detection, error propagation. Red flag: routers tested only for 200.
3. **Infrastructure tests** — every router has `GET /<resource>/health` (200, `{"status": "ok"}`, no auth)
   *and* a test for it; every `Supabase*` method with JOINs / embedded counts (`table(count)`) / multi-table
   queries has an integration test (the fake cannot verify these).
4. **Fake-contract completeness** — full interface, no silent constants (`return 0/[]/None/False` as a whole
   body); test-controllable helpers for computed fields; and **error-behaviour parity** — the fake raises the
   *same* exception on the *same* condition as the real repo (asymmetry in the fake is a red flag).
5. **Domain composition** — see the trigger below.

### Wirkgefüge domain-composition trigger

Category 5 fires when the diff touches `models/causal_model*.py`, `models/slot*.py`,
`models/causal_relation*.py`, `models/causal_model_scope*.py`, **or any method on** `CausalModel`, `Slot`,
`CausalRelation`, `CausalModelScope` — including `CausalModel`-only changes (they can affect scope without
touching the other files). Checks: null-return guard (`resolve()` returns `[]`, never `None`, for an empty
model), assembled-network tests, **top-down operations only** (resolve/validate on the model, never on a
context-free component), and CausalMixin shared-component independence (source:
`qa-review/domain-composition-rules.md`).

### Report format

Fixed three-section output (`qa-review/report-format.md`): **✅ Complete** (named class/method/test) ·
**⚠️ Gaps found — RED tests written** (`[WRITTEN]` only when the code exists and runs RED) · **❌ Requires
manual decision** (with a specific reason). Never `[WRITTEN]` without code.

### tdd Step-3 binding

The `tdd` skill invokes `qa-review` as its non-optional Step 3 — all-green is necessary, not sufficient.
After a **bug fix**, if the bug should have been caught originally, the flow continues into `qa-retro`.

### Infrastructure-test review (four-eyes)

When DevOps requests review of `api/tests/infrastructure/`, QA checks: does a test exist · does it catch the
real failure mode (not just the happy path) · is `@pytest.mark.integration` set · is the assertion message
informative. QA may add assertions in that directory directly — no DevOps Briefing for test additions there.
QA does **not** assess PostgREST/migration SQL/CI-config correctness (DevOps domain).

## Enforcement (klartext)

Ritual at invocation (close-out of every implementation session; `tdd` Step 3). The structural slice is
**mechanical** via `scripts/check_test_coverage.py` (source→test, router→health, supabase→integration). The
category judgement stays QA's — qa-review found 5 real contract-gap tests in H01-422; it is judgement, not a
coverage counter.

## Related

- L3 definition: [`../../library/practices/qa-review.md`](../../library/practices/qa-review.md).
- The composition that calls it: [`tdd.md`](tdd.md) (Step 3) · the test-gap sibling: [`qa-retro.md`](qa-retro.md).
- The skill source: `docs/superpowers/skills/qa-review/` (F3 — not modified by this package).
