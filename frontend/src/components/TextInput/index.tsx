import type { CSSProperties } from "react";

// Spec: design/components/text-input.md

export interface TextInputProps {
  /** Unique ID — links <label> to <input>. Must be unique on the page. */
  id: string;
  /** Visible label. Pass pre-translated string via t('key'). */
  label: string;
  /** Controlled value. */
  value: string;
  /** Called with the new string on every keystroke. */
  onChange: (value: string) => void;
  placeholder?: string;
  /** Explanatory text shown below the input. */
  helperText?: string;
  /** Validation error — visible + sets aria-invalid. null = no error. */
  errorMessage?: string | null;
  disabled?: boolean;
  readOnly?: boolean;
  maxLength?: number;
  type?: "text" | "email" | "password" | "url";
}

/** Labelled single-line text input for form fields.
 *  Validation lives outside this component — pass errorMessage from the caller. */
export function TextInput({
  id,
  label,
  value,
  onChange,
  placeholder,
  helperText,
  errorMessage,
  disabled = false,
  readOnly = false,
  maxLength,
  type = "text",
}: TextInputProps) {
  const hasError = !!errorMessage;
  const descId = helperText || hasError ? `${id}-desc` : undefined;

  const labelStyle: CSSProperties = {
    display: "block",
    fontSize: "12px",        // font.size.sm
    fontWeight: "500",       // font.weight.medium
    color: "var(--color-text-secondary)",
    fontFamily: "var(--font-sans)",
    marginBottom: "6px",     // spacing.xs + 2px
  };

  const inputStyle: CSSProperties = {
    display: "block",
    width: "100%",
    boxSizing: "border-box",
    padding: "8px 10px",     // spacing.sm / TODO(token): 10px not in scale
    fontSize: "14px",        // font.size.base
    fontFamily: "var(--font-sans)",
    color: disabled ? "var(--color-text-tertiary)" : "var(--color-text-primary)",
    background: disabled ? "var(--color-bg-subtle)" : "var(--color-bg)",
    border: hasError
      ? "1px solid var(--color-red-text)"
      : "1px solid var(--color-border)",
    borderRadius: "6px",     // radius.md
    outline: "none",
    cursor: disabled ? "not-allowed" : readOnly ? "default" : "text",
    lineHeight: "1.5",
  };

  const subTextBase: CSSProperties = {
    display: "block",
    marginTop: "4px",        // spacing.xs
    fontSize: "12px",        // font.size.sm
    fontFamily: "var(--font-sans)",
    lineHeight: "1.4",
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <label htmlFor={id} style={labelStyle}>
        {label}
      </label>

      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        readOnly={readOnly}
        maxLength={maxLength}
        aria-invalid={hasError || undefined}
        aria-describedby={descId}
        style={inputStyle}
      />

      {(helperText || hasError) && (
        <span
          id={descId}
          role={hasError ? "alert" : undefined}
          style={{
            ...subTextBase,
            color: hasError ? "var(--color-red-text)" : "var(--color-text-tertiary)",
          }}
        >
          {hasError ? errorMessage : helperText}
        </span>
      )}
    </div>
  );
}
