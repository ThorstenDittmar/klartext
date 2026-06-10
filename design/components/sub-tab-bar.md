# SubTabBar

## Purpose

Sekundäre Tab-Leiste unterhalb der AppBar — schaltet zwischen Ansichtsvarianten desselben Mode um (z.B. Grid/Matrix/Outline im Plan-Mode). Erscheint nur wenn der aktive Mode mehrere Ansichten hat.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `plan-views` | Plan-Mode aktiv | Grid, Matrix, Outline + FILTER-Suchfeld + View-Button |
| `minimal` | Mode mit wenigen Sub-Views | Nur Tab-Buttons ohne Filter |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `tab-active` | Aktive Sub-View | Tab erhält gefüllten Background |
| `tab-hover` | Mouse over | TODO(design): nicht spezifiziert — Issue #TODO |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tabs` | `Array<{ id: string; label: string; icon?: string }>` | yes | — | Tab-Definitionen |
| `activeTab` | `string` | yes | — | ID des aktiven Tabs |
| `onTabChange` | `(id: string) => void` | yes | — | Callback bei Tab-Wechsel |
| `filterValue` | `string` | no | — | Wert des Filter-Suchfelds (optional) |
| `onFilterChange` | `(value: string) => void` | no | — | Callback Filter-Änderung |
| `onViewSettings` | `() => void` | no | — | Öffnet View-Einstellungen |

---

## Rules

- Nur in Kombination mit AppBar verwenden — nie standalone
- Filter-Suchfeld nur einblenden wenn der aktive Mode es unterstützt
- Tab-Labels immer via `t('key')`

---

## Accessibility

- `role="tablist"` auf dem Container
- Jeder Tab: `role="tab"` + `aria-selected`
- Keyboard: Arrow-Keys navigieren zwischen Tabs (Left/Right)

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ SubTabBar für komplett verschiedene Inhalte verwenden
✅ SubTabBar nur für verschiedene Ansichten desselben Inhalts

---

## Missing Information Protocol

```tsx
// TODO(design): Tab-active-Background-Farbe als Token — Issue #TODO
// TODO(i18n): Tab-Labels als t()-Keys — Issue #TODO
```

---

## Related

- `app-bar.md` — primäre Navigation, sitzt direkt darüber
- `search-input.md` — Filter-Suchfeld in der SubTabBar
- `toggle-button-group.md` — ähnliches Konzept für Ansichtswechsel
