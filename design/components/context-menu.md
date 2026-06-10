# ContextMenu

## Purpose

Kontextuelles Dropdown-Menü das auf Rechtsklick oder Icon-Button öffnet — zeigt Aktionen für ein spezifisches Element (Umbenennen, Duplizieren, Löschen). Schwebend über dem UI, positioniert sich am Cursor/Trigger.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard-Aktionsliste | Vertikale Liste mit Text-Items |
| `with-icons` | Aktionen mit Icons | Icons links vor jedem Item |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `open` | Rechtsklick oder Icon-Button-Klick | Menü erscheint am Cursor |
| `closed` | Auswahl, Escape oder Klick außerhalb | Menü verschwindet |
| `item-hover` | Mouse über Item | Item-Highlight |
| `item-disabled` | Item nicht verfügbar | Gedimmt, nicht klickbar |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `isOpen` | `boolean` | yes | — | Sichtbarkeit |
| `onClose` | `() => void` | yes | — | Schließen-Callback |
| `position` | `{ x: number; y: number }` | yes | — | Cursor-Position |
| `items` | `ContextMenuItem[]` | yes | — | Menü-Items |

---

## Types

```tsx
type ContextMenuItem =
  | {
      type: "action"
      label: string
      icon?: React.ReactNode
      onClick: () => void
      isDestructive?: boolean
      isDisabled?: boolean
    }
  | { type: "separator" }
```

---

## Rules

- Destruktive Aktionen (Löschen) immer am Ende, visuell hervorgehoben
- Destruktive Aktionen öffnen Bestätigungs-Modal — kein direktes Löschen aus dem ContextMenu
- Menü positioniert sich so dass es nicht aus dem Viewport fällt (Flip-Logik)
- Maximal 8 Items — mehr via Untermenü oder andere Lösung

---

## Accessibility

- `role="menu"` auf dem Container
- Items: `role="menuitem"` oder `role="menuitemcheckbox"`
- Keyboard: Arrow Keys navigieren, Enter aktiviert, Escape schließt
- Fokus geht beim Öffnen auf das erste Item

---

## Code Pattern

```tsx
const [menuState, setMenuState] = useState<{ x: number; y: number } | null>(null)

<EntityListItem
  onContextMenu={(e) => {
    e.preventDefault()
    setMenuState({ x: e.clientX, y: e.clientY })
  }}
/>

{menuState && (
  <ContextMenu
    isOpen
    onClose={() => setMenuState(null)}
    position={menuState}
    items={[
      { type: "action", label: t("action.rename"), onClick: handleRename },
      { type: "separator" },
      { type: "action", label: t("action.delete"), onClick: () => setConfirmDelete(true), isDestructive: true },
    ]}
  />
)}
```

---

## Do / Don't

❌ Direkte Lösch-Aktion im ContextMenu ohne Bestätigung
✅ Bestätigungs-Modal öffnen für destruktive Aktionen

❌ ContextMenu ohne Flip-Logik (wird abgeschnitten am Rand)
✅ Position prüfen und bei Bedarf nach oben/links flippen

---

## Missing Information Protocol

```tsx
// TODO(tech): Positionierungs-Bibliothek (Floating UI / Popper) — Issue #TODO
// TODO(design): Schatten und Border-Radius des Menüs — Issue #TODO
// TODO(design): Item-Höhe und Padding — Issue #TODO
```

---

## Related

- `modal.md` — Bestätigungs-Dialog für destruktive Aktionen
- `entity-list-item.md` — Öffnet ContextMenu via Rechtsklick
- `scene-card.md` — Öffnet ContextMenu via Rechtsklick
