# AutosaveIndicator

## Purpose

Zeigt den Speicher-Zustand im Manuskript-Editor — drei Zustände: Speichert…, Gespeichert ✓, Nicht gespeichert ⚠. Wird in der BottomBar verwendet.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `saving` | Debounce-Fenster läuft | "Speichert…" in Sekundärfarbe |
| `saved` | Letzter Save erfolgreich | "Gespeichert ✓" in Success-Farbe |
| `unsaved` | Fehler oder offline | "Nicht gespeichert ⚠" in Error-Farbe |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | `"saving" \| "saved" \| "unsaved"` | yes | — | Aktueller Speicher-Zustand |
| `savingLabel` | `string` | no | `"Speichert…"` | TODO(i18n) |
| `savedLabel` | `string` | no | `"Gespeichert ✓"` | TODO(i18n) |
| `unsavedLabel` | `string` | no | `"Nicht gespeichert ⚠"` | TODO(i18n) |

---

## Rules

- Zustandswechsel mit `transition: color 0.3s` animiert
- Nur Text, kein eigener Spinner — BottomBar-Kontext hat keine Höhe für Animationen
- `aria-live="polite"` damit Screenreader Änderungen ankündigt

---

## Missing Information Protocol

```tsx
// TODO(design): Transition-Dauer als Token — Issue #TODO
// TODO(i18n): Labels via t() sobald i18next installiert — Issue #TODO
```

---

## Related

- `bottom-bar.md` — AutosaveIndicator lebt in der BottomBar
