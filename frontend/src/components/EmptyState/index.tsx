import type { ReactNode } from "react";
import { Button } from "../Button";

// Spec: design/components/empty-state.md

type EmptyStateBase = {
  /** Main message — describe the current state, not the action. Pass via t('key'). */
  title: string;
  /** Supporting explanation of what the user can do. */
  subtitle?: string;
  /** Optional illustrative icon or illustration above the title. */
  icon?: ReactNode;
};

/** Either both actionLabel + onAction are provided, or neither. */
export type EmptyStateProps = EmptyStateBase &
  (
    | { actionLabel: string; onAction: () => void }
    | { actionLabel?: never; onAction?: never }
  );

/** Centred empty-state message for lists and panels that have no content yet.
 *  Always show an EmptyState instead of an empty container — never leave the user without context. */
export function EmptyState({ title, subtitle, actionLabel, onAction, icon }: EmptyStateProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "12px",           // spacing.md
        padding: "40px 24px",  // spacing.4xl spacing.2xl
        textAlign: "center",
      }}
    >
      {icon && (
        <div
          aria-hidden="true"
          style={{
            fontSize: "32px",
            color: "var(--color-text-tertiary)",
            lineHeight: 1,
          }}
        >
          {icon}
        </div>
      )}

      <h3
        style={{
          margin: 0,
          fontSize: "15px",    // font.size.md
          fontWeight: "500",   // font.weight.medium
          color: "var(--color-text-primary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {title}
      </h3>

      {subtitle && (
        <p
          style={{
            margin: 0,
            fontSize: "13px",  // font.size.sm2
            color: "var(--color-text-secondary)",
            fontFamily: "var(--font-sans)",
            lineHeight: "1.5", // font.lineHeight.normal
            maxWidth: "320px",
          }}
        >
          {subtitle}
        </p>
      )}

      {actionLabel && onAction && (
        <div style={{ marginTop: "4px" }}>  {/* spacing.xs */}
          <Button variant="primary" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
}
