# EpistemicBadge

## Purpose

Displays the epistemic status of a causal model slot or relation as a colour-coded pill badge.
Amber = incomplete (default), green = axiomatic. Display-only — no interactive behaviour.
Not to be used as a button or clickable element.

---

## Variants

| Variant | When to use | Visual description |
|---------|-------------|--------------------|
| `default` | All uses — single visual style, colour varies by status value | Pill badge, amber background for "incomplete", green background for "axiomatic" |

---

## States

| State | Trigger | Visual change |
|-------|---------|---------------|
| `default` | — | — |

This is a display-only component. No hover, focus, disabled, loading, or error states.

---

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | `string` | yes | — | Epistemic status value from the API ("incomplete" \| "axiomatic") |

---

## Rules

- No `onClick`, no interactive behaviour — use a plain `<span>`
- Status label rendered directly as `{status}` (API enum value). i18n TODO noted in code.
- `minWidth` not needed — badge grows with its content
- Pill shape via `borderRadius: "9999px"` (`radius.full`)
- Colour uses CSS custom properties only — no raw hex values
- Two-value colour mapping: `"axiomatic"` → green (`--color-green-bg` / `--color-green-text`), everything else → amber (`--color-amber-bg` / `--color-amber-text`)

---

## Accessibility

- Rendered as `<span>` — decorative display element, no interactive semantics needed
- No `aria-label` required when used in a table cell: the surrounding column header provides context
- If `EpistemicBadge` is the **only** information in its container (e.g. a standalone status display), add `aria-label={t('status.epistemic.label', { status })}` to the wrapping element
- No keyboard behaviour — not focusable

---

## Code Pattern

```tsx
// Minimal usage — status value comes directly from the API
<EpistemicBadge status={slot.epistemic_status} />
```

---

## Do / Don't (Komponenten-spezifisch)

❌ Using a raw hex color or hardcoded background
```tsx
<span style={{ background: "#FAEEDA" }}>incomplete</span>
```

✅ CSS custom properties from design tokens
```tsx
<EpistemicBadge status="incomplete" />
// → background: var(--color-amber-bg), color: var(--color-amber-text)
```

❌ Wrapping in a button or adding onClick
```tsx
<button onClick={handleClick}><EpistemicBadge status={s} /></button>
```

✅ Separate the badge from any interactive affordance
```tsx
<td>
  <EpistemicBadge status={s.epistemic_status} />
  <button onClick={handleEdit}>{t('actions.edit')}</button>
</td>
```

---

## Missing Information Protocol

```tsx
// TODO(i18n): status values should be translated via t('status.epistemic.{status}')
// Interim: rendering raw API enum value until i18n keys are defined
{status}
```

```tsx
// TODO(token): 2px vertical padding not in spacing scale
padding: "2px 8px"
```

---

## Related

- `design/tokens/colors.json` — `color.semantic.amber`, `color.semantic.green`
- `design/tokens/radii.json` — `radius.full` (9999px, pill shape)
- `design/tokens/typography.json` — `font.size.xs` (11px), `font.weight.medium` (500)
- `frontend/src/components/EpistemicBadge.tsx` — implementation
