# EntityListItem

## Purpose

Einzel-Zeile in einer scrollbaren Liste — repräsentiert eine Entität (Narrativ, Szene, Kapitel, Akteur). Klick öffnet das DetailPanel oder navigiert. Unterstützt Drag & Drop für manuelle Sortierung.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard-Listeneintrag | Titel, optional Subtitle, rechts Badges/Icons |
| `compact` | Dicht gepackte Listen (Sidebar) | Kleinere Schrift, weniger vertikaler Abstand |
| `with-thumbnail` | Einträge mit Vorschaubild | Thumbnail links, Titel + Subtitle rechts |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `hover` | Mouse over | Hintergrund-Highlight |
| `active` | Eintrag ausgewählt / DetailPanel offen | Persistentes Highlight, andere Farbe als hover |
| `dragging` | Drag & Drop aktiv | Schatten, leicht skaliert |
| `drag-over` | Anderes Element wird darüber gezogen | Drop-Indikator (Linie oben/unten) |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Entitäts-ID |
| `title` | `string` | yes | — | Haupttitel |
| `subtitle` | `string \| null` | no | `null` | Sekundärer Text (Typ, Datum) |
| `isActive` | `boolean` | no | `false` | Ausgewählt/aktiv |
| `onClick` | `() => void` | yes | — | Klick-Callback |
| `onContextMenu` | `((e: React.MouseEvent) => void) \| null` | no | `null` | Rechtsklick öffnet ContextMenu |
| `isDraggable` | `boolean` | no | `false` | Drag & Drop aktiviert |
| `dragHandleRef` | `React.RefObject` | no | — | Ref für DragHandle |
| `badges` | `React.ReactNode \| null` | no | `null` | Badges/Icons rechts (Status, Zähler) |
| `variant` | `"default" \| "compact" \| "with-thumbnail"` | no | `"default"` | Visueller Stil |

---

## Rules

- `isActive` und hover sind verschiedene Stile — nicht vermischen
- Klick öffnet DetailPanel — kein direktes Navigieren ohne explizite Anforderung
- Rechtsklick öffnet ContextMenu wenn `onContextMenu` übergeben
- Drag & Drop nur wenn `isDraggable = true` — dann muss `dragHandleRef` übergeben werden

---

## Accessibility

- Fokussierbar via Tab
- `aria-selected` spiegelt `isActive`
- `role="option"` innerhalb einer `role="listbox"` — oder `role="listitem"` in `role="list"`
- Keyboard: Enter/Space löst `onClick` aus

---

## Code Pattern

```tsx
<EntityListItem
  id={scene.id}
  title={scene.title}
  subtitle={t("scene.type." + scene.type)}
  isActive={selectedId === scene.id}
  onClick={() => setSelectedId(scene.id)}
  onContextMenu={(e) => openContextMenu(e, scene.id)}
  isDraggable
/>
```

---

## Do / Don't

❌ EntityListItem ohne onClick-Handler
✅ Immer onClick übergeben — auch wenn es nur zur Selection führt

❌ Inline-Bearbeitung direkt im Listeneintrag
✅ DetailPanel oder Modal für Bearbeitung öffnen

---

## Missing Information Protocol

```tsx
// TODO(design): Hover und Active Highlight-Farben als Tokens — Issue #TODO
// TODO(design): Thumbnail-Größe und -Format — Issue #TODO
// TODO(ux): Drag & Drop Sortierung — Bibliothek noch nicht entschieden — Issue #TODO
```

---

## Related

- `section-header.md` — Gruppiert Listeneinträge
- `detail-panel.md` — Öffnet sich bei Klick auf EntityListItem
- `context-menu.md` — Bei Rechtsklick
- `drag-handle.md` — Handle für Drag & Drop
- `count-badge.md` — Badge-Variante für Zähler
