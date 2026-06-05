// Colour constants for EpistemicStatus badges
const BADGE = {
  incomplete: { bg: "var(--color-amber-bg)", text: "var(--color-amber-text)" },
  axiomatic: { bg: "var(--color-green-bg)", text: "var(--color-green-text)" },
} as const;

export function EpistemicBadge({ status }: { status: string }) {
  /** Renders the epistemic status of a causal model slot or relation as a colour-coded pill badge. */
  const style = status === "axiomatic" ? BADGE.axiomatic : BADGE.incomplete;
  return (
    <span
      style={{
        fontSize: "11px", // font.size.xs
        background: style.bg,
        color: style.text,
        padding: "2px 8px", // TODO(token): 2px vertical padding not in spacing scale
        borderRadius: "9999px", // radius.full — pill shape
        fontWeight: "500", // font.weight.medium
      }}
    >
      {/* TODO(i18n): status values should be translated via t('status.epistemic.{status}') */}
      {status}
    </span>
  );
}
