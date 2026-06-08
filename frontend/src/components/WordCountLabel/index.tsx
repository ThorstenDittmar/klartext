import type { CSSProperties } from "react";

// Spec: design/components/word-count-label.md

export interface WordCountLabelProps {
  /** Pre-counted word total to display. */
  count: number;
  /** Unit suffix shown after the number. TODO(i18n): pass via t('manuscript.word_count_suffix'). */
  suffix?: string;
  /** sm = 13px, md = 16px. Default: md. */
  size?: "sm" | "md";
}

/** Displays a formatted word count — e.g. "1.240 Wörter". Used in BottomBar. */
export function WordCountLabel({ count, suffix = "Wörter", size = "md" }: WordCountLabelProps) {
  const style: CSSProperties = {
    fontSize: size === "sm" ? "var(--font-size-sm)" : "var(--font-size-base)",
    color: "var(--color-text-secondary)",
    fontVariantNumeric: "tabular-nums",
    fontFamily: "var(--font-sans)",
  };

  return (
    <span style={style}>
      {count.toLocaleString("de-DE")} {suffix}
    </span>
  );
}
