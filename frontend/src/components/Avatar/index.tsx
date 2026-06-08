import { useState, type CSSProperties } from "react";

// Spec: design/components/avatar.md

export type AvatarSize = "xs" | "sm" | "md" | "lg";

export interface AvatarProps {
  /** Full name — used for alt text and initial extraction. */
  name?: string;
  /** Photo URL. Falls back to initials on load error. */
  imageUrl?: string;
  /** Visual size. Default: "md". */
  size?: AvatarSize;
}

const SIZE_PX: Record<AvatarSize, string> = {
  xs: "20px",
  sm: "24px",
  md: "32px",
  lg: "48px",
};

const FONT_SIZE: Record<AvatarSize, string> = {
  xs: "9px",
  sm: "10px",
  md: "13px",  // font.size.sm2
  lg: "18px",  // font.size.xl
};

/** Palette of background colours for initials avatars.
 *  Colour is derived deterministically from the name hash so the same
 *  person always gets the same colour. */
const INITIALS_PALETTE: Array<{ bg: string; text: string }> = [
  { bg: "var(--color-blue-bg)",  text: "var(--color-blue-text)" },
  { bg: "var(--color-teal-bg)",  text: "var(--color-teal-text)" },
  { bg: "var(--color-green-bg)", text: "var(--color-green-text)" },
  { bg: "var(--color-amber-bg)", text: "var(--color-amber-text)" },
  { bg: "var(--color-red-bg)",   text: "var(--color-red-text)" },
];

/** Converts a name string to a stable palette index via a simple hash. */
function paletteIndexFromName(name: string): number {
  let hash = 0;
  for (const char of name) {
    hash = (hash << 5) - hash + char.charCodeAt(0);
    hash |= 0; // convert to 32-bit int
  }
  return Math.abs(hash) % INITIALS_PALETTE.length;
}

/** Extracts up to 2 initials from a full name (first + last word). */
function initialsFromName(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/** Circular avatar — shows photo, generated initials, or a placeholder icon.
 *  Falls back from photo → initials → placeholder automatically. */
export function Avatar({ name, imageUrl, size = "md" }: AvatarProps) {
  const [imgError, setImgError] = useState(false);
  const px = SIZE_PX[size];

  const circleBase: CSSProperties = {
    width: px,
    height: px,
    borderRadius: "9999px",   // radius.full
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    overflow: "hidden",
    fontSize: FONT_SIZE[size],
    fontFamily: "var(--font-sans)",
    fontWeight: "500",         // font.weight.medium
    userSelect: "none",
  };

  // — Image variant —
  if (imageUrl && !imgError) {
    return (
      <img
        src={imageUrl}
        alt={name ?? ""}
        width={px}
        height={px}
        style={{ ...circleBase, objectFit: "cover" }}
        onError={() => setImgError(true)}
      />
    );
  }

  // — Initials variant —
  if (name) {
    const idx = paletteIndexFromName(name);
    const { bg, text } = INITIALS_PALETTE[idx];
    return (
      <span
        role="img"
        aria-label={name}
        style={{ ...circleBase, background: bg, color: text }}
      >
        {initialsFromName(name)}
      </span>
    );
  }

  // — Placeholder variant —
  return (
    <span
      aria-hidden="true"
      style={{
        ...circleBase,
        background: "var(--color-bg-subtle)",
        color: "var(--color-text-tertiary)",
        border: "1px solid var(--color-border)",
        fontSize: FONT_SIZE[size],
      }}
    >
      {/* Generic person silhouette via Unicode */}
      ◯
    </span>
  );
}
