# CountBadge

## Purpose

Kleine numerische Anzeige neben einem Label oder Icon — zeigt Anzahl von Unterelementen (z.B. Szenen in einem Kapitel, Kommentare, offene Items). Rein informativ, nicht interaktiv.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `inline` | Neben einem Text-Label | Kleines Pill direkt hinter dem Text |
| `dot` | Auf einem Icon (z.B. Notifications) | Roter Punkt, kein Zahl-Text (für hohe Zahlen) |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `zero` | Zähler = 0 | Ausgeblendet oder gedimmt — je nach Kontext |
| `max` | Zähler > 99 | Zeigt „99+" statt exakter Zahl |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `count` | `number` | yes | — | Anzuzeigender Zähler |
| `max` | `number` | no | `99` | Obergrenze — höhere Werte zeigen „{max}+" |
| `variant` | `"inline" \| "dot"` | no | `"inline"` | Visueller Stil |
| `hideWhenZero` | `boolean` | no | `true` | Badge ausblenden wenn count = 0 |

---

## Rules

- CountBadge zeigt nur Zahlen — kein Text
- Null-Wert standardmäßig ausgeblendet (Override via `hideWhenZero={false}`)
- `dot`-Variante ignoriert `count` und `max` — zeigt nur Punkt
- Keine Klick-Interaktion

---

## Accessibility

- `aria-label` beschreibt den Zähler: `aria-label={`${count} Szenen`}`
- `dot`-Variante: `aria-label="Neue Einträge vorhanden"`

---

## Code Pattern

```tsx
// Neben einem SectionHeader-Titel
<span>{t("scenes.title")}</span>
<CountBadge count={sceneCount} />

// Auf einem Icon-Button
<IconButton icon={<CommentIcon />}>
  <CountBadge count={commentCount} variant="dot" />
</IconButton>
```

---

## Do / Don't

❌ CountBadge für Text-Labels verwenden
✅ Nur für numerische Zähler

❌ `count={0}` anzeigen wenn es keinen sinnvollen Kontext gibt
✅ `hideWhenZero` default lassen

---

## Missing Information Protocol

```tsx
// TODO(design): Badge-Farbe als Token — Issue #TODO
// TODO(design): Schrift-Größe und -Gewicht im Badge — Issue #TODO
```

---

## Related

- `badge.md` — Text-Badge für Kategorien/Status
- `section-header.md` — Zeigt CountBadge neben dem Abschnittstitel
