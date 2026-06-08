import type { CSSProperties } from "react";

// Spec: design/components/autosave-indicator.md

export type AutosaveStatus = "saving" | "saved" | "unsaved";

export interface AutosaveIndicatorProps {
  /** Current autosave state. */
  status: AutosaveStatus;
  /** TODO(i18n): pass via t('manuscript.autosave.saving'). */
  savingLabel?: string;
  /** TODO(i18n): pass via t('manuscript.autosave.saved'). */
  savedLabel?: string;
  /** TODO(i18n): pass via t('manuscript.autosave.unsaved'). */
  unsavedLabel?: string;
}

const COLOR_MAP: Record<AutosaveStatus, string> = {
  saving:  "var(--color-text-secondary)",
  saved:   "var(--color-success)",
  unsaved: "var(--color-error)",
};

/** Autosave status display for the BottomBar. Announced via aria-live on change. */
export function AutosaveIndicator({
  status,
  savingLabel  = "Speichert…",
  savedLabel   = "Gespeichert ✓",
  unsavedLabel = "Nicht gespeichert ⚠",
}: AutosaveIndicatorProps) {
  const label = { saving: savingLabel, saved: savedLabel, unsaved: unsavedLabel }[status];

  const style: CSSProperties = {
    fontSize: "var(--font-size-sm)",
    color: COLOR_MAP[status],
    transition: "color 0.3s ease",
    fontFamily: "var(--font-sans)",
  };

  return (
    <span style={style} aria-live="polite">
      {label}
    </span>
  );
}
