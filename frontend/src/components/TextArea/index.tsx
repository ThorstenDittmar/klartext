import { useEffect, useRef, type CSSProperties } from "react";

// Spec: design/components/text-area.md

export interface TextAreaProps {
  id: string;
  /** Visible label. Pass pre-translated string via t('key'). */
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  helperText?: string;
  errorMessage?: string | null;
  /** Initial visible row count. Default: 4. */
  rows?: number;
  maxLength?: number;
  /** Show "{current} / {maxLength}" counter below the textarea. */
  showCharCount?: boolean;
  /** Textarea grows with content — disables manual resize. */
  autoResize?: boolean;
  disabled?: boolean;
}

/** Labelled multiline text input for descriptions, notes and free-form content.
 *  For single-line input use TextInput. */
export function TextArea({
  id,
  label,
  value,
  onChange,
  placeholder,
  helperText,
  errorMessage,
  rows = 4,
  maxLength,
  showCharCount = false,
  autoResize = false,
  disabled = false,
}: TextAreaProps) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const hasError = !!errorMessage;
  const descId = helperText || hasError || showCharCount ? `${id}-desc` : undefined;

  useEffect(() => {
    /** Adjusts textarea height when autoResize is active. */
    if (autoResize && ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = `${ref.current.scrollHeight}px`;
    }
  }, [value, autoResize]);

  const labelStyle: CSSProperties = {
    display: "block",
    fontSize: "12px",
    fontWeight: "500",
    color: "var(--color-text-secondary)",
    fontFamily: "var(--font-sans)",
    marginBottom: "6px",
  };

  const textareaStyle: CSSProperties = {
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
    resize: autoResize ? "none" : "vertical",
    cursor: disabled ? "not-allowed" : "text",
    lineHeight: "1.5",
    minHeight: `${rows * 1.5 * 14 + 16}px`,  // rows × lineHeight × fontSize + padding
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <label htmlFor={id} style={labelStyle}>
        {label}
      </label>

      <textarea
        ref={ref}
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        maxLength={maxLength}
        aria-invalid={hasError || undefined}
        aria-describedby={descId}
        style={textareaStyle}
      />

      <div
        id={descId}
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: "4px",
        }}
      >
        {(hasError || helperText) && (
          <span
            role={hasError ? "alert" : undefined}
            style={{
              fontSize: "12px",
              fontFamily: "var(--font-sans)",
              color: hasError ? "var(--color-red-text)" : "var(--color-text-tertiary)",
              lineHeight: "1.4",
            }}
          >
            {hasError ? errorMessage : helperText}
          </span>
        )}

        {showCharCount && maxLength && (
          <span
            style={{
              fontSize: "12px",
              fontFamily: "var(--font-sans)",
              color: "var(--color-text-tertiary)",
              marginLeft: "auto",
            }}
          >
            {value.length} / {maxLength}
          </span>
        )}
      </div>
    </div>
  );
}
