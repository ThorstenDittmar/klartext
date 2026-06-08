# ChapterContainer

## Purpose

Struktureller Container für ein Kapitel in der Kapitel-Ansicht — gruppiert Szenen oder Abschnitte die zum Kapitel gehören. Zeigt Kapitel-Titel, Kapitel-Nummer und Wort-Ziel vs. aktuell.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Kapitel-Liste im Plan | Kapitel-Header + Szenen/Abschnitte darunter |
| `collapsed` | Kapitel zugeklappt | Nur Header sichtbar |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `expanded` | Standard | Inhalte sichtbar |
| `collapsed` | Header-Klick | Inhalte ausgeblendet |
| `on-target` | Wort-Ziel ≥ 100% | Ziel-Indikator grün |
| `below-target` | Wort-Ziel < 100% | Ziel-Indikator neutral oder gelb |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Kapitel-ID |
| `title` | `string` | yes | — | Kapitel-Titel |
| `chapterNumber` | `number` | yes | — | Kapitel-Nummer |
| `wordCount` | `number` | yes | — | Aktuelle Wortzahl |
| `wordTarget` | `number \| null` | no | `null` | Wort-Ziel — null = kein Ziel |
| `isCollapsed` | `boolean` | no | `false` | Eingeklappt |
| `onToggle` | `() => void` | yes | — | Collapse/Expand |
| `children` | `React.ReactNode` | yes | — | Szenen oder Abschnitte |

---

## Rules

- Wort-Ziel-Anzeige nur wenn `wordTarget` gesetzt ist
- Wort-Ziel-Fortschritt als Prozentzahl oder Balken — noch nicht spezifiziert
- Kapitel-Nummer wird immer angezeigt
- Keine direkte Bearbeitung im Container-Header — via DetailPanel oder Modal

---

## Accessibility

- `aria-label` mit Kapitel-Nummer und Titel
- Collapse-Button: `aria-expanded`

---

## Code Pattern

```tsx
// TODO: noch nicht als shared Component extrahiert
```

---

## Do / Don't

❌ Kapitel-Logik im ChapterContainer
✅ Container ist Darstellung — Logik im Service/Hook

---

## Missing Information Protocol

```tsx
// TODO(design): Wort-Ziel-Darstellung (Balken vs. Zahl vs. Prozent) — Issue #TODO
// TODO(ux): Kapitel-Reihenfolge per Drag & Drop — Issue #TODO
// TODO(design): Kapitel-Header visuell vs. ActContainer — Issue #TODO
```

---

## Related

- `act-container.md` — Analoges Konzept für Akte
- `section-header.md` — Einfachere Variante für Listen in der Sidebar
- `word-count-label.md` — Wort-Anzeige im Header
