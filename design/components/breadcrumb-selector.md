# BreadcrumbSelector

## Purpose

Erweiterung des letzten Breadcrumb-Segments als Dropdown — ermöglicht schnelles Wechseln zwischen Einträgen der gleichen Ebene (z.B. andere Szene im selben Kapitel) ohne zurück zu navigieren.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard-Dropdown | Aktueller Eintrag als Text + Pfeil, Dropdown öffnet unter dem Segment |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `closed` | Standard | Text + Dropdown-Pfeil |
| `open` | Klick auf Segment | Dropdown-Liste sichtbar |
| `loading` | Optionen werden geladen | Skeleton in der Dropdown-Liste |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `currentLabel` | `string` | yes | — | Aktuell angezeigter Name |
| `options` | `Array<{ value: string; label: string }>` | yes | — | Verfügbare Optionen |
| `onSelect` | `(value: string) => void` | yes | — | Callback bei Auswahl |
| `isLoading` | `boolean` | no | `false` | Optionen werden noch geladen |

---

## Rules

- BreadcrumbSelector ersetzt das letzte Breadcrumb-Segment
- Aktuelle Auswahl erscheint nicht in der Dropdown-Liste (oder ist deaktiviert markiert)
- Maximale Dropdown-Höhe begrenzt mit Scroll
- Dropdown schließt bei Auswahl, Escape oder Klick außerhalb

---

## Accessibility

- `role="combobox"` oder `aria-haspopup="listbox"` auf dem Trigger
- Dropdown: `role="listbox"` + `aria-label`
- Keyboard: Arrow Keys navigieren, Enter wählt aus, Escape schließt

---

## Code Pattern

```tsx
<BreadcrumbSelector
  currentLabel={currentScene.title}
  options={siblingScenes.map(s => ({ value: s.id, label: s.title }))}
  onSelect={(id) => navigate(`/scene/${id}`)}
/>
```

---

## Do / Don't

❌ BreadcrumbSelector für nicht-hierarchische Navigation
✅ Nur für gleichwertige Einträge auf derselben Hierarchie-Ebene

---

## Missing Information Protocol

```tsx
// TODO(design): Dropdown-Pfeil Icon und Größe — Issue #TODO
// TODO(design): Maximale Dropdown-Höhe — Issue #TODO
// TODO(ux): Suche/Filter im Dropdown bei vielen Optionen — Issue #TODO
```

---

## Related

- `breadcrumb.md` — Übergeordnete Breadcrumb-Komponente
- `context-menu.md` — Ähnliche Dropdown-Mechanik, anderer Kontext
