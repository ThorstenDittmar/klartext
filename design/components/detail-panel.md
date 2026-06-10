# DetailPanel

## Purpose

Slide-over Panel das sich über den Hauptinhalt legt wenn ein Listen-Eintrag ausgewählt wird — zeigt Detail-Informationen mit eigenem Tab-System. Nicht-blockierend: Hauptinhalt bleibt im Hintergrund sichtbar.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `right` | Standard | Öffnet von rechts, Breite ~400px |
| `left` | Sidebar-nahe Details | Öffnet von links über der Sidebar |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `open` | Listen-Eintrag ausgewählt | Panel gleitet ein, Main-Content verschiebt sich oder überlagert |
| `closed` | Schließen oder Eintrag deselektiert | Panel gleitet aus |
| `loading` | Detail-Daten werden geladen | Skeleton-Loader im Inhalt |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `isOpen` | `boolean` | yes | — | Sichtbarkeit des Panels |
| `onClose` | `() => void` | yes | — | Callback beim Schließen |
| `title` | `string` | yes | — | Heading im Panel-Header |
| `subtitle` | `string \| null` | no | `null` | Optionaler Untertitel (z.B. Entitäts-Typ) |
| `children` | `React.ReactNode` | yes | — | Panel-Inhalt |
| `tabs` | `Array<{ id: string; label: string }>` | no | `[]` | Optionale Tab-Navigation im Panel |
| `activeTab` | `string` | no | — | Aktiver Tab |
| `onTabChange` | `(id: string) => void` | no | — | Callback bei Tab-Wechsel |

---

## Rules

- Kein Focus Trap — Hauptinhalt bleibt nutzbar
- Escape schließt das Panel
- Panel öffnet nicht über einem Modal
- Scroll im Panel ist unabhängig vom Hauptinhalt-Scroll

---

## Accessibility

- `role="complementary"` oder `aside` als HTML-Element
- `aria-label` beschreibt den Panel-Inhalt
- Schließen-Button mit `aria-label="Schließen"`
- Beim Öffnen: Fokus auf ersten interaktiven Element oder Panel-Heading

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ DetailPanel für Aktionen verwenden die eine Entscheidung erzwingen
✅ Modal für blockierende Entscheidungen verwenden

❌ Panel mit unbegrenzter Breite
✅ Feste maximale Breite damit Hauptinhalt sichtbar bleibt

---

## Missing Information Protocol

```tsx
// TODO(design): Panel-Breite als Token — Issue #TODO
// TODO(design): Slide-Animation Dauer und Easing — Issue #TODO
// TODO(design): Verhältnis zum Hauptinhalt (overlay vs. push) — Issue #TODO
```

---

## Related

- `modal.md` — blockierendes Overlay für explizite Entscheidungen
- `entity-list-item.md` — öffnet das DetailPanel bei Klick
- `avatar.md` — oft im Panel-Header für Entitäten mit Bild
