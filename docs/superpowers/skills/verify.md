# Frontend Verifier

## Setup

### 1. Check servers

```bash
lsof -i :8000 -i :5173 -sTCP:LISTEN 2>/dev/null | awk '{print $1, $2, $9}' | grep -v COMMAND
```

- Port `5173` — Vite (frontend)
- Port `8000` — FastAPI (backend)

**If Vite is not running:**
```bash
cd /Users/thormar/klartext/frontend && npm run dev -- --host 127.0.0.1 &
```

**If API is not running:**
```bash
source /Users/thormar/klartext/api/.venv/bin/activate && klartext start &
```

Wait 3 seconds after starting, then proceed.

### 2. Seed test data (if needed)

If the change requires real data (slots, causal models, narrative with claims):
```bash
source /Users/thormar/klartext/api/.venv/bin/activate && klartext testdata
```

### 3. Open browser

Use `mcp__Claude_in_Chrome__tabs_context_mcp` with `createIfEmpty: true` to get a tab ID.

---

## Screens to verify

Navigate to each screen relevant to the change. For a full regression, visit all five:

| Screen | URL | What to check |
|---|---|---|
| NarrativeEditor | `http://127.0.0.1:5173/narrative` | Primary buttons dark/white, sidebar selection highlight, Analysieren button |
| NarrativeAnalyse | Navigate via Analysieren button | COLOR_MAP badges (green/amber/red/teal), ConfirmButtons, Wirkgefüge button |
| WirkgefuegeVorschlag | Navigate from NarrativeAnalyse | Slot/Relation cards, primary save button |
| CausalModelEditor | `http://127.0.0.1:5173/causal-model` | Section headers, EpistemicBadge (amber/green pill), disabled button states |
| ReadingView | `http://127.0.0.1:5173/reading` | Text color, scene number color, claim highlight (blue) |

---

## What to look for

### Token compliance

- Primary buttons: dark background (`--color-text-primary` = `#1A1A1A`), white text (`--color-text-inverse` = `#FFFFFF`)
- Disabled buttons: `--color-bg-subtle` background, `--color-text-tertiary` text
- Section labels / placeholder text: `--color-text-tertiary` (light gray, not `#888`)
- Error text: `--color-red-text`
- No raw hex values visible (you cannot see hex in the browser, but wrong colors are detectable by shade)

### EpistemicBadge

Visible in CausalModelEditor when a model has slots. Requires testdata or a full analysis run.
- `incomplete` → amber pill (`--color-amber-bg` / `--color-amber-text`)
- `axiomatic` → green pill (`--color-green-bg` / `--color-green-text`)
- Shape: fully rounded (pill, not rectangle)

### ColorMap badges (NarrativeAnalyse)

- Confirmed actor/claim: green left border
- Rejected: gray/struck through
- Confidence ≥80%: green badge
- Confidence 60–79%: amber badge
- Confidence <60%: red badge

---

## Console check

After navigating to each screen:
```
mcp__Claude_in_Chrome__read_console_messages — onlyErrors: true, pattern: "."
```

Any error is a finding. Log it with the URL where it appeared.

---

## Report format

```
## Verification: <what changed>

**Verdict:** PASS | FAIL | BLOCKED

### Steps
1. ✅/❌/⚠️/🔍 <screen> — <what was checked> → <what was observed>
   [screenshot if relevant]

### Findings
- ⚠️ <anything worth flagging>
- 🔍 <probes taken>
```

---

## Known limitations

- **EpistemicBadge** requires a model with slots — only visible after running the full
  Analyse → WirkgefügeVorschlag → Save flow. `tsc` passing is the fallback verification.
- **NarrativeAnalyse / WirkgefuegeVorschlag** require an Anthropic API call to reach —
  cannot be verified in every run. Verify after intentional changes to those screens.
