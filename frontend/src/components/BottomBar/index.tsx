import type { CSSProperties } from "react";
import { AutosaveIndicator, type AutosaveStatus } from "../AutosaveIndicator";
import { WordCountLabel } from "../WordCountLabel";

// Spec: design/components/bottom-bar.md

export interface BottomBarProps {
  /** Pre-counted total word count across all fragments. */
  wordCount: number;
  /** Current autosave state. */
  saveStatus: AutosaveStatus;
}

/** Fixed bottom bar for the Manuscript View — shows total word count and autosave status. */
export function BottomBar({ wordCount, saveStatus }: BottomBarProps) {
  const style: CSSProperties = {
    position: "fixed",
    bottom: 0,
    left: 0,
    right: 0,
    height: "var(--bottom-bar-height)",
    backgroundColor: "var(--color-surface)",
    borderTop: "1px solid var(--color-border)",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 var(--space-4)",
    zIndex: 100,
  };

  return (
    <footer style={style}>
      <WordCountLabel count={wordCount} />
      <AutosaveIndicator status={saveStatus} />
    </footer>
  );
}
