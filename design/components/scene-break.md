# SceneBreak

## Purpose

Visueller Trenner zwischen Szenen in der Manuskriptansicht — zeigt den Szenen-Titel zentriert zwischen zwei horizontalen Linien. Kein Absatzumbruch, sondern ein struktureller Marker für den Autor.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Szenen-Trenner | Titel zentriert, Linien links und rechts |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | `string` | yes | — | Szenen-Titel (zentriert) |

---

## Rules

- Kein editierbarer Inhalt — nur Darstellung
- Szenen-Titel kommt aus dem Modell, kein direktes Editieren hier
- Volle Breite des Eltern-Containers

---

## Accessibility

- Rein visuell / strukturell — kein interaktives Element
- Linien: `aria-hidden="true"`

---

## Missing Information Protocol

```tsx
// TODO(design): Schrift-Größe und Gewicht des Szenen-Titels — Issue #TODO
// TODO(design): Vertikaler Abstand zum umgebenden Text — Issue #TODO
```

---

## Related

- `chapter-container.md` — übergeordneter struktureller Container
- `bottom-bar.md` — BottomBar zeigt die Gesamt-Wortzahl aller Szenen
