# Avatar

## Purpose

Kreisförmige Darstellung einer Person oder Figur — mit Foto, generiertem Initial-Bild oder Platzhalter-Icon. Wird in List-Items, Panel-Headern und Kommentar-Kontexten verwendet.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `image` | Foto vorhanden | Kreisförmiges Bild |
| `initials` | Kein Foto, Name bekannt | Farbiger Kreis mit Initial(en) |
| `placeholder` | Kein Name/Foto | Generisches Person-Icon |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `loading` | Bild wird geladen | Skeleton-Kreis |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | `string \| null` | no | `null` | Vollständiger Name — für Initials und alt-Text |
| `imageUrl` | `string \| null` | no | `null` | Foto-URL |
| `size` | `"xs" \| "sm" \| "md" \| "lg"` | no | `"md"` | Größe |
| `colorKey` | `string \| null` | no | `null` | Token-Key für Hintergrundfarbe (Initials-Variante) |

---

## Rules

- Wenn `imageUrl` gesetzt: Image-Variante — bei Ladefehler Fallback auf Initials
- Wenn kein `imageUrl` aber `name` gesetzt: Initials-Variante
- Wenn weder Image noch Name: Placeholder-Variante
- Initials: erste Buchstaben von Vor- und Nachname (max 2 Zeichen)
- Farbe der Initials-Variante deterministisch aus Name ableiten (gleicher Name = gleiche Farbe)

---

## Accessibility

- `<img>` mit `alt={name ?? ""}` bei Image-Variante
- Initials-Kreis: `aria-label={name}` + `role="img"`
- Placeholder: `aria-hidden="true"` wenn nur dekorativ

---

## Code Pattern

```tsx
<Avatar
  name={actor.name}
  imageUrl={actor.imageUrl}
  size="sm"
/>
```

---

## Do / Don't

❌ Avatar ohne alt/aria-label
✅ Immer `name` übergeben wenn bekannt

❌ Feste Farbe für Initials
✅ Farbe deterministisch aus Name ableiten oder per Token-Key übergeben

---

## Missing Information Protocol

```tsx
// TODO(design): Größen-Tokens xs/sm/md/lg in px — Issue #TODO
// TODO(design): Initials-Farbpalette (welche Token-Keys) — Issue #TODO
// TODO(tech): Deterministischen Farb-Hash-Algorithmus definieren — Issue #TODO
```

---

## Related

- `entity-list-item.md` — Avatar im Listeneintrag
- `detail-panel.md` — Avatar im Panel-Header
- `badge.md` — Statusanzeige kombinierbar mit Avatar
