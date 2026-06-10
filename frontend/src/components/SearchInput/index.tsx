import { useRef, type CSSProperties } from "react";

// Spec: design/components/search-input.md

export type SearchInputVariant = "default" | "inline";

export interface SearchInputProps {
  /** Controlled value. */
  value: string;
  /** Called with the new string on every keystroke, and with "" when cleared. */
  onChange: (value: string) => void;
  /** Placeholder text — pass pre-translated string. */
  placeholder?: string;
  /** Focus the input on mount. */
  autoFocus?: boolean;
  disabled?: boolean;
  variant?: SearchInputVariant;
}

/** Controlled search/filter input with a magnifying-glass icon and optional clear button.
 *  Debouncing belongs in the hook or page that owns the state — not in this component. */
export function SearchInput({
  value,
  onChange,
  placeholder,
  autoFocus = false,
  disabled = false,
  variant = "default",
}: SearchInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const isInline = variant === "inline";

  const containerStyle: CSSProperties = {
    position: "relative",
    display: "flex",
    alignItems: "center",
    width: "100%",
    background: disabled ? "var(--color-bg-subtle)" : "var(--color-bg)",
    border: isInline ? "none" : "1px solid var(--color-border)",
    borderRadius: "6px",     // radius.md
    overflow: "hidden",
  };

  const iconStyle: CSSProperties = {
    position: "absolute",
    left: "10px",
    color: "var(--color-text-tertiary)",
    fontSize: "14px",        // font.size.base
    pointerEvents: "none",
    display: "flex",
    alignItems: "center",
    lineHeight: 1,
    top: "50%",
    transform: "translateY(-50%)",
  };

  const inputStyle: CSSProperties = {
    width: "100%",
    border: "none",
    outline: "none",
    background: "transparent",
    // TODO(token): 2px vertical padding not in spacing scale — Issue #TODO
    padding: isInline ? "4px 8px 4px 30px" : "7px 32px 7px 30px",
    fontSize: "13px",        // font.size.sm2
    fontFamily: "var(--font-sans)",
    color: disabled ? "var(--color-text-tertiary)" : "var(--color-text-primary)",
    cursor: disabled ? "not-allowed" : "text",
  };

  const clearButtonStyle: CSSProperties = {
    position: "absolute",
    right: "6px",
    top: "50%",
    transform: "translateY(-50%)",
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--color-text-tertiary)",
    fontSize: "14px",
    display: "flex",
    alignItems: "center",
    padding: "2px",
    borderRadius: "4px",
    lineHeight: 1,
  };

  function handleClear() {
    /** Clears the value and returns focus to the input. */
    onChange("");
    inputRef.current?.focus();
  }

  return (
    <div style={containerStyle}>
      {/* Magnifying glass icon */}
      <span aria-hidden="true" style={iconStyle}>⌕</span>

      <input
        ref={inputRef}
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autoFocus}
        style={inputStyle}
      />

      {value && !disabled && (
        <button
          type="button"
          onClick={handleClear}
          aria-label="Suche löschen"
          style={clearButtonStyle}
        >
          ✕
        </button>
      )}
    </div>
  );
}
