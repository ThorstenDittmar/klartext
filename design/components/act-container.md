# ActContainer

## Purpose

Struktureller Container für einen Akt im Szenenplan — gruppiert SceneCards, zeigt Akt-Titel und Szenen-Anzahl. Akzeptiert Drops für Drag & Drop-Sortierung zwischen Akten.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Horizontale Akt-Spalte | Akt-Header oben, SceneCards darunter |
| `collapsed` | Akt ist zugeklappt | Nur Akt-Header sichtbar, Pfeil nach rechts |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `expanded` | Standard | SceneCards sichtbar |
| `collapsed` | Header-Klick | Cards ausgeblendet |
| `drag-over` | Szene wird über Akt gezogen | Drop-Zone hervorgehoben |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Akt-ID |
| `title` | `string` | yes | — | Akt-Name (z.B. „Akt 1", „Exposition") |
| `sceneCount` | `number` | yes | — | Anzahl Szenen im Akt |
| `isCollapsed` | `boolean` | no | `false` | Eingeklappt |
| `onToggle` | `() => void` | yes | — | Collapse/Expand |
| `children` | `React.ReactNode` | yes | — | SceneCards |
| `isDragTarget` | `boolean` | no | `false` | Akzeptiert Drops |

---

## Rules

- ActContainer ist kein scrollender Container — der übergeordnete Plan-Canvas scrollt
- Akt-Titel ist editable via Doppelklick oder Edit-Icon (Inline-Edit oder Modal — noch offen)
- Kein Löschen über ActContainer direkt — via ContextMenu oder Settings
- Drag & Drop zwischen Akten ändert die Szenen-Reihenfolge global

---

## Accessibility

- `aria-label` beschreibt den Akt
- Collapse-Button: `aria-expanded` spiegelt Zustand
- Drop-Zone: `aria-dropeffect="move"` wenn `isDragTarget`

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ Akt-Logik (Reihenfolge, Zugehörigkeit) im ActContainer
✅ Container ist nur Darstellung — Logik im Service/Hook

❌ ActContainer ohne SceneCards rendern wenn Akt Szenen hat
✅ Immer alle Szenen des Akts als children übergeben

---

## Missing Information Protocol

```tsx
// TODO(design): Akt-Container Breite — fest oder flexibel? — Issue #TODO
// TODO(ux): Inline-Edit des Akt-Titels vs. Modal — noch nicht entschieden — Issue #TODO
// TODO(ux): Drag & Drop Bibliothek (dnd-kit, react-beautiful-dnd) — noch nicht entschieden — Issue #TODO
```

---

## Related

- `scene-card.md` — Inhalt des ActContainers
- `chapter-container.md` — Analoges Konzept für Kapitel
- `section-header.md` — Strukturell ähnlich (collapse + count), aber für Listen in der Sidebar
