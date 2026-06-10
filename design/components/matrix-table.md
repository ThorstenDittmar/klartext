# MatrixTable

## Purpose

Zweidimensionale Kreuztabelle — Zeilen und Spalten repräsentieren je eine Entitätsmenge (z.B. Szenen × Akteure, Szenen × Wirkungsfaktoren). Zellen zeigen Beziehungen oder Werte. Scrollt horizontal und vertikal.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `presence` | Binäre Beziehung (vorhanden/nicht) | Zellen: Checkbox oder Symbol |
| `value` | Numerischer Wert pro Zell-Kreuzpunkt | Zellen: Zahl oder Icon-Intensität |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `cell-hover` | Mouse über Zelle | Zeilen + Spalten-Header hervorgehoben |
| `row-selected` | Zeile angeklickt | Zeile hervorgehoben |
| `loading` | Daten werden geladen | Skeleton-Tabelle |
| `empty` | Keine Daten | EmptyState an Stelle der Tabelle |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `rowEntities` | `Array<{ id: string; label: string }>` | yes | — | Zeilen-Entitäten |
| `columnEntities` | `Array<{ id: string; label: string }>` | yes | — | Spalten-Entitäten |
| `cells` | `Record<string, Record<string, MatrixCellValue>>` | yes | — | Zellinhalte: `cells[rowId][colId]` |
| `variant` | `"presence" \| "value"` | no | `"presence"` | Zelltyp |
| `onCellClick` | `((rowId: string, colId: string) => void) \| null` | no | `null` | Zell-Interaktion |
| `onRowClick` | `((rowId: string) => void) \| null` | no | `null` | Zeilen-Auswahl |
| `isLoading` | `boolean` | no | `false` | Loading-State |

---

## Rules

- Header-Zeile und Header-Spalte sind sticky (bleiben beim Scrollen sichtbar)
- Zellen-Labels die nicht passen werden mit Tooltip vollständig angezeigt
- Bei Hover: Kreuzpunkt-Highlighting (Zeile + Spalte der aktuellen Zelle)
- Bei sehr vielen Zeilen/Spalten: Virtualisierung nötig — noch nicht spezifiziert

---

## Accessibility

- `<table>` mit `<caption>` für den Gesamt-Kontext
- Header-Zellen als `<th scope="col">` / `<th scope="row">`
- Interaktive Zellen: `role="button"` oder `<button>` im Zell-Inhalt
- Keyboard-Navigation: Tab-Reihenfolge durch Zellen

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ MatrixTable ohne sticky Header
✅ Immer `position: sticky` für Zeilen- und Spalten-Header

❌ Inline-Bearbeitung in der Matrix
✅ DetailPanel oder Modal für Bearbeitung öffnen

---

## Missing Information Protocol

```tsx
// TODO(design): Zell-Größe und Mindestbreite — Issue #TODO
// TODO(design): Kreuzpunkt-Highlight-Farbe als Token — Issue #TODO
// TODO(tech): Virtualisierung für große Matrizen — Issue #TODO
// TODO(design): Spalten-Header Rotation bei langen Labels — Issue #TODO
```

---

## Related

- `matrix-column-pill.md` — Spalten-Header als Pill-Element
- `entity-list-item.md` — Alternativ-Ansicht für dieselben Entitäten
- `empty-state.md` — Wenn Matrix leer ist
