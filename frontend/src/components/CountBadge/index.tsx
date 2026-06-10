import type { CSSProperties } from "react";

// Spec: design/components/count-badge.md

export interface CountBadgeProps {
  /** Numeric count to display. */
  count: number;
  /** Values above this render as "{max}+". Default: 99. */
  max?: number;
  /** "inline" shows the number; "dot" shows a plain circle indicator. Default: "inline". */
  variant?: "inline" | "dot";
  /** Hide badge when count is 0. Default: true. */
  hideWhenZero?: boolean;
  /** Accessible label for screen readers — e.g. "3 Szenen". */
  "aria-label"?: string;
}

/** Numeric count indicator. Read-only, not interactive.
 *  For text labels use Badge; for dot notifications use variant="dot". */
export function CountBadge({
  count,
  max = 99,
  variant = "inline",
  hideWhenZero = true,
  "aria-label": ariaLabel,
}: CountBadgeProps) {
  if (hideWhenZero && count === 0) return null;

  const baseStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "var(--font-sans)",
    fontWeight: "500",        // font.weight.medium
    lineHeight: 1,
    borderRadius: "9999px",   // radius.full
    background: "var(--color-text-secondary)",
    color: "var(--color-text-inverse)",
    flexShrink: 0,
  };

  if (variant === "dot") {
    return (
      <span
        aria-label={ariaLabel ?? "Neue Einträge vorhanden"}
        style={{
          ...baseStyle,
          width: "8px",
          height: "8px",
          background: "var(--color-red-text)",
        }}
      />
    );
  }

  const label = count > max ? `${max}+` : String(count);

  return (
    <span
      aria-label={ariaLabel}
      style={{
        ...baseStyle,
        // TODO(token): 2px vertical padding not in spacing scale — Issue #TODO
        padding: "2px 6px",
        fontSize: "11px",      // font.size.xs
        minWidth: "18px",
      }}
    >
      {label}
    </span>
  );
}
