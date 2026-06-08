# Sidebar

## Purpose

Kollabierbare linke Panel mit eigenem Tab-System (Codex/Snippets/Chats), Suchfeld und Eintrags-Listen. Dient als Kontext-Navigator neben dem Hauptinhalt.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `expanded` | Standard | Volle Breite, Inhalt sichtbar |
| `collapsed` | Platzsparend | Auf Icon-Breite reduziert, kein Text |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `expanded` | Standard oder nach Toggle | Breite ~280px, Inhalt sichtbar |
| `collapsed` | Toggle-Button geklickt | Minimale Breite, nur Icons |
| `tab-codex` | Codex-Tab aktiv | Codex-Inhalt sichtbar |
| `tab-snippets` | Snippets-Tab aktiv | Snippets-Inhalt sichtbar |
| `tab-chats` | Chats-Tab aktiv | Chats-Inhalt sichtbar |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `isCollapsed` | `boolean` | no | `false` | Kollabiert/expanded state |
| `onToggle` | `() => void` | no | — | Callback bei Collapse/Expand |
| `activeTab` | `"codex" \| "snippets" \| "chats"` | no | `"codex"` | Aktiver innerer Tab |
| `children` | `React.ReactNode` | yes | — | Inhalt des aktiven Tabs |

---

## Rules

- Zustand (collapsed/expanded) wird im App-State gehalten, nicht lokal
- Collapsed-Zustand persistiert über Navigation hinweg
- Im collapsed-Zustand sind Tooltips für Icons Pflicht (Accessibility)

---

## Accessibility

- `nav` oder `aside` als HTML-Element
- Toggle-Button: `aria-expanded` spiegelt aktuellen Zustand
- Innere Tabs: `role="tablist"` + `role="tab"` + `aria-selected`
- Im collapsed-Zustand: Icon-Buttons mit `aria-label`

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ Business-Logik in die Sidebar einbauen
✅ Sidebar ist rein navigatorisch — sie zeigt Einträge an, triggert keine Aktionen außer Navigation

---

## Missing Information Protocol

```tsx
// TODO(design): Breite expanded/collapsed als Token — Issue #TODO
// TODO(design): Transition-Dauer beim Collapse — Issue #TODO
```

---

## Related

- `section-header.md` — Abschnittsköpfe innerhalb der Sidebar
- `entity-list-item.md` — einzelne Einträge in der Sidebar-Liste
- `search-input.md` — Suchfeld am Kopf der Sidebar
- `app-bar.md` — Toggle-Button für Sidebar sitzt in der AppBar
