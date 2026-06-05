# [Component Name]

<!--
  Vorlage für neue Komponenten-Specs.
  Alle Abschnitte sind Pflicht. Fehlende Informationen werden als
  "TODO — Issue #XX" markiert, nicht weggelassen.
-->

## Purpose

Ein Satz: Was tut diese Komponente? Wofür wird sie verwendet?
Was ist kein Anwendungsfall (abgrenzen wenn hilfreich)?

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | Standardfall | ... |
| `...`     | ...         | ... |

---

## States

| State      | Trigger                    | Visual change                         |
|------------|----------------------------|---------------------------------------|
| `default`  | —                          | —                                     |
| `hover`    | Mouse over                 | ...                                   |
| `focus`    | Keyboard focus             | Sichtbarer Fokus-Ring (Browser default oder custom) |
| `disabled` | `disabled` prop = true     | opacity: 0.4, cursor: not-allowed     |
| `loading`  | Async operation in flight  | disabled + ... (Spinner o.ä.)         |
| `error`    | Validation failed          | ...                                   |

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `...` | `...` | yes/no | `...` | ... |

---

## Rules

- Bullet-Liste verbindlicher Regeln für diese Komponente
- z.B. "Label immer via t('key'), kein Hardcoding"
- z.B. "Kein festes width wenn der Inhalt Text ist"
- z.B. "Immer finally für Async-Reset"

---

## Accessibility

Spezifische A11y-Anforderungen für diese Komponente (zusätzlich zu `accessibility.md`):

- Welches HTML-Element? (`button`, `a`, `input`, ...)
- Braucht `aria-label`? Wann?
- Keyboard-Verhalten (Enter, Space, Escape, Arrow Keys)?
- Gibt es `aria-expanded`, `aria-selected`, etc.?

---

## Code Pattern

```tsx
// Minimalbeispiel das alle Rules und States zeigt
// Kein Showcase-Code — nur was der Agent tatsächlich bauen soll

function ComponentName({ ... }: ComponentNameProps) {
  // ...
}
```

---

## Do / Don't (Komponenten-spezifisch)

❌ Was für diese Komponente spezifisch verboten ist

✅ Was stattdessen

---

## Missing Information Protocol

Wenn beim Bauen dieser Komponente Informationen fehlen:

```tsx
// TODO(design): [was fehlt] — Issue #XX
// Interim: [was vorläufig verwendet wird und warum]
```

---

## Related

- Andere Komponenten die zusammen verwendet werden
- Patterns aus `design/patterns/` die relevant sind
- Design-Tokens die primär hier verwendet werden
