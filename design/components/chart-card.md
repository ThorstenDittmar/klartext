# ChartCard

## Purpose

Umrandete Karte für Datenvisualisierungen — umschließt Charts (Balken, Linien, Fläche) mit Titel, optionaler Legende und Zeitraum-Selektion. Die eigentliche Chart-Bibliothek ist noch nicht festgelegt.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `bar` | Vergleich über Zeitperioden | Balken-Chart mit X/Y-Achsen |
| `line` | Zeitlicher Verlauf (Trend) | Linien-Chart |
| `area` | Kumulative Entwicklung | Flächen-Chart mit Fill |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | Daten geladen | Chart vollständig |
| `loading` | Daten werden geladen | Skeleton-Placeholder in Karten-Höhe |
| `empty` | Keine Daten für Zeitraum | EmptyState im Karten-Inhalt |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | `string` | yes | — | Karten-Überschrift (via t()-Key) |
| `data` | `ChartDataPoint[]` | yes | — | Chart-Datenpunkte |
| `variant` | `"bar" \| "line" \| "area"` | no | `"bar"` | Chart-Typ |
| `period` | `"week" \| "month" \| "year"` | no | `"month"` | Angezeigter Zeitraum |
| `onPeriodChange` | `((period: string) => void) \| null` | no | `null` | Zeitraum-Selektion — null = kein Selektor |
| `isLoading` | `boolean` | no | `false` | Loading-State |

---

## Rules

- ChartCard kapselt nur Layout + Header — Chart-Rendering liegt in der jeweiligen Chart-Implementierung
- Achsenbeschriftungen immer via `t('key')`
- Farben für Serien aus Design-Token-Palette, nie hardcoded
- Interaktive Tooltips optional — aber wenn vorhanden: Tastatur-zugänglich

---

## Accessibility

- `role="img"` auf dem Chart-Container mit `aria-label` der Kernaussage
- Daten-Tabelle als visuell versteckter Fallback für Screen Reader
- Keine reinen Farb-Kodierungen ohne zweiten Kanal (Muster, Label)

---

## Code Pattern

```tsx
<ChartCard
  title={t("stats.words_per_day.title")}
  data={wordsPerDayData}
  variant="bar"
  period={selectedPeriod}
  onPeriodChange={setSelectedPeriod}
/>
```

---

## Do / Don't

❌ Chart-Bibliothek direkt im ChartCard hardcoden
✅ Chart-Rendering in eigener Komponente kapseln, ChartCard liefert nur den Wrapper

❌ Statische Farb-Hexcodes für Chart-Serien
✅ Design-Token-Keys für alle Chart-Farben

---

## Missing Information Protocol

```tsx
// TODO(tech): Chart-Bibliothek noch nicht entschieden (Recharts, Chart.js, Victory) — Issue #TODO
// TODO(design): Chart-Farb-Token-Palette — Issue #TODO
// TODO(design): Chart-Karten-Höhe — Issue #TODO
// TODO(a11y): Daten-Tabellen-Fallback Implementierung — Issue #TODO
```

---

## Related

- `stat-card.md` — Einzelne Kennzahl ohne Chart
- `sparkline-bar.md` — Kompakte Inline-Visualisierung in StatCard
