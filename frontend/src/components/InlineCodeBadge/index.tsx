import { useState, type CSSProperties } from "react";

// Spec: design/components/inline-code-badge.md

export interface InlineCodeBadgeProps {
  children: string;
  /** Shows a copy-to-clipboard button alongside the badge. Default: false. */
  copyable?: boolean;
}

/** Monospace inline pill for technical identifiers — API keys, field names, short code snippets.
 *  For multi-line code use a separate CodeBlock component (not yet built). */
export function InlineCodeBadge({ children, copyable = false }: InlineCodeBadgeProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    /** Copies the badge content to clipboard and briefly shows a confirmation. */
    await navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  const codeStyle: CSSProperties = {
    display: "inline",
    fontFamily: "ui-monospace, 'SF Mono', 'Cascadia Code', monospace",
    fontSize: "12px",          // font.size.sm
    fontWeight: "400",
    // TODO(token): 2px vertical padding not in spacing scale — Issue #TODO
    padding: "2px 6px",
    borderRadius: "4px",       // radius.sm
    background: "var(--color-bg-subtle)",
    color: "var(--color-text-primary)",
    border: "1px solid var(--color-border)",
    lineHeight: "1.5",
  };

  const copyButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    marginLeft: "4px",         // spacing.xs
    padding: "2px 4px",
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--color-text-tertiary)",
    fontSize: "11px",          // font.size.xs
    borderRadius: "4px",       // radius.sm
    fontFamily: "var(--font-sans)",
  };

  return (
    <>
      <code style={codeStyle}>{children}</code>
      {copyable && (
        <button
          type="button"
          onClick={handleCopy}
          aria-label={copied ? "Kopiert!" : "Kopieren"}
          title={copied ? "Kopiert!" : "Kopieren"}
          style={copyButtonStyle}
        >
          {copied ? "✓" : "⧉"}
        </button>
      )}
    </>
  );
}
