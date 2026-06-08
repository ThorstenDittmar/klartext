import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Badge } from ".";

describe("Badge", () => {
  it("renders the label text", () => {
    /** Expects: Badge displays its label as visible text. */
    render(<Badge label="Entwurf" />);
    expect(screen.getByText("Entwurf")).toBeInTheDocument();
  });

  it("is not interactive — no button role", () => {
    /** Expects: Badge is a read-only element, not a button or link. */
    render(<Badge label="Abgeschlossen" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  it("renders all color keys without crashing", () => {
    /** Expects: each colorKey renders a valid span with the label. */
    const colorKeys = ["default", "green", "amber", "red", "blue", "teal"] as const;
    for (const colorKey of colorKeys) {
      const { unmount } = render(<Badge label={colorKey} colorKey={colorKey} />);
      expect(screen.getByText(colorKey)).toBeInTheDocument();
      unmount();
    }
  });

  it("renders all variants without crashing", () => {
    /** Expects: each variant renders a valid span. */
    const variants = ["status", "category", "outline"] as const;
    for (const variant of variants) {
      const { unmount } = render(<Badge label="Test" variant={variant} />);
      expect(screen.getByText("Test")).toBeInTheDocument();
      unmount();
    }
  });

  it("outline variant has no fill background", () => {
    /** Expects: outline variant uses transparent background. */
    render(<Badge label="Outline" colorKey="blue" variant="outline" />);
    expect(screen.getByText("Outline")).toHaveStyle({ background: "transparent" });
  });
});
