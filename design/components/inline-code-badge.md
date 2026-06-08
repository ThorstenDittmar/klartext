# InlineCodeBadge

## Purpose

Monospace-Pill für technische Bezeichner die im Fließtext vorkommen — z.B. API-Schlüssel-Namen, Feld-Bezeichnungen, kurze Code-Snippets. Rein visuell/semantisch, nicht interaktiv.

---

## Variants

Keine Varianten — einheitliches Aussehen.

---

## States

Keine interaktiven States.

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `children` | `string` | yes | — | Anzuzeigender Code-Text |
| `copyable` | `boolean` | no | `false` | Copy-to-Clipboard Button neben dem Badge |

---

## Rules

- Nur für kurze Bezeichner (~30 Zeichen max) — kein mehrzeiliger Code
- Für mehrzeiligen Code: eigene Code-Block-Komponente (noch nicht spezifiziert)
- `copyable = true` zeigt Copy-Icon rechts, Klick kopiert den Text

---

## Accessibility

- `<code>` HTML-Element für semantisch korrektes Markup
- `copyable`-Button: `aria-label="Kopieren"` + visuelles Feedback nach dem Kopieren

---

## Code Pattern

```tsx
// In einem Info-Text
<p>
  {t("settings.api_key_hint")}{" "}
  <InlineCodeBadge copyable>ANTHROPIC_API_KEY</InlineCodeBadge>
</p>
```

---

## Do / Don't

❌ InlineCodeBadge für langen Code (mehrere Zeilen)
✅ Eigene CodeBlock-Komponente für mehrzeiligen Code

❌ InlineCodeBadge für normale Labels oder Status-Tags
✅ Badge-Komponente für Labels, InlineCodeBadge nur für technische Bezeichner

---

## Missing Information Protocol

```tsx
// TODO(design): Monospace-Schrift und Padding als Tokens — Issue #TODO
// TODO(design): Hintergrundfarbe (hell/dunkel Theme) — Issue #TODO
// TODO(ux): Wo im Produkt kommen technische Bezeichner vor? — Issue #TODO
```

---

## Related

- `badge.md` — Für semantische Labels, nicht technische Bezeichner
- `info-card.md` — Kontext in dem InlineCodeBadge oft vorkommt
