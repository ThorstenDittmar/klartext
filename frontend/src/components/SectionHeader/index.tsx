import type { CSSProperties } from "react";
import { CountBadge } from "../CountBadge";

// Spec: design/components/section-header.md

export interface SectionHeaderProps {
  /** Section title. Pass pre-translated string via t('key'). */
  title: string;
  /** Number of items in the section. null = no badge. */
  count?: number | null;
  /** Whether the section can be collapsed. Default: true. */
  isCollapsible?: boolean;
  /** Current collapsed state. Default: false. */
  isCollapsed?: boolean;
  /** Called when the header is clicked to toggle collapse. */
  onToggle: () => void;
  /** Shows a '+' button for inline add actions. null = hidden. */
  onAdd?: (() => void) | null;
}

/** Collapsible section heading with item count and optional inline add action.
 *  Used primarily in the Sidebar to group entity lists. */
export function SectionHeader({
  title,
  count = null,
  isCollapsible = true,
  isCollapsed = false,
  onToggle,
  onAdd,
}: SectionHeaderProps) {
  const containerStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    width: "100%",
    minHeight: "28px",
  };

  const titleStyle: CSSProperties = {
    fontSize: "11px",          // font.size.xs
    fontWeight: "600",         // font.weight.semibold
    color: "var(--color-text-tertiary)",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    fontFamily: "var(--font-sans)",
    flex: 1,
    textAlign: "left",
  };

  const addButtonStyle: CSSProperties = {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--color-text-tertiary)",
    fontSize: "16px",
    lineHeight: 1,
    padding: "2px 4px",
    borderRadius: "4px",
    display: "flex",
    alignItems: "center",
    fontFamily: "var(--font-sans)",
    flexShrink: 0,
  };

  const arrowStyle: CSSProperties = {
    fontSize: "9px",
    color: "var(--color-text-tertiary)",
    transition: "transform 0.15s",
    transform: isCollapsed ? "rotate(-90deg)" : "rotate(0deg)",
    lineHeight: 1,
    flexShrink: 0,
  };

  return (
    <div style={containerStyle}>
      {isCollapsible ? (
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={!isCollapsed}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            flex: 1,
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
            minWidth: 0,
          }}
        >
          <span aria-hidden="true" style={arrowStyle}>▼</span>
          <span style={titleStyle}>{title}</span>
          {count !== null && count !== undefined && (
            <CountBadge count={count} aria-label={`${count} ${title}`} />
          )}
        </button>
      ) : (
        <div style={{ display: "flex", alignItems: "center", gap: "6px", flex: 1 }}>
          <span style={titleStyle}>{title}</span>
          {count !== null && count !== undefined && (
            <CountBadge count={count} aria-label={`${count} ${title}`} />
          )}
        </div>
      )}

      {onAdd && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onAdd();
          }}
          aria-label={`${title} hinzufügen`}
          style={addButtonStyle}
        >
          +
        </button>
      )}
    </div>
  );
}
