# TextArea

## Purpose

Mehrzeiliges Texteingabefeld für längere Freitexte — Beschreibungen, Zusammenfassungen, Notizen. Mit Label, optionalem Helper-Text, Error-State und Zeichen-Zähler.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Allgemeines mehrzeiliges Feld | Label oben, Textarea darunter |
| `auto-resize` | Höhe passt sich dem Inhalt an | Kein vertikaler Scrollbalken, wächst mit Text |
| `with-ai` | KI kann Inhalt befüllen oder ergänzen | AI-Button — siehe `field-with-ai.md` |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `empty` | Kein Wert | Placeholder sichtbar |
| `filled` | Wert vorhanden | — |
| `focused` | Fokus | Fokus-Ring |
| `error` | Validierungsfehler | Roter Rand, Error-Message unterhalb |
| `disabled` | `disabled` prop | Gedimmt, nicht editierbar |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `id` | `string` | yes | — | Für Label-Textarea-Verknüpfung |
| `label` | `string` | yes | — | Sichtbares Label (via t()-Key) |
| `value` | `string` | yes | — | Kontrollierter Wert |
| `onChange` | `(value: string) => void` | yes | — | Callback bei Änderung |
| `placeholder` | `string \| null` | no | `null` | Placeholder (via t()-Key) |
| `helperText` | `string \| null` | no | `null` | Erklärender Text unterhalb |
| `errorMessage` | `string \| null` | no | `null` | Fehlermeldung |
| `rows` | `number` | no | `4` | Initiale Anzahl sichtbarer Zeilen |
| `maxLength` | `number \| null` | no | `null` | Maximale Zeichenlänge — null = unbegrenzt |
| `showCharCount` | `boolean` | no | `false` | Zeichen-Zähler anzeigen |
| `autoResize` | `boolean` | no | `false` | Automatisches Höhen-Anpassen |
| `disabled` | `boolean` | no | `false` | Deaktiviert |

---

## Rules

- Immer kontrolliert — kein uncontrolled state
- Zeichen-Zähler nur wenn `maxLength` gesetzt ist
- `autoResize` verhindert manuelles Vergrößern durch den User
- Kein `resize: horizontal` — vertikales Resize optional wenn kein `autoResize`

---

## Accessibility

- `<label htmlFor={id}>` verknüpft mit der Textarea
- `aria-describedby` zeigt auf Helper-Text oder Error-Message
- `aria-invalid="true"` wenn `errorMessage` vorhanden
- `maxlength` Attribut auf dem Element für Browser-natives Handling

---

## Code Pattern

```tsx
<TextArea
  id="scene-description"
  label={t("scene.description.label")}
  value={description}
  onChange={setDescription}
  rows={5}
  autoResize
  placeholder={t("scene.description.placeholder")}
/>
```

---

## Do / Don't

❌ TextArea für einzeiligen Text verwenden
✅ TextInput für einzeiligen Text

❌ Unbegrenzte Textarea ohne minRows
✅ Sinnvolle initiale Höhe via `rows` prop

---

## Missing Information Protocol

```tsx
// TODO(design): Fokus-Ring und Error-Border Tokens — Issue #TODO
// TODO(design): Resize-Handle sichtbar oder versteckt — Issue #TODO
// TODO(ux): Auto-resize Schwellenwert — Issue #TODO
```

---

## Related

- `text-input.md` — Einzeiliges Formularfeld
- `field-with-ai.md` — TextArea-Erweiterung mit KI-Integration
