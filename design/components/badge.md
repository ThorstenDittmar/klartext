# Badge

## Purpose

Kleines Label-Element für Kategorien, Status-Tags und Typ-Kennzeichnung — z.B. „Protagonist", „Konflikt", „Offen". Rein dekorativ/informativ, nicht interaktiv.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `status` | Prozess-Zustand | Farbiges Pill mit Text |
| `category` | Typ/Kategorie-Kennzeichnung | Neutral oder farbig |
| `outline` | Dezenter Hinweis | Nur Umriss, kein Fill |

---

## States

Keine interaktiven States — Badge ist read-only.

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `label` | `string` | yes | — | Anzuzeigender Text |
| `colorKey` | `string \| null` | no | `null` | Token-Key für Farbe |
| `variant` | `"status" \| "category" \| "outline"` | no | `"status"` | Visueller Stil |

---

## Rules

- Badge ist nicht klickbar — für klickbare Tags: separate ClickableBadge oder Button
- Label maximal ~20 Zeichen — längerer Text wird abgeschnitten mit Tooltip
- Farbe immer als Token-Key, nie als direkter Hex-Wert

---

## Accessibility

- Kein interaktives Element — kein `role` nötig wenn rein dekorativ
- Wenn Badge semantisch bedeutsam: `aria-label` auf dem Container
- Kein reines Farb-Encoding ohne Text-Label

---

## Code Pattern

```tsx
<Badge
  label={t("actor.type.protagonist")}
  colorKey="actor.type.protagonist"
  variant="category"
/>
```

---

## Do / Don't

❌ Badge interaktiv machen (onClick)
✅ Eigene ClickableBadge-Komponente wenn Klick-Verhalten nötig

❌ Langen Text in Badge
✅ Max ~20 Zeichen, Rest Tooltip

---

## Missing Information Protocol

```tsx
// TODO(design): Farb-Token-Palette für Badges — Issue #TODO
// TODO(design): Pill-Radius und Padding — Issue #TODO
// TODO(design): Maximale Label-Länge vor Truncation — Issue #TODO
```

---

## Related

- `count-badge.md` — Numerischer Zähler (andere Semantik)
- `matrix-column-pill.md` — Pill-Form aber für Tabellen-Header
- `entity-list-item.md` — Badge als Meta-Info im Listeneintrag
