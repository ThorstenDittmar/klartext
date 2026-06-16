# Frontend Standards — klartext

> **Essence type:** Practice
> **Advances Alpha:** Software System  ·  **Work Products:** React/TypeScript components, pages, hooks, inline styles (design-token-bound), i18n keys (`de.json` + `en.json`), component spec stubs (`design/components/`)
> **Activity / Activity Space:** Implement the System → build a React/TypeScript UI element that conforms to the klartext design system, i18n and architecture rules
> **External dependencies (referenced Resources):** none
> **Enforcement:** ritual (the `frontend` skill loads the standards at the start of every UI task; the pre-commit Quality Checklist is the gate)  ·  **NN:** —
> **Status:** living  ·  **Owner:** UX/UI
> **Enacted as:** the `frontend` skill (`docs/method/enactment/skills/frontend.md`)
>
> **Scope.** This is a **wholly-L2** card: it has **no generic L3 sibling**. klartext frontend
> standards hardcode this app's stack (React 18 + TypeScript + Vite, **inline styles only**), this
> app's design tokens (`design/tokens/*.json`), the API-contract rule against `api.ts`, and the
> `tsc --noEmit`-before-commit gate — there is no reusable, app-independent definition to extract.
> **Out of scope.** The generic TDD discipline and the frontend test *completeness criteria* — those are
> the [[tdd]] and [[frontend-testing]] practices. The technical *how* of writing tests
> (`renderWithProviders`, query hierarchy) lives in the skill source.
> **Language.** English — documentation-language rule (the standards doc); product-facing strings are
> externalized via i18n in the document's own language.
> **UX/UI-OWNED — AWAITS RATIFICATION.** Drafted by an OE-spawned sub-agent (F0.2-P-D), **not yet
> ratified by real UX/UI** (Guardrail 2 — ratify on wake).

## Purpose

Make every klartext UI element conform to one design system, one i18n discipline and one architectural
boundary — so that what the user sees and touches is consistent, localizable and free of silent data-loss
or accessibility regressions. Guards the failure modes the klartext frontend has actually hit: raw hex /
off-token values, hardcoded strings, state-only updates that never reach the API, and `api.ts` entries
with no backing endpoint.

## klartext bindings

### Stack and styling

React 18 + TypeScript + Vite. **Inline styles only** — no CSS modules, no Tailwind (ADR-0004). Colors via
`var(--color-*)` custom properties; spacing/radii/typography via the `$value` from
`design/tokens/*.json`. **Never** a raw hex, an arbitrary pixel value, or a font size outside the token
files. A missing token → GitHub Issue (`design-decision`), closest token as placeholder, `TODO(token)`
marker — never a silent invention.

### Mandatory first action

Before writing any code, read the design sources **in order**: `design/tokens/{colors,typography,spacing,radii}.json`,
then `design/do-dont.md`, `design/i18n.md`, `design/accessibility.md`, then the relevant
`design/components/` spec (or create a stub from `_template.md`).

### API-contract rule

When a Pydantic response schema (`api/schemas/`) changes, the matching TypeScript interface in
`frontend/src/lib/api.ts` is updated **in the same commit**. Run `tsc --noEmit` in `frontend/` locally
before committing to catch type drift early. **Never** add an `api.ts` entry without a backing backend
endpoint — if the endpoint is missing, stop at that boundary, file a `backend-request` Issue, mock the
value, mark `TODO(backend)`.

### Mandatory patterns

- **Async:** every user-triggered async op uses `setLoading(true)` + a `finally { setLoading(false) }`
  and disables its trigger while in flight. A missing `finally` is a bug.
- **State consistency for persisted data:** every UI state update for persisted data is paired with an
  API call. State-only updates to persisted data are a silent data-loss bug. The only exception is
  genuinely local UI state (accordion open/closed, active tab).
- **i18n:** all user-facing strings via `t('key')` (`{namespace}.{element}`); new keys added to **both**
  `de.json` and `en.json`. No fixed `width` on elements holding localized text.
- **Error handling:** API errors are caught and shown as a meaningful German message (a 404 shows
  "Narrativ nicht gefunden", not an empty UI or an infinite spinner). No `catch (e) {}` without reaction.

### Architecture boundary

UX/UI builds only within `frontend/src/` and `design/`. No imports from `api/`. No component-specific
styles in `frontend/src/index.css` (only new CSS custom properties mirroring a new token). Every new
component has a spec file in `design/components/` (stub acceptable).

### Stop-and-ask protocol

Missing design token, missing backend endpoint/field, a spec gap needing a design decision, an uncovered
interaction pattern, or an ambiguous accessibility requirement → file a GitHub Issue with the right label,
document the assumption in code, link the issue. Never silently invent a design decision.

## Enforcement (klartext)

**Ritual** at invocation (the `frontend` skill runs at the start of every UI task) plus the **pre-commit
Quality Checklist** (design tokens, i18n, async, state consistency, accessibility, architecture, pending
TODOs) which the implementer walks item-by-item before committing. Mechanical promotion candidate: a
token/i18n/`api.ts` lint gate (none enforced today — declared honestly).

## Related

- Test completeness criteria: [[frontend-testing]] (QA-owned).
- Browser verification of the rendered result: [[verify]].
- The skill source: `docs/method/enactment/skills/frontend.md` (F3 — not modified by this package).
- Register row: *Frontend Standards* in [`../method.md`](../method.md).
