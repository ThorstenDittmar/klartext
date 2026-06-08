# ToggleButtonGroup

## Purpose

Gruppe von eng zusammenstehenden Buttons bei denen immer genau einer (oder keiner) aktiv ist — für View-Umschaltung, Filter-Optionen oder Ansichts-Modi. Kein Dropdown, keine Mehrfachauswahl.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `single` | Genau eine Option muss gewählt sein | Aktiver Button ist hervorgehoben, kein Deselektieren |
| `nullable` | Keine Option = kein Filter aktiv | Aktiver Button kann durch Klick deselektiert werden |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `option-active` | Eine Option gewählt | Button mit aktivem Stil |
| `option-hover` | Mouse over nicht-aktiver Option | TODO(design): nicht spezifiziert — Issue #TODO |
| `disabled` | Gesamte Gruppe deaktiviert | Gedimmt, keine Interaktion |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `options` | `Array<{ value: string; label: string }>` | yes | — | Verfügbare Optionen |
| `value` | `string \| null` | yes | — | Aktuelle Auswahl — null = keine |
| `onChange` | `(value: string \| null) => void` | yes | — | Callback bei Auswahl |
| `variant` | `"single" \| "nullable"` | no | `"single"` | Auswahl-Verhalten |
| `disabled` | `boolean` | no | `false` | Gesamte Gruppe deaktiviert |

---

## Rules

- Bei `single`: value darf nie null sein — immer ein Default setzen
- Options-Labels immer via `t('key')` übergeben
- Maximal 5 Optionen — sonst Select oder Dropdown verwenden
- Keine Icons-only Buttons ohne tooltips

---

## Accessibility

- `role="group"` auf dem Container
- Jeder Button: `aria-pressed="true/false"` spiegelt Auswahl-Zustand
- Keyboard: Tab navigiert zur Gruppe, Arrow-Keys wechseln zwischen Optionen
- `aria-label` auf dem Container beschreibt den Gruppenkontext

---

## Code Pattern

```tsx
<ToggleButtonGroup
  options={[
    { value: "list", label: t("view.list") },
    { value: "grid", label: t("view.grid") },
  ]}
  value={viewMode}
  onChange={setViewMode}
/>
```

---

## Do / Don't

❌ ToggleButtonGroup für mehr als 5 Optionen
✅ Select/Dropdown ab 6+ Optionen

❌ Mehrfachauswahl über ToggleButtonGroup
✅ Checkboxen oder Chip-Group für Mehrfachauswahl

---

## Missing Information Protocol

```tsx
// TODO(design): Aktiv-Farbe als Token — Issue #TODO
// TODO(design): Hover-Zustand des inaktiven Buttons — Issue #TODO
// TODO(design): Border-Radius für einzelne vs. Gruppen-Buttons — Issue #TODO
```

---

## Related

- `sub-tab-bar.md` — Ähnlich, aber explizit für Tab-Navigation (Role: tablist)
- `badge.md` — Optionale Zähler-Badge auf einer Option
