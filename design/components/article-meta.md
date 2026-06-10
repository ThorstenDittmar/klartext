# ArticleMeta

## Purpose

Kompakte Metadaten-Zeile unter einem Artikel- oder Dokument-Titel — zeigt Autor, Datum, Lesedauer oder Kategorie in einer strukturierten, optisch dezenten Zeile. Rein informativ, nicht interaktiv.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Allgemeine Metadaten | Kommaseparierte oder „•"-separierte Felder |
| `compact` | Enge Räume (Sidebar, Liste) | Kleinere Schrift, weniger Felder |

---

## States

Keine interaktiven States.

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `author` | `string \| null` | no | `null` | Autorenname |
| `publishedAt` | `string \| null` | no | `null` | Datum (ISO 8601 — relative Anzeige) |
| `readingTime` | `number \| null` | no | `null` | Lesedauer in Minuten |
| `category` | `string \| null` | no | `null` | Kategorie-Label |
| `variant` | `"default" \| "compact"` | no | `"default"` | Visueller Stil |

---

## Rules

- Nur Felder anzeigen die nicht null sind
- `publishedAt` wird relativ angezeigt (z.B. „vor 3 Tagen") — Formatierung im Hook
- Trennzeichen zwischen Feldern: „•" (Unicode U+2022)
- Kein Wrapper wenn alle Felder null — nichts rendern

---

## Accessibility

- `<time dateTime={publishedAt}>` für Datumsangaben
- Rein textueller Inhalt — kein ARIA nötig

---

## Code Pattern

```tsx
<ArticleMeta
  author={article.authorName}
  publishedAt={article.publishedAt}
  readingTime={article.readingTimeMinutes}
  category={t(`article.category.${article.category}`)}
/>
```

---

## Do / Don't

❌ Mehr als 4 Metadaten-Felder in einer Zeile
✅ Wichtigste Felder priorisieren, Rest weglassen

❌ Datum als rohen ISO-String anzeigen
✅ Immer relative Anzeige via Formatter-Util

---

## Missing Information Protocol

```tsx
// TODO(design): Schriftfarbe und -größe für Meta-Informationen — Issue #TODO
// TODO(design): Trennzeichen-Stil — Issue #TODO
// TODO(ux): Welche Dokument-Typen in klartext haben Metadaten? — Issue #TODO
```

---

## Related

- `novel-card.md` — Metadaten auf Projekt-Karte (ähnliches Konzept)
- `entity-list-item.md` — Subtitle im Listeneintrag als ähnliche Info
