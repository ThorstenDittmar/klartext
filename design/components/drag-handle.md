# DragHandle

## Purpose

Kleines Griff-Icon das Drag & Drop-Interaktion auf einem Element auslöst — zeigt visuell an dass ein Element sortierbar ist. Wird als eigenes Element gerendert, nicht als Overlay.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard | Sechs-Punkte-Grid-Icon (⠿) |
| `dots` | Kompakt | Zwei-Spalten-Punkte-Icon |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | Icon sichtbar oder semi-transparent |
| `hover` | Mouse über Handle oder Parent-Element | Icon volle Sichtbarkeit, Cursor `grab` |
| `dragging` | Drag aktiv | Cursor `grabbing` |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `dragHandleRef` | `React.RefObject<HTMLDivElement>` | yes | — | Ref wird von Drag-Bibliothek benötigt |
| `variant` | `"default" \| "dots"` | no | `"default"` | Icon-Stil |
| `isVisible` | `"always" \| "on-hover"` | no | `"on-hover"` | Sichtbarkeit |

---

## Rules

- DragHandle ist kein Button — kein onClick
- Sichtbarkeit `on-hover` bedeutet: sichtbar wenn Parent-Element gehovered wird
- DragHandle immer ganz links oder ganz rechts im Parent-Element positioniert
- Drag-Bibliothek (noch nicht entschieden) bestimmt den `ref`-Mechanismus

---

## Accessibility

- `aria-label="Sortieren"` oder `aria-roledescription="Sortierbarer Griff"`
- Keyboard-Sortierung wird durch die Drag-Bibliothek realisiert — Handle allein reicht nicht
- Fokussierbar wenn Keyboard-Drag unterstützt wird

---

## Code Pattern

```tsx
// Bibliotheks-Beispiel (dnd-kit Stil — noch nicht final)
const { attributes, listeners, setNodeRef } = useSortable({ id })

<EntityListItem>
  <DragHandle dragHandleRef={setNodeRef} {...listeners} {...attributes} />
  {/* Rest des Inhalts */}
</EntityListItem>
```

---

## Do / Don't

❌ Die gesamte Zeile/Karte als Drag-Trigger verwenden
✅ Explizites DragHandle — verhindert unbeabsichtigte Drags bei Klicks

---

## Missing Information Protocol

```tsx
// TODO(tech): Drag-Bibliothek noch nicht entschieden (dnd-kit, react-beautiful-dnd) — Issue #TODO
// TODO(design): Icon-Stil (Dots vs. Lines) — Issue #TODO
// TODO(design): Hover-Sichtbarkeit vs. immer sichtbar — Issue #TODO
```

---

## Related

- `entity-list-item.md` — Verwendet DragHandle für Sortierung
- `scene-card.md` — Verwendet DragHandle für Karten-Sortierung
