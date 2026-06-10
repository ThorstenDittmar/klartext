# EmptyState

## Purpose

Zentrierte Nachricht wenn ein Bereich noch keine Inhalte hat — zeigt Titel, Erklärungstext und optional eine primäre Aktion. Kein leeres UI, kein Spinner ohne Ende.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Liste/Bereich ist leer | Zentrierter Titel + Subtitle, optionaler CTA-Button |
| `search-no-results` | Suche hat keine Treffer | Titel + Hinweis auf Suchbegriff, kein CTA |
| `error` | Laden fehlgeschlagen | Fehlermeldung + Retry-Button |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | `string` | yes | — | Hauptaussage (via t()-Key) |
| `subtitle` | `string \| null` | no | `null` | Erklärungstext (via t()-Key) |
| `actionLabel` | `string \| null` | no | `null` | Label für CTA-Button — null = kein Button |
| `onAction` | `(() => void) \| null` | no | `null` | Callback für CTA |
| `icon` | `React.ReactNode \| null` | no | `null` | Optionales illustratives Icon |

---

## Rules

- Immer anzeigen wenn eine Liste leer ist — niemals leere Container ohne Erklärung
- Titel beschreibt den Zustand (nicht die Aktion): „Keine Narrative vorhanden", nicht „Narrativ erstellen"
- Subtitle erklärt was der Nutzer tun kann
- Nur einen CTA-Button — kein zweiter Link daneben

---

## Accessibility

- Kein spezielles ARIA required — semantischer Text reicht
- CTA-Button folgt Button-Spec

---

## Code Pattern

```tsx
<EmptyState
  title={t("narratives.empty.title")}
  subtitle={t("narratives.empty.subtitle")}
  actionLabel={t("narratives.empty.create")}
  onAction={handleCreate}
/>
```

---

## Do / Don't

❌ Leerer Container ohne EmptyState
✅ Immer eine EmptyState-Nachricht zeigen

❌ Spinner als dauerhaften Zustand zeigen wenn keine Daten kommen
✅ Nach Timeout EmptyState oder Error-Variante zeigen

---

## Missing Information Protocol

```tsx
// TODO(design): Icon-Illustrationen für leere Zustände — Issue #TODO
// TODO(i18n): empty-state t()-Keys pro Domain festlegen — Issue #TODO
```

---

## Related

- `info-card.md` — für systemische Hinweise (nicht datenbezogene Leerzustände)
- `button.md` — CTA im EmptyState
