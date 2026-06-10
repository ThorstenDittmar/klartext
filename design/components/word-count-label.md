# WordCountLabel

## Purpose

Kompakte Wort-Anzahl-Anzeige mit optionalem Ziel-Wert und Fortschritts-Indikator — z.B. „1.240 / 2.000 W". Wird in Kapitel-Headern, BottomBar und Stats-Bereichen verwendet.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `count-only` | Nur aktuelle Anzahl | „1.240 W" |
| `with-target` | Aktuell + Ziel | „1.240 / 2.000 W" |
| `percentage` | Als Prozentwert | „62 %" |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | Unter Ziel | Neutral |
| `on-target` | Ziel erreicht (≥ 100%) | Grüne Farbe oder Checkmark |
| `loading` | Zahl wird berechnet | Skeleton-Balken |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `count` | `number` | yes | — | Aktuelle Wortzahl |
| `target` | `number \| null` | no | `null` | Ziel-Wort-Anzahl — null = kein Ziel |
| `variant` | `"count-only" \| "with-target" \| "percentage"` | no | `"count-only"` | Anzeigeformat |
| `size` | `"sm" \| "md"` | no | `"md"` | Schrift-Größe |

---

## Rules

- Formatierung via `toLocaleString()` — nie rohes `number.toString()`
- Einheit „W" (Wörter) immer anzeigen
- `percentage` Variante nur wenn `target` gesetzt ist

---

## Accessibility

- Rein textueller Inhalt — kein ARIA nötig
- Screen Reader liest die Zahlen korrekt wenn Einheit im Text enthalten

---

## Code Pattern

```tsx
// In BottomBar
<WordCountLabel count={currentWordCount} target={chapterTarget} variant="with-target" />

// In ChapterContainer
<WordCountLabel count={chapterWordCount} variant="count-only" size="sm" />
```

---

## Do / Don't

❌ Rohzahl ohne Formatierung anzeigen
✅ `toLocaleString()` für lesbare Zahlen

❌ `percentage` ohne `target`
✅ Variante nur setzen wenn Daten vorhanden

---

## Missing Information Protocol

```tsx
// TODO(design): On-target Farbe und Icon — Issue #TODO
// TODO(i18n): Einheit „W" lokalisierbar? — Issue #TODO
// TODO(design): Schrift-Größen sm/md als Token — Issue #TODO
```

---

## Related

- `bottom-bar.md` — Zeigt WordCountLabel global für das Dokument
- `chapter-container.md` — Zeigt WordCountLabel pro Kapitel
- `stat-card.md` — Alternative für Übersichts-Dashboard
