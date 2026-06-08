import type { CSSProperties } from "react";

// Spec: design/components/scene-break.md

export interface SceneBreakProps {
  /** Scene title shown centered between the two decorative rules. */
  title: string;
}

/** Visual separator between scenes in the Manuscript View. Purely presentational. */
export function SceneBreak({ title }: SceneBreakProps) {
  const containerStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    margin: "32px 0 16px",
  };

  const ruleStyle: CSSProperties = {
    flex: 1,
    height: "1px",
    backgroundColor: "var(--color-border)",
  };

  const titleStyle: CSSProperties = {
    fontSize: "var(--font-size-sm)",
    color: "var(--color-text-secondary)",
    fontWeight: "500",
    letterSpacing: "0.05em",
    textTransform: "uppercase",
    whiteSpace: "nowrap",
    fontFamily: "var(--font-sans)",
  };

  return (
    <div style={containerStyle}>
      <div aria-hidden="true" style={ruleStyle} />
      <span style={titleStyle}>{title}</span>
      <div aria-hidden="true" style={ruleStyle} />
    </div>
  );
}
