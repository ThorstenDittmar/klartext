# Frontend Verification — klartext

> **Essence type:** Practice
> **Advances Alpha:** Software System  ·  **Work Products:** a verification report (verdict PASS/FAIL/BLOCKED + per-screen steps + findings + screenshots)
> **Activity / Activity Space:** Test the System → run the klartext app and observe a UI change behaving correctly in a real browser before it lands
> **External dependencies (referenced Resources):** the browser-driving MCP (`Claude_in_Chrome`, fallback `Claude_Preview`) — load-bearing: the observe step drives a real browser through it. The app's own runtime (Vite on `:5173`, FastAPI on `:8000`, Supabase, optionally the Anthropic API for analysis screens) is the *system under test*, not a referenced method Resource.
> **Enforcement:** ritual (run for UI changes before done; four-eyes — QA owns the criteria, UX/UI executes)  ·  **NN:** ✓ (for UI changes)
> **Status:** living  ·  **Owner:** UX/UI (executes) — QA owns the verification *criteria*
> **Enacted as:** the `verify` skill (`docs/superpowers/skills/verify.md`)
>
> **Scope.** This is a **wholly-L2** card: it has **no generic L3 sibling**. The flow hardcodes the
> klartext app — the concrete ports (`5173`/`8000`), the `klartext start` / `klartext testdata` commands,
> the five named screens and their URLs, and the exact token/badge expectations to eyeball. There is no
> app-independent definition to extract.
> **Out of scope.** Frontend *unit-test* completeness (that is [[frontend-testing]], a different layer —
> mocked, no real browser/backend). The build standards being verified ([[frontend]]).
> **Language.** English — documentation-language rule.
> **FOUR-EYES — QA OWNS THE CRITERIA, UX/UI EXECUTES.** This is a four-eyes-pairing instance:
> what counts as "verified" is a QA-owned criterion; the run/observe is performed by UX/UI.
> **AWAITS RATIFICATION.** Drafted by an OE-spawned sub-agent (F0.2-P-D), **not yet ratified by real
> UX/UI (execution) or QA (criteria)** (Guardrail 2 — ratify on wake).

## Purpose

Confirm that a frontend change actually behaves correctly on the **live klartext app** — rendered in a
real browser against the real backend — before it lands. `tsc` passing and green unit tests are necessary,
not sufficient: token shades, badge colors, disabled-button states and console errors are only observable
in the running app. Guards "it compiled, ship it" regressions that unit tests with mocked APIs cannot see.

## klartext bindings

### Run flow

1. **Check servers** — `lsof -i :8000 -i :5173 -sTCP:LISTEN`. Vite on `5173` (frontend), FastAPI on
   `8000` (backend). Start what is missing: `npm run dev -- --host 127.0.0.1` for Vite;
   `klartext start` (in the activated venv) for the API. Wait ~3s after starting.
2. **Seed test data** if the change needs real data (slots, causal models, narrative with claims):
   `klartext testdata`.
3. **Open the browser** via the MCP (`tabs_context_mcp` with `createIfEmpty: true`).

### Screens (the five)

| Screen | URL | What to check |
|---|---|---|
| NarrativeEditor | `http://127.0.0.1:5173/narrative` | primary buttons dark/white, sidebar selection highlight, Analysieren button |
| NarrativeAnalyse | via Analysieren | COLOR_MAP badges (green/amber/red/teal), ConfirmButtons, Wirkgefüge button |
| WirkgefuegeVorschlag | from NarrativeAnalyse | slot/relation cards, primary save button |
| CausalModelEditor | `http://127.0.0.1:5173/causal-model` | section headers, EpistemicBadge (amber/green pill), disabled button states |
| ReadingView | `http://127.0.0.1:5173/reading` | text color, scene-number color, claim highlight (blue) |

Navigate the screens relevant to the change; for a full regression, visit all five.

### What to observe

- **Token compliance** — primary buttons dark bg (`--color-text-primary`) / white text
  (`--color-text-inverse`); disabled = `--color-bg-subtle` / `--color-text-tertiary`; labels/placeholders
  `--color-text-tertiary`; error text `--color-red-text`. Wrong shades are detectable by eye.
- **EpistemicBadge** — `incomplete` → amber pill, `axiomatic` → green pill, fully rounded.
- **ColorMap badges** — confirmed = green left border; rejected = gray/struck; confidence ≥80 % green,
  60–79 % amber, <60 % red.
- **Console** — `read_console_messages` with `onlyErrors: true`; any error is a finding (log it with the
  URL where it appeared).

### Known limitations

EpistemicBadge requires a model with slots (only after a full Analyse → WirkgefügeVorschlag → Save run).
NarrativeAnalyse / WirkgefuegeVorschlag require an Anthropic API call to reach — not verifiable in every
run; verify after intentional changes there. When the live path is unreachable, `tsc` passing is the
documented fallback.

### Report

Fixed shape: a verdict (**PASS / FAIL / BLOCKED**), per-screen steps (✅/❌/⚠️/🔍 with what was checked →
what was observed, screenshot if relevant), then findings and probes.

## Enforcement (klartext)

**Ritual** — run for UI changes before "done". Four-eyes by construction: QA owns the verification
*criteria* (what "verified" means), UX/UI performs the run/observe. Not mechanizable (a human/agent
eyeballs rendered shades); the structural fallback when the live path is blocked is `tsc --noEmit`.

## Related

- The standards being verified: [[frontend]].
- The orthogonal unit-test completeness layer (mocked, no browser): [[frontend-testing]] (QA-owned).
- The skill source: `docs/superpowers/skills/verify.md` (F3 — not modified by this package).
- Register row: *Frontend Verification* in [`../method.md`](../method.md).
