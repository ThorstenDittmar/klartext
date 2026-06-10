# SectionHeader

## Purpose

Kollabierbare Abschnittsüberschrift mit Titel, Eintrags-Zähler und inline Actions (z.B. „+ Hinzufügen"). Strukturiert Listen in der Sidebar oder im Hauptbereich.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `collapsible` | Abschnitt kann geschlossen werden | Collapse-Arrow, Titel, Zähler, Actions |
| `static` | Abschnitt ist immer sichtbar | Nur Titel + optionaler Zähler, kein Arrow |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `expanded` | Standard | Arrow zeigt nach unten, Inhalt sichtbar |
| `collapsed` | Arrow-Klick oder Header-Klick | Arrow zeigt nach rechts, Inhalt ausgeblendet |
| `hover` | Mouse over Header | TODO(design): nicht spezifiziert — Issue #TODO |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | `string` | yes | — | Abschnittstitel (via t()-Key übergeben) |
| `count` | `number \| null` | no | `null` | Anzahl Einträge — `null` = nicht anzeigen |
| `isCollapsible` | `boolean` | no | `true` | Ob Abschnitt klappbar ist |
| `isCollapsed` | `boolean` | no | `false` | Aktueller Zustand |
| `onToggle` | `() => void` | no | — | Callback bei Collapse/Expand |
| `onAdd` | `(() => void) \| null` | no | `null` | „+" Aktion — null = nicht anzeigen |

---

## Rules

- Titel immer via `t('key')` — kein Hardcoding
- Zähler zeigt die Anzahl sichtbarer (nicht gefilterter) Einträge
- Actions nur anzeigen wenn der User die Berechtigung hat

---

## Accessibility

- Collapse-Trigger: `aria-expanded` spiegelt aktuellen Zustand
- Collapse-Trigger: `aria-controls` zeigt auf die ID des Inhalts-Containers
- Keyboard: Enter/Space togglet den Collapse-Zustand

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ Komplexe Aktionen direkt im SectionHeader ausführen
✅ Header-Actions nur für schnelle Einstieg-Aktionen (Hinzufügen)

---

## Missing Information Protocol

```tsx
// TODO(design): Hover-Zustand nicht spezifiziert — Issue #TODO
// TODO(design): Collapsed-Arrow-Icon und Animation — Issue #TODO
```

---

## Related

- `sidebar.md` — SectionHeader wird primär in der Sidebar verwendet
- `entity-list-item.md` — Inhalt unterhalb des SectionHeaders
- `count-badge.md` — Eintrags-Zähler rechts vom Titel
