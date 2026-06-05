# Button

## Purpose

Triggers an action. Never used for navigation to a URL — use `<a>` or React Router
`<Link>` for that. One `primary` button per screen at most.

---

## Variants

| Variant     | When to use                                    | Visual                                              |
|-------------|------------------------------------------------|-----------------------------------------------------|
| `primary`   | Main CTA per screen (save, create, submit)     | Dark fill (`color.text.primary`), white text        |
| `secondary` | Secondary action at same hierarchy as primary  | No fill, `color.border.default` border              |
| `ghost`     | Low-emphasis: navigation back, inline actions  | No fill, no border                                  |
| `nav-item`  | Sidebar list items with selection state        | Full-width, left-aligned, blue highlight when active |

---

## States

| State      | Trigger                          | Visual change                                                      |
|------------|----------------------------------|--------------------------------------------------------------------|
| `default`  | —                                | —                                                                  |
| `hover`    | Mouse over                       | TODO(design): not yet specified — Issue #TODO                      |
| `focus`    | Keyboard focus                   | Browser default outline (do not remove)                            |
| `disabled` | `disabled` prop true             | `color.bg.subtle` fill, `color.text.tertiary` text, `cursor: not-allowed` |
| `loading`  | Async operation in flight        | Same as disabled + label replaced with `"…"`                       |

> **TODO(design):** Hover states not defined — all variants. Issue to be created.

---

## Props

| Prop        | Type                                          | Required | Default     | Description                          |
|-------------|-----------------------------------------------|----------|-------------|--------------------------------------|
| `onClick`   | `() => void` or `() => Promise<void>`         | yes      | —           | Action handler                       |
| `disabled`  | `boolean`                                     | no       | `false`     | Disables interaction                 |
| `isLoading` | `boolean`                                     | no       | `false`     | Disables + replaces label with `"…"` |
| `type`      | `"button" \| "submit" \| "reset"`             | no       | `"button"`  | HTML button type                     |
| `aria-label`| `string`                                      | no       | —           | Required when label is icon-only     |
| `style`     | `React.CSSProperties`                         | no       | —           | Override or extend inline styles     |

> Note: In the current codebase buttons are not yet extracted as a shared component —
> they are inline `<button>` elements in each screen. The props above describe the
> intended API once extraction happens.

---

## Rules

- Label text always via `t('key')` — no hardcoded strings in any language
- No fixed `width` — use `padding` to size, let content determine width
- Exception: full-width `nav-item` and single-action CTAs may use `width: "100%"` when
  they span their container deliberately (not to set a text-based width)
- Every async handler: `setLoading(true)` + `finally { setLoading(false) }`
- `disabled` must be `true` while `isLoading` is `true`
- `primary` variant: maximum one per screen

---

## Known Token Gaps

The following values appear in existing button code but are not yet in the token files.
GitHub Issues must be created before these buttons are extracted into a shared component.

| Gap | Current code | Needed token | Action |
|-----|-------------|--------------|--------|
| White text on primary | `color: "#FFFFFF"` | `color.text.inverse` | TODO: Issue to create `color.text.inverse: #FFFFFF` |
| 13px font size | `fontSize: "13px"` | `font.size.sm2` or rename existing | TODO: Issue — `font.size.sm = 12px` and `font.size.base = 14px`, no 13px slot |
| 10px padding | `padding: "10px ..."` | — | TODO: Issue — round to `spacing.sm=8` or `spacing.md=12` |

---

## Accessibility

- HTML element: always `<button>` (not `<div>`, not `<span>`)
- Button with visible text label: no extra `aria-*` needed
- Icon-only button: `aria-label` is mandatory
- Loading state: add `aria-busy={isLoading}` alongside `disabled`
- Keyboard: Enter and Space activate the button natively (do not re-implement)
- Focus: do not set `outline: none` — browser default is acceptable

---

## Code Pattern

### Primary (async, current inline pattern)

```tsx
// Current inline pattern — used in NarrativeEditor, WirkgefuegeVorschlag, NarrativeAnalyse
// TODO(i18n): all label strings must be replaced with t('...') before extraction

const [isLoading, setIsLoading] = useState(false);

const handleAction = async () => {
  setIsLoading(true);
  try {
    await someApiCall();
  } finally {
    setIsLoading(false); // always — success AND error path
  }
};

<button
  onClick={handleAction}
  disabled={isLoading || !canSubmit}
  aria-busy={isLoading}
  style={{
    background: isLoading || !canSubmit
      ? "var(--color-bg-subtle)"
      : "var(--color-text-primary)",   // #1A1A1A — correct token usage
    // TODO(token): color should be color.text.inverse once created — Issue #TODO
    color: isLoading || !canSubmit ? "var(--color-text-tertiary)" : "#FFFFFF",
    border: "none",
    borderRadius: "6px",             // radius.md
    padding: "8px 16px",             // spacing.sm / spacing.lg
    fontSize: "14px",                // font.size.base
    fontWeight: "500",               // font.weight.medium
    cursor: isLoading || !canSubmit ? "not-allowed" : "pointer",
  }}
>
  {isLoading ? "…" : t("actions.save")}
</button>
```

### Ghost (navigation back)

```tsx
<button
  onClick={() => navigate(-1)}
  style={{
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--color-text-secondary)",
    padding: "0",
    fontSize: "14px",               // font.size.base
  }}
>
  ← {t("actions.back")}
</button>
```

### Secondary (low-emphasis action)

```tsx
<button
  onClick={onAction}
  style={{
    background: "var(--color-bg)",
    border: "1px solid var(--color-border)",
    borderRadius: "6px",            // radius.md
    padding: "5px 12px",            // TODO(token): 5px not in spacing — Issue #TODO
    fontSize: "12px",               // font.size.sm
    cursor: "pointer",
    color: "var(--color-text-secondary)",
  }}
>
  {t("actions.accept_all")}
</button>
```

### Nav-item (sidebar selection)

```tsx
<button
  onClick={() => onSelect(item.id)}
  style={{
    background: isSelected ? "var(--color-blue-bg)" : "none",
    border: "none",
    borderRadius: "6px",            // radius.md
    padding: "8px 10px",            // spacing.sm / TODO(token): 10px not in spacing
    cursor: "pointer",
    width: "100%",
    textAlign: "left",
    fontSize: "13px",               // TODO(token): 13px not in typography scale
    color: isSelected ? "var(--color-blue-text)" : "var(--color-text-primary)",
    fontWeight: isSelected ? "500" : "normal",
  }}
>
  {item.label}
</button>
```

---

## Do / Don't (Button-specific)

❌ Raw hex for primary button text color
```tsx
color: "#FFFFFF"   // not a token yet
```
✅ Use `var(--color-bg)` as interim (same value), mark TODO
```tsx
color: "var(--color-bg)"  // TODO(token): use color.text.inverse once created
```

❌ Hardcoded label
```tsx
<button>Anlegen</button>
<button>Speichere…</button>
```
✅ i18n key
```tsx
<button>{isLoading ? "…" : t("actions.create")}</button>
```

❌ Missing `finally` in async handler
```tsx
try { await save(); } catch (e) { setLoading(false); }  // breaks on success
```
✅ `finally` guarantees reset on both paths
```tsx
try { await save(); } finally { setLoading(false); }
```

---

## Missing Information Protocol

```tsx
// TODO(token): color.text.inverse (#FFFFFF) needed for primary button text — Issue #TODO
// TODO(token): 13px font size not in typography scale — Issue #TODO
// TODO(token): 10px padding not in spacing scale — Issue #TODO
// TODO(design): hover states not specified for any variant — Issue #TODO
// TODO(i18n): hardcoded labels "Anlegen", "Speichere…" etc. need t() keys — Issue #TODO
```

---

## Related

- `design/patterns/async-states.md` — loading/error pattern (not yet written)
- `design/tokens/colors.json` — `color.text.primary`, semantic colors
- `design/tokens/spacing.json` — `spacing.sm=8`, `spacing.md=12`, `spacing.lg=16`
- `design/tokens/radii.json` — `radius.md=6px` for buttons
- `design/tokens/typography.json` — `font.size.base=14px`, `font.weight.medium=500`
