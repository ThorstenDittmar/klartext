# Breadcrumb

## Purpose

Horizontale Navigations-Pfad-Anzeige — zeigt die aktuelle Position in der Hierarchie (z.B. Projekt → Kapitel → Szene). Letzte Ebene ist nicht klickbar, übergeordnete Ebenen sind Links.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standard-Breadcrumb | Text-Links getrennt durch „/" oder „›" |
| `with-selector` | Letzte Ebene ist wechselbar | Letztes Segment als Dropdown — siehe `breadcrumb-selector.md` |

---

## States

Keine eigenen States außer den Link-States der einzelnen Segmente.

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `segments` | `Array<{ label: string; href?: string }>` | yes | — | Pfad-Segmente — letztes ohne `href` |
| `separator` | `"slash" \| "chevron"` | no | `"chevron"` | Trenn-Symbol zwischen Segmenten |

---

## Rules

- Letztes Segment ist immer nicht-klickbar (aktuelle Position)
- Maximale Länge: 4 Segmente — längere Pfade werden mit „…" gekürzt (mittlere Segmente ausgeblendet)
- Labels via `t('key')` übergeben oder als bereits übersetzte Strings
- Kein Wrapping — Breadcrumb ist einzeilig

---

## Accessibility

- `<nav aria-label="Breadcrumb">` als Container
- `<ol>` für die Segment-Liste
- Letztes Segment: `aria-current="page"`
- Separator-Symbole: `aria-hidden="true"`

---

## Code Pattern

```tsx
<Breadcrumb
  segments={[
    { label: project.title, href: `/project/${project.id}` },
    { label: chapter.title, href: `/project/${project.id}/chapter/${chapter.id}` },
    { label: scene.title },
  ]}
/>
```

---

## Do / Don't

❌ Mehr als 4 Breadcrumb-Segmente ohne Kürzung
✅ Mittlere Segmente ausblenden und mit „…" ersetzen

❌ Letztes Segment klickbar machen
✅ Aktuelle Seite ist nie ein Link

---

## Missing Information Protocol

```tsx
// TODO(design): Separator-Symbol-Design — Issue #TODO
// TODO(design): Kürzungs-Logik bei langen Labels — Issue #TODO
// TODO(design): Schrift-Größe und Farbe — Issue #TODO
```

---

## Related

- `breadcrumb-selector.md` — Erweiterung des letzten Segments als Dropdown
- `app-bar.md` — Breadcrumb oft im oberen Bereich der AppBar
