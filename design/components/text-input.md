# TextInput

## Purpose

Einzeiliges Texteingabefeld für Formular-Felder — Titel, Namen, kurze Freitexte. Mit Label, optionalem Helper-Text und Error-State. Gegenstück zu TextArea für mehrzeiligen Text.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Allgemeines Eingabefeld | Label oben, Input darunter |
| `with-ai` | KI kann den Wert befüllen | Zusätzlicher AI-Button rechts im Feld — siehe `field-with-ai.md` |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `empty` | Kein Wert | Placeholder sichtbar |
| `filled` | Wert eingegeben | — |
| `focused` | Fokus | Fokus-Ring |
| `error` | Validierungsfehler | Roter Rand, Error-Message unterhalb |
| `disabled` | `disabled` prop | Gedimmt, nicht klickbar |
| `read-only` | `readOnly` prop | Kein Cursor, kein Fokus-Ring |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Für Label-Input-Verknüpfung |
| `label` | `string` | yes | — | Sichtbares Label (via t()-Key) |
| `value` | `string` | yes | — | Kontrollierter Wert |
| `onChange` | `(value: string) => void` | yes | — | Callback bei Änderung |
| `placeholder` | `string \| null` | no | `null` | Placeholder (via t()-Key) |
| `helperText` | `string \| null` | no | `null` | Erklärender Text unterhalb |
| `errorMessage` | `string \| null` | no | `null` | Fehlermeldung — null = kein Error |
| `disabled` | `boolean` | no | `false` | Deaktiviert |
| `readOnly` | `boolean` | no | `false` | Nur lesbar |
| `maxLength` | `number \| null` | no | `null` | Maximale Zeichenlänge |
| `type` | `"text" \| "email" \| "password" \| "url"` | no | `"text"` | Input-Typ |

---

## Rules

- Immer kontrolliert — kein uncontrolled state
- Label ist immer sichtbar — kein Label-only-Aria
- Validierung liegt außerhalb der Komponente (in der Page oder im Service-Layer)
- `id` muss auf der Page eindeutig sein

---

## Accessibility

- `<label htmlFor={id}>` verknüpft mit dem Input
- `aria-describedby` zeigt auf Helper-Text oder Error-Message
- `aria-invalid="true"` wenn `errorMessage` vorhanden
- Error-Message `role="alert"` damit Screen Reader sie vorliest

---

## Code Pattern

```tsx
<TextInput
  id="scene-title"
  label={t("scene.title.label")}
  value={title}
  onChange={setTitle}
  errorMessage={errors.title ? t(errors.title) : null}
  placeholder={t("scene.title.placeholder")}
/>
```

---

## Do / Don't

❌ Validierungslogik im TextInput
✅ `errorMessage` von außen übergeben

❌ Label weglassen und nur Placeholder verwenden
✅ Immer ein sichtbares Label

---

## Missing Information Protocol

```tsx
// TODO(design): Fokus-Ring Token — Issue #TODO
// TODO(design): Error-State Farb-Tokens — Issue #TODO
// TODO(design): Label-Typografie (Größe, Gewicht) — Issue #TODO
```

---

## Related

- `text-area.md` — Mehrzeiliges Textfeld
- `search-input.md` — Suche/Filter ohne Formular-Kontext
- `field-with-ai.md` — TextInput-Erweiterung mit KI-Unterstützung
