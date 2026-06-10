# StatCard

## Purpose

Kompakte Karte für eine einzelne Kennzahl mit Label und optionalem Trend-Indikator — z.B. Wörter gesamt, Szenen-Anzahl, Fortschritt. Immer read-only, nie interaktiv.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Einfache Zahl + Label | Zahl prominent, Label darunter |
| `with-trend` | Zahl + Trend-Richtung | Zusätzlicher Pfeil-Indikator (▲/▼) mit Differenz |
| `with-sparkline` | Zeitlicher Verlauf | Zahl + Sparkline-Bar unterhalb |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `loading` | Daten werden geladen | Skeleton-Placeholder für Zahl |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `label` | `string` | yes | — | Bezeichnung der Kennzahl (via t()-Key) |
| `value` | `string \| number` | yes | — | Anzuzeigende Zahl oder Wert |
| `unit` | `string \| null` | no | `null` | Einheit rechts neben dem Wert (z.B. „W") |
| `trend` | `"up" \| "down" \| "neutral" \| null` | no | `null` | Trend-Richtung — null = kein Indikator |
| `trendValue` | `string \| null` | no | `null` | Absoluter oder relativer Trend-Wert |
| `sparklineData` | `number[] \| null` | no | `null` | Daten für Sparkline — null = keine Sparkline |

---

## Rules

- StatCard ist immer read-only — keine Klick-Interaktion
- Wert muss vorformatiert übergeben werden (keine interne Formatierung)
- Maximal 4 StatCards nebeneinander

---

## Accessibility

- `role="status"` wenn der Wert sich dynamisch ändern kann
- Kein interaktives Element — kein Fokus nötig

---

## Code Pattern

```tsx
<StatCard
  label={t("stats.word_count")}
  value={wordCount.toLocaleString()}
  trend="up"
  trendValue="+234"
/>
```

---

## Do / Don't

❌ StatCard für Eingaben oder navigierbare Elemente verwenden
✅ StatCard nur für reine Kennzahl-Darstellung

❌ Wert-Formatierung (Komma/Punkt) im Component hardcoden
✅ Vorformatiert übergeben via `toLocaleString()` oder Formatter-Util

---

## Missing Information Protocol

```tsx
// TODO(design): Trend-Farben (grün/rot) als Tokens — Issue #TODO
// TODO(design): Maximale und minimale Karten-Breite — Issue #TODO
// TODO(design): Loading-Skeleton Höhe/Breite — Issue #TODO
```

---

## Related

- `sparkline-bar.md` — Sparkline-Visualisierung in der with-sparkline Variante
- `chart-card.md` — Für komplexere Datenvisualisierungen
- `info-card.md` — Für systemische Hinweise statt Kennzahlen
