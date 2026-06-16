# Test-Driven Development — klartext enactment

> **Scope.** klartext's enactment of the **tdd** wrapper practice: the concrete test bindings that
> extend the upstream discipline — the inside-out test levels, fakes-not-mocks, the Supabase
> integration-test rule, the `/health` endpoint rule, and the `qa-review` close-out step.
> **Out of scope.** The generic TDD discipline (red-green-refactor, the Iron Law) — that is
> `superpowers:test-driven-development`, **referenced, not restated** here. The composition shape — see
> the L3 wrapper card.
> **Language.** English — documentation-language rule.
>
> **L3 definition:** [`../../library/practices/tdd.md`](../../library/practices/tdd.md)
> **Upstream Resource:** [`../../library/resources/superpowers.md`](../../library/resources/superpowers.md) (`superpowers:test-driven-development`)
> **Status:** living (ritual) · **Owner:** QA (test standards) / OE (composition shape, L3) · **Advances Alpha:** Software System + Way of Working · **NN:** ✓
> **Enacted as:** the `tdd` skill (`docs/superpowers/skills/tdd/SKILL.md`) + the structural coverage check (`scripts/check_test_coverage.py`)

## klartext bindings

### Test levels — inside out

Test in this order; each level has a distinct tool and isolation boundary:

| Level | What is tested | Isolation |
|---|---|---|
| **Domain** | pure unit tests — invariants, factory methods, state changes | no mocks, no external systems |
| **Service** | business logic, orchestration | **fake repositories** (in-memory), no Supabase |
| **Repository** | SQL / PostgREST queries | `@pytest.mark.integration` against the real test DB |
| **Router** | the HTTP contract (status, body, wiring) | `AsyncClient` + `ASGITransport` |

### Fakes, not mocks

Service tests use **real in-memory fake repositories** (classes), never mock objects. A fake must honor
the full interface contract — **no silent constants** (`claim_count=0` is forbidden; use a
test-controllable `set_claim_count()` helper) and **behavioral parity** (a fake raises the same
exception on the same condition the real repo does — asymmetry in the fake is a red flag). See the QA
fake-contract rules.

### Supabase integration-test rule

Every new `SupabaseXRepository` method gets an `@pytest.mark.integration` test **in the same commit** as
the implementation — unit tests with the fake are *not sufficient* (the fake cannot verify SQL /
embedded PostgREST counts / FK relationships). Required signals: JOINs, embedded counts
(`table(count)`), multi-table queries.

### Health-endpoint rule

Every service router gets `GET /<resource>/health` (HTTP 200, `{"status": "ok"}`, no auth) **added
first**, before any other endpoint — and a router test asserting it. Enforced by test, not by review.

### qa-review close-out (TDD Step 3)

Before "done", invoke `qa-review` — the QA sub-agent reviews the diff with fresh eyes (coverage, edge
cases, infrastructure tests, fake-contract completeness, domain composition). All-green is necessary,
not sufficient. **Bug fixes:** after the fix is green, invoke `qa-retro` if the bug should have been
caught originally.

### Structural invariants (mechanical)

`scripts/check_test_coverage.py` enforces three invariants — no manual review substitutes:

1. every source file in `models/` `services/` `repositories/` `routers/` has a `test_<stem>*.py`;
2. every `test_*_router.py` has a `health`-named function;
3. every `supabase_*.py` repository has at least one `@pytest.mark.integration` test.

### Frontend

For React/TypeScript work, additionally apply the `frontend-testing` skill (QA-defined completeness
criteria extending these standards).

## Enforcement (klartext)

Ritual at invocation (the skill runs at the start of every feature/bugfix); **mechanical** for the three
structural invariants (`check_test_coverage.py`). The `qa-review` close-out is a non-optional ritual
step of the `tdd` skill.

## Related

- L3 wrapper card: [`../../library/practices/tdd.md`](../../library/practices/tdd.md).
- Upstream Resource: [`../../library/resources/superpowers.md`](../../library/resources/superpowers.md).
- Dependency contract: [`../contracts/superpowers.md`](../contracts/superpowers.md) (S2 — the wrapped TDD discipline still carries its Iron Law).
- The skill source: `docs/superpowers/skills/tdd/SKILL.md` (F3 — not modified by this package).
