# AppBar

## Purpose

Oberste Leiste der App — enthält Projekt-Titel, globale Navigation (Plan/Write/Chat/Review), Settings-Zugang und Collapse-Controls für die Sidebar. Existiert einmal pro Seite.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `novel` | Innerhalb eines Projekts | Zeigt Projekttitel + Autor, alle vier Mode-Tabs |
| `library` | Auf der Projektliste | Nur Logo + Top-Level-Navigation (Novels, Series, Prompts) |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `tab-active` | Aktiver Mode-Tab | Tab hat gefüllten dunklen Background, weißer Text |
| `tab-hover` | Mouse over Tab | TODO(design): nicht spezifiziert — Issue #TODO |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `projectTitle` | `string` | no | — | Name des aktiven Projekts |
| `projectSubtitle` | `string` | no | — | Autor o.ä. Untertitel |
| `activeTab` | `"plan" \| "write" \| "chat" \| "review"` | no | — | Aktuell aktiver Mode-Tab |
| `onTabChange` | `(tab: string) => void` | no | — | Callback bei Tab-Wechsel |
| `onSettingsClick` | `() => void` | no | — | Öffnet Settings |
| `onToggleSidebar` | `() => void` | no | — | Sidebar ein-/ausblenden |

---

## Rules

- Tab-Label immer via `t('key')` — kein Hardcoding
- Nur einer der vier Mode-Tabs ist gleichzeitig aktiv
- AppBar ist nie scrollbar — bleibt sticky am oberen Rand

---

## Accessibility

- Tabs: `role="tablist"` mit `role="tab"` pro Item
- Aktiver Tab: `aria-selected="true"`
- Settings- und Collapse-Buttons: `aria-label` erforderlich (Icon-only)
- Keyboard: Tab-Navigation zwischen den Tabs

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
// Referenz-Implementierung: TODO(backend): warten auf Screen-Implementierung
```

---

## Do / Don't

❌ Weitere Aktionen direkt in die AppBar einbauen
✅ Sekundäre Actions in SubTabBar oder Kontextmenüs auslagern

---

## Missing Information Protocol

```tsx
// TODO(design): hover states für Mode-Tabs — Issue #TODO
// TODO(design): AppBar-Höhe als Token definieren — Issue #TODO
// TODO(i18n): Tab-Labels (plan, write, chat, review) brauchen t()-Keys — Issue #TODO
```

---

## Related

- `sub-tab-bar.md` — sekundäre Tabs (Grid/Matrix/Outline) im Plan-Mode
- `sidebar.md` — wird über Toggle-Button in AppBar ein-/ausgeklappt
- `design/tokens/colors.json` — active-Tab-Background
