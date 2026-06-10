# SceneCard

## Purpose

Karte in der Karten-Ansicht des Szenenplans — zeigt eine Szene als visuellen Block mit Titel, optionaler Kurzbeschreibung, Status-Farbe und Szenen-Nummer. Draggable für manuelle Reihenfolge.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard Szenen-Karte | Farbiger Rand/Kopf (nach Szenentyp), Titel, optionaler Text |
| `compact` | Schmale Karten-Spalte | Weniger Padding, kleinere Schrift |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `hover` | Mouse over | Schatten erhöht sich |
| `selected` | Karte geklickt | Rand hervorgehoben, bleibt bis zur Deselection |
| `dragging` | Drag gestartet | Transparenz + Schatten |
| `drag-over` | Anderes Element wird darüber gezogen | Drop-Zone Indikator |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Szenen-ID |
| `title` | `string` | yes | — | Szenen-Titel |
| `sceneNumber` | `number` | yes | — | Szenen-Nummer (1-basiert) |
| `description` | `string \| null` | no | `null` | Kurzbeschreibung oder ersten Satz |
| `colorKey` | `string` | no | — | Token-Key für Szenen-Typ-Farbe |
| `isSelected` | `boolean` | no | `false` | Ausgewählt |
| `onClick` | `() => void` | yes | — | Klick-Callback |
| `onContextMenu` | `((e: React.MouseEvent) => void) \| null` | no | `null` | Rechtsklick |
| `isDraggable` | `boolean` | no | `false` | Drag & Drop aktiviert |
| `variant` | `"default" \| "compact"` | no | `"default"` | Visueller Stil |

---

## Rules

- Szenen-Farbe kommt als Token-Key, nie als direkter Hex-Wert
- Szenen-Nummer wird immer angezeigt — keine optionale Ausblendung
- Karte öffnet DetailPanel bei Klick — kein direktes Navigieren
- Beschreibung wird abgeschnitten nach 2 Zeilen (CSS `line-clamp`)

---

## Accessibility

- Fokussierbar
- `aria-selected` spiegelt `isSelected`
- Keyboard: Enter öffnet DetailPanel

---

## Code Pattern

```tsx
<SceneCard
  id={scene.id}
  title={scene.title}
  sceneNumber={index + 1}
  description={scene.summary}
  colorKey={`scene.type.${scene.type}`}
  isSelected={selectedId === scene.id}
  onClick={() => setSelectedId(scene.id)}
  isDraggable
/>
```

---

## Do / Don't

❌ Szenen-Farbe direkt als Hex übergeben
✅ `colorKey` als Design-Token-Key

❌ Vollständigen Text in der Karte anzeigen
✅ 2-Zeilen-Limit mit `line-clamp` + Tooltip oder DetailPanel für vollen Text

---

## Missing Information Protocol

```tsx
// TODO(design): Karten-Breite pro Szenentyp — Issue #TODO
// TODO(design): Farbpalette für Szenentypen (Token-Keys) — Issue #TODO
// TODO(ux): Drag & Drop Bibliothek — noch nicht entschieden — Issue #TODO
// TODO(design): Schatten-Tokens für Hover/Dragging — Issue #TODO
```

---

## Related

- `entity-list-item.md` — Listen-Ansicht derselben Szene
- `detail-panel.md` — Öffnet sich bei Klick
- `context-menu.md` — Bei Rechtsklick
- `act-container.md` — SceneCards werden darin gruppiert
- `drag-handle.md` — Drag-Auslöser
