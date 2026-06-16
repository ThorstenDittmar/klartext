# Frontend Testing — Vollständigkeitskriterien

> **Dieses Dokument beschreibt das WAS und WANN — nicht das WIE.**
> Das technische Wie (Stack, Query-Hierarchie, `renderWithProviders`, `vi.mock`)
> steht in `docs/method/enactment/skills/frontend.md`.

---

## Schichten-Äquivalente

Das Backend hat vier Testschichten (Domain / Service / Repository / Router).
Das Frontend hat drei:

| Frontend | Backend-Äquivalent | Was wird getestet |
|---|---|---|
| Hook | Domain + Service | Reine Logik: Zustandsübergänge, Return-Werte, Fehler-State |
| Component | Service | Darstellungslogik: Render-Varianten, Interaktionen, i18n |
| Page | Router | Vollintegration: Datenladen, alle States, User-Flows — API gemockt |

**E2E (Playwright) ist kein Teil dieser Ebenen** — es testet echte Browser + Backend.
Kriterien dafür stehen nicht in diesem Dokument.

---

## Vollständigkeitskriterien

### Page

Eine Page ist ausreichend getestet wenn folgende Szenarien abgedeckt sind:

**Obligatorisch:**

| Szenario | Warum obligatorisch |
|---|---|
| Loading state sichtbar | Spinner/Skeleton verhindert Blank-Screen-Bugs |
| Success state — Daten rendern | Kernfunktion der Page |
| API-Fehler → Fehlermeldung sichtbar | Kein stiller Fehler, kein Infinite Spinner |
| 404 / Ressource nicht gefunden | Wenn die Page eine spezifische Ressource lädt |
| User-Interaktion Happy Path | Jede Aktion die persistiert werden soll (mindestens 1) |

**Optional (empfohlen, kein Review-Blocker):**

- Empty state (Liste ist leer nach erfolgreichem Load)
- Mehrere gleichzeitige Fehler-Zustände
- Optimistic UI / Race conditions

**Trigger: wann braucht eine neue Page einen Test?**
Immer — keine Page shipped ohne Testdatei.

---

### Component

Ein Component ist ausreichend getestet wenn:

**Obligatorisch:**

| Szenario | Warum obligatorisch |
|---|---|
| Default-Render mit minimal required Props | Verhindert Crash bei der häufigsten Verwendung |
| Jede visuelle Variante | z.B. `active/inactive`, `error/success`, `loading/loaded` |
| User-Interaktion → Callback aufgerufen | Sichert dass `onClick`, `onChange` etc. verdrahtet sind |
| i18n — mindestens ein übersetzter String vorhanden | Verhindert fehlende/falsche Keys in Production |

**Optional:**

- Edge cases mit extremen Props (sehr langer Text, leere Array, `null`)
- Keyboard-Navigation und Fokus-Verhalten (wichtig für Accessibility, aber kein QA-Blocker)

**Trigger: wann braucht ein neues Component einen Test?**
Wenn es eigene Logik hat (Interaktion, Conditional Rendering, Datenformatierung).
Reine Layout-Wrapper ohne Logik können übersprungen werden — Urteil liegt beim QA-Review.

---

### Hook

Ein Hook ist ausreichend getestet wenn:

**Obligatorisch:**

| Szenario | Warum obligatorisch |
|---|---|
| Initial State | Was liefert der Hook beim ersten Render? |
| Success Path — State nach API-Call | `data` korrekt, `isLoading` false, `error` null |
| Error Path — State nach API-Fehler | `error` gesetzt, `isLoading` false, `data` leer/null |
| `isLoading` während des Calls | Verhindert Zustand wo UI auf nie-kommende Daten wartet |
| Callback-Aufruf triggert State-Update | Sichert dass die zurückgegebenen Funktionen funktionieren |

**Optional:**

- Debouncing / Throttling-Verhalten
- Refetch-Logik nach State-Änderungen
- Cache-Invalidierung

**Trigger: wann braucht ein neuer Hook einen Test?**
Immer — kein Hook shipped ohne Test. Hooks sind die einzige Schicht wo
API-Logik und State zusammenkommen, Bugs hier propagieren in alle Pages.

---

## Obligatorische Fehlerpfade

Diese Fehlerpfade müssen immer getestet sein — kein optionaler Ermessensspielraum:

| Wo | Fehlerpfad | Erwartung |
|---|---|---|
| Jede Page mit API-Call | Netzwerkfehler / 500 | Fehlermeldung sichtbar, kein Infinite Spinner |
| Jede Page die Ressource per ID lädt | 404 Not Found | Sinnvolle Meldung, kein Crash |
| Jeder Hook mit `async` | `rejected` Promise | `error`-State gesetzt, `isLoading` false |
| Jedes Component mit `error`-Prop | Error-Zustand gerendert | Error-Variante sichtbar im DOM |

**Nicht obligatorisch (kann aber reviewt werden):**

- 401 / 403 — nur wenn die Page explizit Auth-Logik hat
- Timeout-Szenarien
- Mehrfach-Klick / Double-Submit

---

## Abgrenzung zu E2E

Frontend-Unit-Tests decken ab:
- Alle States innerhalb einer Page/Component/Hook
- API-Responses (gemockt — kein echter Server)
- Routing nur über `MemoryRouter` (kein echter Browser)

E2E-Tests (Playwright) decken ab:
- Echter Browser + echter Backend-Request
- Auth-Flows end-to-end
- Navigation über mehrere Pages
- Formulare, die echte Datenbankänderungen verursachen

**QA reviewt keine E2E-Vollständigkeit im normalen Review-Flow.**
E2E-Kriterien kommen in ein separates Dokument wenn dieser Bereich etabliert wird.

---

## QA Review — Checkliste

Wenn QA nach einer Frontend-Implementierung reviewt:

### Struktur-Check (maschinell prüfbar)

```bash
# Gibt es Testdateien für neue Pages?
find frontend/src/pages/__tests__ -name "*.test.tsx"

# Gibt es Testdateien für neue Components mit Logik?
find frontend/src/components/__tests__ -name "*.test.tsx"

# Gibt es Testdateien für neue Hooks?
find frontend/src/hooks/__tests__ -name "*.test.tsx"
```

### Inhalt-Check (manuell, pro Testdatei)

**Für jede neue Page:**
- [ ] Loading state getestet (`waitFor` + Spinner/Skeleton)
- [ ] Success state getestet (Daten im DOM)
- [ ] API-Fehler getestet (Fehlermeldung im DOM)
- [ ] 404-Fall getestet (wenn Page eine Ressource per ID lädt)
- [ ] Happy Path für Haupt-Interaktion getestet (wenn Buttons/Formulare vorhanden)

**Für jede neue Component mit Logik:**
- [ ] Default-Render getestet
- [ ] Alle visuellen Varianten getestet
- [ ] User-Interaktion → Callback aufgerufen getestet
- [ ] Mindestens ein i18n-String verifiziert

**Für jeden neuen Hook:**
- [ ] Initial State verifiziert
- [ ] Success Path verifiziert
- [ ] Error Path verifiziert
- [ ] `isLoading` während des Calls verifiziert

### Qualitäts-Check (Überall)

- [ ] Kein `setTimeout` in Tests — nur `waitFor`
- [ ] Kein echter API-Aufruf — alle Calls mit `vi.mock` gemockt
- [ ] `renderWithProviders()` verwendet wo i18n oder Router nötig
- [ ] Queries folgen der Hierarchie: `getByRole` > `getByLabelText` > `getByText` > `getByTestId`

---

## Bezug zur Quality Checklist in frontend.md

Die Tests-Sektion der Quality Checklist in `frontend.md` beschreibt die Mindestanforderungen
die UX/UI beim Commit prüft. Die Kriterien hier sind feiner granuliert und dienen QA beim Review.

Wenn QA einen Testtyp vermisst der nicht in der frontend.md-Checkliste steht:
→ Briefing an UX/UI formulieren mit Vorschlag für Ergänzung der Checkliste.

---

## Shared Components — Kritische Props-Kombinationen

Diese Sektion ergänzt die allgemeinen Component-Kriterien um komponentenspezifische
Kombinationen wo Bugs erfahrungsgemäß versteckt sind.

### Button

| Kombination | Was getestet werden muss |
|---|---|
| `isLoading=true` | `disabled` gesetzt UND `aria-busy="true"` — beide, nicht nur einer |
| `disabled=true` | `onClick` wird NICHT aufgerufen |
| `variant="nav-item"` + `isActive=true` | Active-Styling sichtbar im DOM |
| `variant="nav-item"` + `isActive=false` | Kein Active-Styling |

Tückisch: `isLoading` muss beides gleichzeitig setzen. Wenn nur `disabled` oder nur `aria-busy`
gesetzt wird, ist entweder Accessibility oder Interaktion kaputt.

### Badge

- Jede `colorKey`-Variante (`green`, `amber`, `red`, `blue`, `teal`, `default`) rendert ohne Crash
- Kein onClick, kein Interaktions-Test nötig

### CountBadge

| Kombination | Was getestet werden muss |
|---|---|
| `count=0` (default: `hideWhenZero=true`) | Rendert `null` — nicht leer, nicht `0` |
| `count=0` + `hideWhenZero=false` | Rendert sichtbare `0` |
| `count > max` (default max=99) | Zeigt `"99+"`, nicht die echte Zahl |
| `variant="dot"` | Keine Zahl im DOM |

Tückisch: `hideWhenZero=true` ist der Default. Ein Test mit `count=0` der keinen null-Check macht
besteht auch wenn die Komponente fälschlicherweise `0` anzeigt.

### InlineCodeBadge

- `copyable=true` → Copy-Button im DOM vorhanden
- Copy-Button-Klick → Clipboard-Interaktion ausgelöst (mit `navigator.clipboard` mock)
- `<code>`-Element gerendert (semantisches HTML)

### Avatar

| Szenario | Was getestet werden muss |
|---|---|
| `src` vorhanden, Bild lädt | Img-Element gerendert |
| `src` vorhanden, Bild lädt NICHT (onError) | Fällt auf Initialen zurück |
| Kein `src`, `name` vorhanden | Initialen-Fallback direkt |
| Kein `src`, kein `name` | Placeholder-Fallback |
| Gleicher `name` zweimal | Selbe Initialen-Farbe (deterministischer Hash) |

Tückisch: Der img-onError-Fallback ist async. Test muss das Bild-Load-Failure simulieren,
nicht nur `src` weglassen.

⚠️ **Bekannte Lücke:** Der Fallback-Test (`src` lädt nicht → Initialen) fehlt aktuell.
Nur der Happy Path (Bild vorhanden) ist getestet. Wird nachgezogen.

### EmptyState

Props sind per Discriminated Union erzwungen — TypeScript erlaubt nur zwei gültige Kombinationen:

| Kombination | Was getestet werden muss |
|---|---|
| Beide Props (`actionLabel` + `onAction`) | Button sichtbar, Klick ruft `onAction` auf |
| Keine Props | Kein Button im DOM |

Die ungültige Kombination (`actionLabel` ohne `onAction`) ist ein Compile-Fehler — kein Test nötig.
- `title` rendert immer (Pflicht-Prop)
- `subtitle` optional → Test mit und ohne

### SearchInput

| Kombination | Was getestet werden muss |
|---|---|
| `value=""` | Clear-Button NICHT im DOM |
| `value="x"` | Clear-Button im DOM |
| Clear-Button-Klick | `onChange("")` aufgerufen — nicht internal state |

Tückisch: Komponente ist controlled. Clear-Button muss `onChange` aufrufen, nicht selbst state
setzen. Wenn er state setzt, löscht er visuell aber der Parent weiß nichts davon.

### TextInput

| Kombination | Was getestet werden muss |
|---|---|
| `errorMessage` gesetzt | `aria-invalid="true"` am `<input>`, `role="alert"` an Fehlermeldung |
| `helperText` + `errorMessage` gleichzeitig | Nur `errorMessage` sichtbar |
| `readOnly=true` | Input hat `readOnly`-Attribut |
| `disabled=true` | Input hat `disabled`-Attribut |
| Label immer | `<label>` mit `htmlFor` verknüpft mit Input-`id` |

Tückisch: `aria-invalid` muss am `<input>` hängen, nicht am Wrapper. Und `role="alert"`
muss an der Fehlermeldung selbst sein, damit Screen Reader sie vorlesen.

### TextArea

- Wie TextInput, plus:
- `showCharCount=true` + `maxLength=N` → zeigt `"0 / N"` initial
- Zähler aktualisiert sich wenn `value` sich ändert
- `autoResize=true` → Element hat kein `overflow: hidden` (nicht deaktiviert)

Hinweis: `autoResize` ist schwer unit-zu-testen (scrollHeight im jsdom ist immer 0).
Wenn der Test nicht aussagekräftig ist, lieber weglassen und in verify.md notieren.

### SectionHeader

| Kombination | Was getestet werden muss |
|---|---|
| `isCollapsible=true` (default) | Toggle-Button im DOM, `aria-expanded` vorhanden |
| Klick auf Toggle | `aria-expanded` wechselt zwischen true/false |
| `isCollapsible=false` | Kein Toggle-Button im DOM |
| `count` prop | CountBadge im DOM (wenn count > 0) |
| `onAdd` + Klick | `onAdd`-Callback aufgerufen |
| `onAdd` + Klick | Collapse-State ändert sich NICHT (Propagation gestoppt) |

Tückisch: Der letzte Punkt ist der kritischste. Wenn `onAdd`-Klick durch Event-Propagation
auch den Toggle auslöst, klappt der Header bei jedem „+" -Klick zusammen.
Test: SectionHeader mit `isCollapsible=true` + `onAdd`. Klick auf „+`. `aria-expanded`
muss identisch bleiben.

---

## Manuskriptansicht — Kritische Props-Kombinationen

Komponenten aus der Manuskriptansicht (Phase 1). Gleiche Kategorisierung wie Shared Components.

### WordCountLabel

| Kombination | Was getestet werden muss |
|---|---|
| `count=1240` (kein suffix) | Rendert `"1.240 Wörter"` — deutsches Tausend-Trennzeichen |
| `count=0` | Rendert `"0 Wörter"` — KEINE Unterdrückung (keine `hideWhenZero`-Logik) |
| `suffix="Zeichen"` | Rendert mit alternativem Suffix |
| `size="sm"` | Element vorhanden und rendert ohne Crash |
| `size="md"` | Element vorhanden und rendert ohne Crash |

Tückisch: `count.toLocaleString("de-DE")` — im jsdom-Default-Locale kann das variieren.
Test muss das Locale explizit steuern oder den Output `"1.240"` exakt assertieren.

⚠️ **Bekannte Lücke:** `size`-Varianten sind nicht differenziert getestet (SM vs. MD).
Schwer unit-testbar (CSS Custom Property, kein DOM-Attribut). Statt Lücke schließen:
in verify.md prüfen.

### AutosaveIndicator

| Kombination | Was getestet werden muss |
|---|---|
| `status="saved"` | Gespeichert-Label sichtbar |
| `status="saving"` | Speichern-Label sichtbar |
| `status="unsaved"` | Ungespeichert-Label sichtbar |
| Custom label-Props | Eigenes Label überschreibt Default |
| `aria-live="polite"` | Attribut am span vorhanden — kein optionaler Check |

Alle 3 Status-Varianten sind obligatorisch. `aria-live` ist Accessibility-Pflicht.

### Breadcrumb

| Kombination | Was getestet werden muss |
|---|---|
| Letztes Segment | `aria-current="page"` gesetzt, KEIN onClick |
| Nicht-letztes Segment | `<button>`-Element, Klick ruft `onClick` auf |
| `separator="chevron"` (default) | `"›"` zwischen Segmenten |
| `separator="slash"` | `"/"` zwischen Segmenten |
| Einzelnes Segment | Kein Separator im DOM |
| `<nav aria-label="Breadcrumb">` | Semantische Navigation-Rolle |

Tückisch: Separator-Variante wird leicht vergessen. Beide Separator-Werte müssen
getestet sein — ein Test für `separator="chevron"` (default) ist kein Beweis dass
`"slash"` korrekt rendert.

⚠️ **Bekannte Lücke (PR #41):** `separator="slash"` nicht getestet. Muss vor Phase 2 ergänzt werden.

### SceneBreak

| Kombination | Was getestet werden muss |
|---|---|
| `title` vorhanden | Text im DOM sichtbar |
| Dekorative Elemente | Exakt 2 Elemente mit `aria-hidden="true"` |

Keine Interaktion, keine Varianten. Rein strukturell.

### BottomBar

| Kombination | Was getestet werden muss |
|---|---|
| `wordCount` prop | Wird als formatierter Text delegiert (via WordCountLabel) |
| `saveStatus="saved"` | Autosave-Label "Gespeichert" sichtbar |
| `saveStatus="saving"` | Autosave-Label "Wird gespeichert…" sichtbar |
| `saveStatus="unsaved"` | Autosave-Label "Ungespeichert" sichtbar |
| `<footer>` Element | Semantisches HTML — kein `<div>` |

Alle 3 SaveStatus-Varianten obligatorisch — delegiert zwar an AutosaveIndicator,
aber der Kompositions-Wiring muss getestet sein.
`position: fixed` ist nicht unit-testbar — nur in verify.md.
