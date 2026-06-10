import type { CSSProperties } from "react";

// Spec: design/components/badge.md

export type BadgeColorKey = "default" | "green" | "amber" | "red" | "blue" | "teal";
export type BadgeVariant = "status" | "category" | "outline";

export interface BadgeProps {
  /** Display text — pass already-translated string via t('key') at call site. */
  label: string;
  /** Token-based colour key. Default: "default" (neutral grey). */
  colorKey?: BadgeColorKey;
  /** Visual style variant. Default: "status". */
  variant?: BadgeVariant;
}

const COLOR_MAP: Record<BadgeColorKey, { bg: string; text: string }> = {
  default: { bg: "var(--color-bg-subtle)",  text: "var(--color-text-secondary)" },
  green:   { bg: "var(--color-green-bg)",   text: "var(--color-green-text)" },
  amber:   { bg: "var(--color-amber-bg)",   text: "var(--color-amber-text)" },
  red:     { bg: "var(--color-red-bg)",     text: "var(--color-red-text)" },
  blue:    { bg: "var(--color-blue-bg)",    text: "var(--color-blue-text)" },
  teal:    { bg: "var(--color-teal-bg)",    text: "var(--color-teal-text)" },
};

/** Read-only pill label for categories, status and type tags. Not interactive.
 *  For numeric counters use CountBadge. For clickable tags use a button instead. */
export function Badge({
  label,
  colorKey = "default",
  variant = "status",
}: BadgeProps) {
  const { bg, text } = COLOR_MAP[colorKey];

  const style: CSSProperties = {
    display: "inline-block",
    fontSize: "11px",          // font.size.xs
    fontWeight: "500",         // font.weight.medium
    fontFamily: "var(--font-sans)",
    whiteSpace: "nowrap",
    borderRadius: "9999px",    // radius.full — pill
    // TODO(token): 2px vertical padding not in spacing scale — Issue #TODO
    padding: "2px 8px",
    background: variant === "outline" ? "transparent" : bg,
    color: text,
    border: variant === "outline" ? `1px solid ${text}` : "none",
    minWidth: "40px",
    textAlign: "center",
    lineHeight: "1.5",         // font.lineHeight.normal
  };

  return <span style={style}>{label}</span>;
}
