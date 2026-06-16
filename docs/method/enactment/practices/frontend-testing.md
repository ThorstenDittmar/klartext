# Frontend Testing — klartext completeness criteria

> **Essence type:** Practice
> **Advances Alpha:** Software System  ·  **Work Products:** frontend test files (Hook / Component / Page level) satisfying the obligatory-scenario criteria; QA-review findings against those criteria
> **Activity / Activity Space:** Test the System → define and check what makes a Hook / Component / Page sufficiently tested in the klartext frontend
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual (QA-review checklist) — partly mechanical (the structure-check `find` over `__tests__` directories)  ·  **NN:** ✓ (Pages and Hooks: no Page/Hook ships without a test)
> **Status:** living  ·  **Owner:** QA (owns the completeness criteria)
> **Enacted as:** the `frontend-testing` skill (`docs/superpowers/skills/frontend-testing.md`), applied within the `tdd` and `qa-review` flows for React/TypeScript work
>
> **Scope.** This is a **wholly-L2** card: it has **no generic L3 sibling**. The criteria hardcode the
> klartext frontend's three test layers and the specific obligatory scenarios — including the named
> shared/Manuskript component props-combinations where klartext bugs have actually hidden. There is no
> app-independent definition to extract.
> **Out of scope.** The technical *how* (stack, query hierarchy, `renderWithProviders`, `vi.mock`) — that
> is the [[frontend]] standards / skill source. The generic red-green discipline — that is [[tdd]].
> Live-browser verification — that is [[verify]] (a different layer: real browser + backend, not unit).
> E2E (Playwright) completeness — explicitly a separate, not-yet-established document.
> **Language.** English — documentation-language rule (the source skill is currently German prose; this
> card describes it in English).
> **QA-OWNED — AWAITS RATIFICATION.** Drafted by an OE-spawned sub-agent (F0.2-P-D), **not yet ratified
> by real QA** (Guardrail 2 — QA owns these criteria, ratify on wake).

## Purpose

Define **what** and **when** a frontend element must be tested (the completeness criteria QA reviews
against) — distinct from the *how* of writing the test. Guards the gap where green unit tests still miss
obligatory error paths (infinite spinner on API failure, no 404 handling) or the tricky props-combinations
where klartext bugs have repeatedly hidden (e.g. a `count=0` test that passes even when the component
wrongly renders `0`).

## klartext bindings

### Three layers (frontend equivalents of the backend four)

| Frontend | Backend equivalent | What is tested |
|---|---|---|
| **Hook** | Domain + Service | pure logic: state transitions, return values, error state |
| **Component** | Service | render variants, interactions, i18n |
| **Page** | Router | full integration: data loading, all states, user flows — **API mocked** |

E2E (Playwright = real browser + backend) is **not** one of these layers and its criteria are out of scope.

### Obligatory scenarios

- **Page** (test required — *always*, no Page ships without one): loading state visible · success state
  (data in DOM) · API error → message visible (no infinite spinner) · 404 when the page loads a resource
  by ID · happy path for the main persisted interaction. *(Optional, not a blocker: empty state, multiple
  error states, optimistic UI / races.)*
- **Component** (test required when it has its own logic — interaction, conditional rendering, formatting):
  default render with minimal required props · every visual variant · user interaction → callback called ·
  at least one translated i18n string. *(Optional: extreme-prop edge cases, keyboard/focus.)*
- **Hook** (test required — *always*): initial state · success path (`data` set, `isLoading` false,
  `error` null) · error path (`error` set, `isLoading` false, data empty) · `isLoading` true during the
  call · returned callback triggers a state update. *(Optional: debounce, refetch, cache invalidation.)*

### Obligatory error paths (no discretion)

Every page with an API call → network/500 shows a message, no infinite spinner. Every page loading a
resource by ID → 404 shows a sensible message, no crash. Every async hook → a rejected promise sets
`error`, `isLoading` false. Every component with an `error` prop → renders the error variant in the DOM.

### Component props-combinations (where bugs hide)

The skill catalogs the tricky combinations per shared and Manuskript component (Button `isLoading` must
set **both** `disabled` and `aria-busy`; `CountBadge count=0` must render `null`, not `0`; SearchInput
clear must call `onChange("")`, not internal state; SectionHeader `onAdd` click must **not** toggle
collapse; Breadcrumb must test **both** separator variants; etc.). These named combinations are part of
the criteria — and so are the skill's flagged **known gaps** (e.g. Avatar fallback, Breadcrumb
`separator="slash"`, WordCountLabel size variants), to be closed or explicitly deferred to [[verify]].

### QA-review checklist

A **structure check** (`find frontend/src/{pages,components,hooks}/__tests__ -name "*.test.tsx"` — do test
files exist?), a per-file **content check** against the obligatory scenarios above, and a **quality check**
everywhere: no `setTimeout` in tests (only `waitFor`), no real API call (all `vi.mock`),
`renderWithProviders()` where i18n/Router needed, queries follow `getByRole > getByLabelText > getByText >
getByTestId`.

### Relation to the frontend Quality Checklist

The Tests section of the [[frontend]] Quality Checklist is the **minimum** UX/UI checks at commit; these
criteria are finer-grained and serve QA at review. If QA misses a test type not in the frontend.md
checklist → QA sends a UX/UI briefing proposing the addition (criteria flow from QA → standards via the
owner, not by direct edit).

## Enforcement (klartext)

**Ritual** — the criteria are applied in the `tdd` flow (frontend work) and checked at `qa-review`. The
structure check (`find` over `__tests__`) is **mechanical**; the content/scenario coverage is a manual
QA-review judgment. Pages and Hooks are **NN** (never ship untested); a logic-bearing Component is NN, a
pure layout wrapper is QA-review judgment.

## Related

- The standards and the technical *how*: [[frontend]] (UX/UI-owned, the skill source).
- The generic test discipline this composes with: [[tdd]].
- The orthogonal live-browser layer: [[verify]].
- The skill source: `docs/superpowers/skills/frontend-testing.md` (F3 — not modified by this package).
- Register row: there is no dedicated *Frontend Testing* row; this criteria set is referenced from the
  *Frontend Standards* / *Frontend Verification* rows and the `tdd` frontend tail. *(Flagged as an
  uncertainty for QA — see PR body.)*
