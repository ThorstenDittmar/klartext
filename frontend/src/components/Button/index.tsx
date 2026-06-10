import { useState, type CSSProperties, type ReactNode } from "react";

// Spec: design/components/button.md

export type ButtonVariant = "primary" | "secondary" | "ghost" | "nav-item";

export interface ButtonProps {
  children: ReactNode;
  /** Visual variant — determines fill, border and text colour. Default: "primary". */
  variant?: ButtonVariant;
  onClick?: () => void | Promise<void>;
  disabled?: boolean;
  /** Disables the button and sets aria-busy="true". Caller still controls the label. */
  isLoading?: boolean;
  type?: "button" | "submit" | "reset";
  /** Required for icon-only buttons that have no visible text label. */
  "aria-label"?: string;
  /** Escape hatch — merged last, overrides all variant styles. */
  style?: CSSProperties;
  /** Makes the button span the full width of its container. */
  fullWidth?: boolean;
  /** nav-item variant only — applies the active (blue highlight) style. */
  isActive?: boolean;
}

/** Shared button component. Covers primary, secondary, ghost, and nav-item variants.
 *  Labels are passed as children — callers are responsible for i18n via t('key'). */
export function Button({
  children,
  variant = "primary",
  onClick,
  disabled = false,
  isLoading = false,
  type = "button",
  "aria-label": ariaLabel,
  style: styleProp,
  fullWidth = false,
  isActive = false,
}: ButtonProps) {
  // TODO(design): hover states not specified for any variant — Issue #TODO
  const [isHovered, setIsHovered] = useState(false);
  const isDisabled = disabled || isLoading;

  const baseStyle: CSSProperties = {
    fontFamily: "var(--font-sans)",
    cursor: isDisabled ? "not-allowed" : "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",            // spacing.sm
    lineHeight: "1.3",     // font.lineHeight.tight
    width: fullWidth ? "100%" : undefined,
    whiteSpace: "nowrap",
    userSelect: "none",
    textDecoration: "none",
    transition: "opacity 0.1s",
    opacity: isDisabled ? 0.6 : 1,
  };

  function getPrimaryStyle(): CSSProperties {
    return {
      background: isDisabled
        ? "var(--color-bg-subtle)"
        : isHovered
        ? "var(--color-text-primary)"  // TODO(design): hover = slight lighten — Issue #TODO
        : "var(--color-text-primary)",
      color: isDisabled ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
      border: isDisabled ? "1px solid var(--color-border)" : "none",
      borderRadius: "6px",   // radius.md
      padding: "8px 16px",   // spacing.sm spacing.lg
      fontSize: "14px",      // font.size.base
      fontWeight: "500",     // font.weight.medium
    };
  }

  function getSecondaryStyle(): CSSProperties {
    return {
      background: isHovered ? "var(--color-bg-subtle)" : "var(--color-bg)",
      color: isDisabled ? "var(--color-text-tertiary)" : "var(--color-text-secondary)",
      border: "1px solid var(--color-border)",
      borderRadius: "6px",   // radius.md
      padding: "8px 12px",   // spacing.sm spacing.md
      fontSize: "14px",      // font.size.base
      fontWeight: "500",     // font.weight.medium
    };
  }

  function getGhostStyle(): CSSProperties {
    return {
      background: isHovered ? "var(--color-bg-subtle)" : "none",
      color: isDisabled ? "var(--color-text-tertiary)" : "var(--color-text-secondary)",
      border: "none",
      borderRadius: "6px",   // radius.md
      padding: "4px 8px",    // spacing.xs spacing.sm
      fontSize: "14px",      // font.size.base
      fontWeight: "400",     // font.weight.normal
    };
  }

  function getNavItemStyle(): CSSProperties {
    return {
      background: isActive
        ? "var(--color-blue-bg)"
        : isHovered
        ? "var(--color-bg-subtle)"
        : "none",
      color: isActive
        ? "var(--color-blue-text)"
        : isDisabled
        ? "var(--color-text-tertiary)"
        : "var(--color-text-primary)",
      border: "none",
      borderRadius: "6px",   // radius.md
      padding: "8px 12px",   // spacing.sm spacing.md
      fontSize: "13px",      // font.size.sm2
      fontWeight: isActive ? "500" : "400",
      width: "100%",
      textAlign: "left",
      justifyContent: "flex-start",
    };
  }

  const variantStyleMap: Record<ButtonVariant, () => CSSProperties> = {
    primary:    getPrimaryStyle,
    secondary:  getSecondaryStyle,
    ghost:      getGhostStyle,
    "nav-item": getNavItemStyle,
  };

  return (
    <button
      type={type}
      onClick={isDisabled ? undefined : onClick}
      disabled={isDisabled}
      aria-label={ariaLabel}
      aria-busy={isLoading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        ...baseStyle,
        ...variantStyleMap[variant](),
        ...styleProp,
      }}
    >
      {children}
    </button>
  );
}
