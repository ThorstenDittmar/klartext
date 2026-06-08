import type { CSSProperties } from "react";

// Spec: design/components/breadcrumb.md

export interface BreadcrumbItem {
  /** Segment label — pass pre-translated string. */
  label: string;
  /** If provided, renders the segment as a clickable button. */
  onClick?: () => void;
}

export interface BreadcrumbProps {
  /** Ordered path segments. The last item is the current page (not clickable). */
  items: BreadcrumbItem[];
  /** Separator style between segments. Default: chevron. */
  separator?: "slash" | "chevron";
}

const separatorChar: Record<NonNullable<BreadcrumbProps["separator"]>, string> = {
  slash: "/",
  chevron: "›",
};

/** Horizontal navigation breadcrumb. Last segment marks current page with aria-current. */
export function Breadcrumb({ items, separator = "chevron" }: BreadcrumbProps) {
  const sep = separatorChar[separator];

  const listStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "4px",
    listStyle: "none",
    margin: 0,
    padding: 0,
  };

  const linkStyle: CSSProperties = {
    background: "none",
    border: "none",
    padding: 0,
    cursor: "pointer",
    fontSize: "var(--font-size-sm)",
    color: "var(--color-text-secondary)",
    fontFamily: "var(--font-sans)",
    textDecoration: "underline",
  };

  const currentStyle: CSSProperties = {
    fontSize: "var(--font-size-sm)",
    color: "var(--color-text-primary)",
    fontWeight: "500",
    fontFamily: "var(--font-sans)",
  };

  const sepStyle: CSSProperties = {
    color: "var(--color-text-tertiary)",
    fontSize: "var(--font-size-sm)",
    userSelect: "none",
  };

  return (
    <nav aria-label="Breadcrumb">
      <ol style={listStyle}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              {isLast ? (
                <span aria-current="page" style={currentStyle}>
                  {item.label}
                </span>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={item.onClick}
                    style={linkStyle}
                  >
                    {item.label}
                  </button>
                  <span aria-hidden="true" style={sepStyle}>
                    {sep}
                  </span>
                </>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
