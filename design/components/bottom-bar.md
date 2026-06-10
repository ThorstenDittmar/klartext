# BottomBar

## Purpose

Persistente untere Leiste — zeigt globale Aktionen (Export, Prompts, Help) und Status-Informationen (User-Avatar, Speicher-Status, Tutorial-Fortschritt). Existiert einmal pro Seite, immer sichtbar.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard | Avatar links, globale Aktionen, Status rechts |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `saving` | Auto-Save läuft | „Saving…" statt „Saved" Indikator |
| `saved` | Letzter Save erfolgreich | „Saved" mit Häkchen o.ä. |
| `unsaved` | Ungespeicherte Änderungen | TODO(design): nicht spezifiziert — Issue #TODO |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `saveStatus` | `"saving" \| "saved" \| "unsaved" \| null` | no | `null` | Speicher-Status |
| `onHelpClick` | `() => void` | no | — | Öffnet Help-Panel |
| `onPromptsClick` | `() => void` | no | — | Öffnet Prompts-Panel |
| `onExportClick` | `() => void` | no | — | Öffnet Export-Dialog |
| `tutorialProgress` | `{ current: number; total: number } \| null` | no | `null` | Zeigt TutorialProgress wenn gesetzt |

---

## Rules

- BottomBar ist nie scrollbar — bleibt sticky am unteren Rand
- Aktionen immer via `t('key')` beschriftet
- Kein kritischer Inhalt in der BottomBar — nur unterstützende Aktionen

---

## Accessibility

- `footer` oder `nav` als HTML-Element
- Alle Buttons mit sichtbarem Label oder `aria-label`
- Status-Indikator via `aria-live="polite"` ankündigen

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ Primäre Aktionen (Speichern, Erstellen) in die BottomBar legen
✅ BottomBar nur für unterstützende/globale Aktionen

---

## Missing Information Protocol

```tsx
// TODO(design): BottomBar-Höhe als Token — Issue #TODO
// TODO(design): Unsaved-Indikator-Visual nicht spezifiziert — Issue #TODO
// TODO(i18n): Help, Prompts, Export als t()-Keys — Issue #TODO
```

---

## Related

- `tutorial-progress.md` — optionaler Fortschritts-Badge in der BottomBar
- `avatar.md` — User-Avatar links in der BottomBar
- `app-bar.md` — oberes Pendant
