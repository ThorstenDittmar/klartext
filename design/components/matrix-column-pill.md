# MatrixColumnPill

## Purpose

Pill-förmiger Spalten-Header in der MatrixTable — zeigt den Entitätsnamen kompakt und farbig. Bei langen Namen: abgekürzt mit Tooltip. Ermöglicht Spalten-Aktionen via ContextMenu.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Normaler Spalten-Header | Farb-Pill mit Label |
| `rotated` | Viele Spalten / enge Matrix | Pill um 90° rotiert für mehr Kompaktheit |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `hover` | Mouse over | Tooltip zeigt vollständigen Namen |
| `highlighted` | Entsprechende Zelle ist hovered | Pill hervorgehoben (Kreuzpunkt-Logik) |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Entitäts-ID |
| `label` | `string` | yes | — | Anzuzeigende Bezeichnung |
| `colorKey` | `string \| null` | no | `null` | Token-Key für Pill-Farbe |
| `isHighlighted` | `boolean` | no | `false` | Kreuzpunkt-Highlight aktiv |
| `onContextMenu` | `((e: React.MouseEvent) => void) \| null` | no | `null` | Rechtsklick |
| `variant` | `"default" \| "rotated"` | no | `"default"` | Ausrichtung |

---

## Rules

- Label wird ab ~15 Zeichen abgeschnitten — Tooltip zeigt vollständigen Text
- Farbe kommt als Token-Key, nie als direkter Hex-Wert
- Kein inline Edit des Labels im Pill — Entität muss über normalen Bearbeitungsweg geändert werden

---

## Accessibility

- Tooltip via `aria-describedby` wenn Label abgeschnitten
- `title` Attribut als nativer Tooltip-Fallback

---

## Code Pattern

```tsx
<MatrixColumnPill
  id={actor.id}
  label={actor.name}
  colorKey={`actor.color.${actor.colorIndex}`}
  isHighlighted={hoveredColumnId === actor.id}
  onContextMenu={(e) => openColumnMenu(e, actor.id)}
/>
```

---

## Do / Don't

❌ Pill-Farbe als direkten Hex-Wert übergeben
✅ Token-Key übergeben, Component löst auf

---

## Missing Information Protocol

```tsx
// TODO(design): Pill-Farb-Token-Palette — Issue #TODO
// TODO(design): Maximale Label-Länge vor Truncation — Issue #TODO
// TODO(design): Rotations-Schwellenwert (ab wie vielen Spalten?) — Issue #TODO
```

---

## Related

- `matrix-table.md` — Verwendet MatrixColumnPill als Spalten-Header
- `badge.md` — Ähnliche Pill-Form aber für Statusanzeige, nicht Navigation
