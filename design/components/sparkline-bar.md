# SparklineBar

## Purpose

Kompakter Inline-Balken-Chart ohne Achsen und Labels — zeigt den zeitlichen Verlauf einer Kennzahl in einem kleinen Raum (z.B. innerhalb einer StatCard). Rein informativ, nicht interaktiv.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `bar` | Diskrete Perioden | Kleine Balken nebeneinander |
| `line` | Kontinuierlicher Verlauf | Dünne Linie ohne Achsen |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | Daten geladen | Chart vollständig |
| `loading` | Daten werden geladen | Skeleton-Balken |
| `empty` | Keine Daten | Leere Fläche |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `data` | `number[]` | yes | — | Datenpunkte (Reihenfolge = zeitlich aufsteigend) |
| `variant` | `"bar" \| "line"` | no | `"bar"` | Chart-Stil |
| `colorKey` | `string \| null` | no | `null` | Token-Key für Chart-Farbe |
| `height` | `number` | no | `32` | Höhe in Pixeln |

---

## Rules

- Keine Achsen, keine Labels, keine Tooltips — rein visuell
- Breite passt sich dem Container an (`width: 100%`)
- Keine Interaktion — für interaktive Charts: `chart-card.md`
- Maximale Datenpunkte: 30 — mehr wird performanz-kritisch

---

## Accessibility

- `role="img"` mit `aria-label` der Kernaussage
- Kein `<canvas>` ohne Fallback-Text

---

## Code Pattern

```tsx
<StatCard
  label={t("stats.words_per_day")}
  value="1.240"
  sparklineData={lastThirtyDaysWordCounts}
/>

// intern im StatCard:
<SparklineBar data={sparklineData} height={24} />
```

---

## Do / Don't

❌ SparklineBar für interaktive Datenexploration
✅ ChartCard für interaktive Charts

❌ Mehr als 30 Datenpunkte ohne Sampling/Aggregation
✅ Daten vor dem Übergeben aggregieren

---

## Missing Information Protocol

```tsx
// TODO(tech): SVG vs. Canvas — Issue #TODO
// TODO(design): Standard-Balken-Farbe als Token — Issue #TODO
// TODO(design): Balken-Abstand und -Breite — Issue #TODO
```

---

## Related

- `stat-card.md` — Primärer Verwendungskontext
- `chart-card.md` — Vollständige interaktive Datenvisualisierung
