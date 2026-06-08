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

## Shared Components — Storybook

Storybook läuft auf `http://localhost:6006` wenn gestartet.
Diese Checks laufen nach Änderungen an Shared Components — nicht bei jedem Commit.

### Atoms

**Button** — alle 4 Varianten prüfen:
- `primary`: dunkler Hintergrund, weißer Text, Token-konform
- `secondary` / `ghost`: kein harter Hex-Wert sichtbar
- `nav-item` + `isActive=true`: Blue-Highlight sichtbar, erkennbar unterschiedlich zu default
- `isLoading=true`: Spinner sichtbar, Button nicht klickbar, kein Text-Flackern
- `disabled=true`: visuell abgeschwächt (richtige Disabled-Tokens), kein Hover-Effekt

**Badge** — alle 3 Varianten × 6 Farb-Keys:
- Farben entsprechen den erwarteten Tokens (kein falsches Grün statt Amber etc.)
- Kein unerwarteter Hover-Cursor (es ist read-only)

**CountBadge**:
- `count=0` + Default → nicht sichtbar (kein leerer Raum)
- `count=100` + `max=99` → zeigt `"99+"`, nicht `"100"`
- `variant="dot"` → Punkt sichtbar, keine Zahl

**InlineCodeBadge**:
- `copyable=true` → Copy-Button sichtbar neben dem Code
- Nach Klick: visuelles Feedback (Icon-Wechsel oder kurze Bestätigung)
- Code-Schriftart (monospace) korrekt gesetzt

**Avatar** — Fallback-Kette visuell prüfen:
- Mit Bild → Foto gerendert
- Ohne Bild, mit Name → Initialen in Kreis, Farbe nicht random wirkend
- Gleicher Name zweimal → exakt gleiche Farbe
- Ohne Bild, ohne Name → Placeholder-Icon sichtbar
- Alle 4 Größen (`xs` bis `lg`) proportional

### Molecules

**EmptyState**:
- Ohne `actionLabel` → kein Button
- Mit `actionLabel` → Button vorhanden, Primär-Styling
- `icon` optional → mit und ohne Icon korrekt zentriert

**SearchInput**:
- `value=""` → Clear-Button nicht sichtbar (kein Leerraum)
- `value="Text"` → Clear-Button erscheint ohne Layout-Shift
- `variant="inline"` → kein Border sichtbar, kompakter als `default`

**TextInput**:
- `errorMessage` → rote Fehlermeldung sichtbar, Input hat roten Border/Outline
- `helperText` → grauer Hilfstext unter Input
- `errorMessage` + `helperText` gleichzeitig → nur Fehlermeldung sichtbar
- `readOnly` vs `disabled` → visuell unterschiedlich (readOnly weniger stark abgeschwächt)

**TextArea**:
- `autoResize=true` → Textarea wächst beim Tippen, kein Scrollbalken
- `showCharCount=true` + `maxLength` → Zähler unten rechts, aktualisiert sich
- Bei `maxLength` überschritten → Zähler rot oder deutlich markiert (falls so implementiert)

**SectionHeader**:
- Collapsed: Inhalt nicht sichtbar, `aria-expanded="false"` im DOM (DevTools)
- Expanded: Inhalt sichtbar, `aria-expanded="true"`
- `count` prop → CountBadge neben dem Titel
- `onAdd` → „+"-Button erscheint, Klick darauf klappt Header NICHT zusammen
- `isCollapsible=false` → kein Toggle-Button, immer expanded

### Accessibility-Checks (manuell, Storybook)

Diese Checks sind nicht automatisiert — einmal nach Erstimplementierung, dann bei Änderungen:

- **Button + TextInput/TextArea**: Tab-Navigation funktioniert, Focus-Ring sichtbar
- **TextInput mit errorMessage**: Screen Reader würde Fehler ankündigen
  → DevTools prüfen: `aria-invalid="true"` am `<input>`, `role="alert"` an Fehlermeldung
- **Avatar**: Falls kein `alt`-Text → `aria-hidden="true"` (dekorativ)
- **SectionHeader**: `aria-expanded` korrekt gesetzt, Button hat zugänglichen Namen

---

## Manuskriptansicht — Visuelle Checks

Diese Checks laufen nach Änderungen an Manuskript-Komponenten. Ziel: Layout, Token-Compliance,
Accessibility-Attribute im DOM — was Unit-Tests nicht sehen.

### WordCountLabel

- `size="sm"`: Schrift deutlich kleiner als `size="md"` — visuell unterscheidbar
- Zahl mit Tausender-Separator: `1240` → zeigt `"1.240 Wörter"` (deutsches Format)
- Token: `font-size` kommt aus CSS-Variable, kein Hardcode

### AutosaveIndicator

- Status-Farben Token-konform: success → grün (`--color-success`), error → rot (`--color-error`)
- `aria-live="polite"` im DOM: DevTools → Element inspizieren, Attribut vorhanden
- Status-Wechsel visuell erkennbar (nicht nur Text, auch Farbe)

### Breadcrumb

- Letztes Segment nicht klickbar — kein Hover-Effekt, kein Cursor-Pointer
- Separator-Zeichen klar sichtbar zwischen Segmenten
- `<nav aria-label="Breadcrumb">` im DOM (DevTools)
- `aria-current="page"` am letzten Segment (DevTools)

### SceneBreak

- Zwei horizontale Linien links und rechts des Titels — symmetrisch
- Linien haben `aria-hidden="true"` (DevTools)
- Titel zentriert, visuell als Szenentrennzeichen erkennbar

### BottomBar

- Klebt am unteren Bildschirmrand (fixed) — scrollt NICHT mit dem Inhalt mit
- Wort­zahl und Speicher-Status nebeneinander sichtbar
- Background: `--color-surface` (nicht transparent, nicht `--color-background`)
- Obere Border vorhanden — trennt vom Inhalt

---

## Known limitations

- **EpistemicBadge** requires a model with slots — only visible after running the full
  Analyse → WirkgefügeVorschlag → Save flow. `tsc` passing is the fallback verification.
- **NarrativeAnalyse / WirkgefuegeVorschlag** require an Anthropic API call to reach —
  cannot be verified in every run. Verify after intentional changes to those screens.
