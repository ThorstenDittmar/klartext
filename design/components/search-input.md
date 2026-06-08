# SearchInput

## Purpose

Einzeiliges Texteingabefeld mit Lupe-Icon und optionalem Clear-Button — ausschließlich für die Echtzeit-Filterung von Listen. Kein Submit, kein Server-Request direkt aus der Komponente.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standalone Suche | Lupe links, optionaler Clear-Button rechts |
| `inline` | Kompakt in einem Panel oder Header | Schmalere Höhe, kein äußerer Rahmen |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `empty` | Kein Text eingegeben | Placeholder sichtbar, kein Clear-Button |
| `active` | Text eingegeben | Clear-Button erscheint |
| `focused` | Fokus via Klick oder Tab | Fokus-Ring |
| `disabled` | `disabled` prop | Gedimmt, nicht klickbar |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `value` | `string` | yes | — | Kontrollierter Wert |
| `onChange` | `(value: string) => void` | yes | — | Callback bei Änderung |
| `placeholder` | `string` | no | — | Placeholder-Text (via t()-Key) |
| `autoFocus` | `boolean` | no | `false` | Fokus beim Mounten |
| `disabled` | `boolean` | no | `false` | Deaktivierter Zustand |
| `variant` | `"default" \| "inline"` | no | `"default"` | Visueller Stil |

---

## Rules

- SearchInput ist immer kontrolliert — kein uncontrolled state
- Debouncing liegt in der Page/Hook die SearchInput verwendet, nicht in der Komponente selbst
- Clear-Button löscht den Wert und setzt den Fokus zurück in das Feld
- Kein Submit-Button, kein onSubmit-Handler

---

## Accessibility

- `role="searchbox"` oder `type="search"` auf dem Input-Element
- `aria-label` wenn kein sichtbares Label vorhanden ist
- Clear-Button mit `aria-label="Suche löschen"`
- Escape leert das Feld wenn Fokus im SearchInput ist

---

## Code Pattern

```tsx
const [searchQuery, setSearchQuery] = useState("")

<SearchInput
  value={searchQuery}
  onChange={setSearchQuery}
  placeholder={t("scenes.search.placeholder")}
/>
```

---

## Do / Don't

❌ Debouncing im SearchInput implementieren
✅ Debouncing im Hook (`useSearch`) implementieren

❌ SearchInput für Formular-Felder verwenden
✅ TextInput für Formular-Felder

---

## Missing Information Protocol

```tsx
// TODO(design): Fokus-Ring Farbe als Token — Issue #TODO
// TODO(design): Clear-Button Icon (X) Spezifikation — Issue #TODO
// TODO(a11y): Keyboard Shortcut für schnellen Fokus (Cmd+F) — Issue #TODO
```

---

## Related

- `text-input.md` — Allgemeines Formular-Eingabefeld
- `empty-state.md` — Wird angezeigt wenn Suche keine Treffer hat (`search-no-results` Variante)
- `entity-list-item.md` — Die gefilterten Einträge unterhalb der SearchInput
