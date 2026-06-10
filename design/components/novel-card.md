# NovelCard

## Purpose

Karte in der Projekt-/Bibliotheks-Übersicht — repräsentiert ein Schreibprojekt mit Cover, Titel, Autor und Metadaten. Klick öffnet das Projekt. Primäres Einstiegs-UI in der Library-Ansicht.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Library-Ansicht | Vertikale Karte mit Cover oben, Infos unten |
| `landscape` | Kompakte Listen-Ansicht | Horizontale Karte, Cover links |
| `add-new` | Neues Projekt anlegen | Plus-Symbol statt Cover, gestrichelter Rahmen |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |
| `hover` | Mouse over | Schatten + Cover leicht skaliert |
| `loading` | Cover wird geladen | Skeleton-Placeholder für Cover-Bereich |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Projekt-ID |
| `title` | `string` | yes | — | Projekt-Titel |
| `coverUrl` | `string \| null` | no | `null` | URL des Cover-Bilds |
| `authorName` | `string \| null` | no | `null` | Autorenname |
| `wordCount` | `number \| null` | no | `null` | Aktuelle Wortzahl |
| `lastEditedAt` | `string \| null` | no | `null` | Datum der letzten Bearbeitung (ISO 8601) |
| `onClick` | `() => void` | yes | — | Projekt öffnen |
| `onContextMenu` | `((e: React.MouseEvent) => void) \| null` | no | `null` | Rechtsklick |
| `variant` | `"default" \| "landscape" \| "add-new"` | no | `"default"` | Visueller Stil |

---

## Rules

- Cover-Fallback: Platzhalter-Illustration mit Projekt-Initial
- `lastEditedAt` wird relativ angezeigt (z.B. „vor 2 Tagen") — Formatierung im Hook
- Wortzahl formatiert via `toLocaleString()` übergeben
- `add-new`-Variante hat keinen `id`/Entitäts-Bezug — onClick erstellt neues Projekt

---

## Accessibility

- Gesamte Karte ist fokussierbar
- `aria-label` mit Projekttitel für Screen Reader
- Cover `<img>` mit `alt` Projekttitel
- Keyboard: Enter öffnet das Projekt

---

## Code Pattern

```tsx
<NovelCard
  id={project.id}
  title={project.title}
  coverUrl={project.coverUrl}
  wordCount={project.wordCount}
  lastEditedAt={project.updatedAt}
  onClick={() => navigate(`/project/${project.id}`)}
  onContextMenu={(e) => openContextMenu(e, project.id)}
/>
```

---

## Do / Don't

❌ Inline-Bearbeitung (Titel) direkt auf der Karte
✅ Modal oder DetailPanel für Projekt-Einstellungen

❌ Cover-URL ohne Fallback übergeben
✅ Fallback immer rendern wenn `coverUrl` null oder Ladefehler

---

## Missing Information Protocol

```tsx
// TODO(design): Cover-Seitenverhältnis (2:3 Buch-Format?) — Issue #TODO
// TODO(design): Cover-Fallback-Illustration — Issue #TODO
// TODO(design): Karten-Breite in Grid — Issue #TODO
// TODO(ux): Context Menu Optionen für Projekt-Karte — Issue #TODO
```

---

## Related

- `context-menu.md` — Bei Rechtsklick auf Karte
- `modal.md` — Projekt umbenennen/löschen
- `empty-state.md` — Wenn Library leer ist
