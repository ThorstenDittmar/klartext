import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SceneBreak } from ".";

describe("SceneBreak", () => {
  it("renders the scene title", () => {
    /** Expects: the scene title text is visible. */
    render(<SceneBreak title="Szene 1" />);
    expect(screen.getByText("Szene 1")).toBeInTheDocument();
  });

  it("renders a long title without truncation", () => {
    /** Expects: long titles display fully, not clipped. */
    render(<SceneBreak title="Die Verhandlung im Bundesministerium" />);
    expect(screen.getByText("Die Verhandlung im Bundesministerium")).toBeInTheDocument();
  });

  it("renders two decorative lines", () => {
    /** Expects: two horizontal rule elements flank the title. */
    const { container } = render(<SceneBreak title="Szene" />);
    const lines = container.querySelectorAll("[aria-hidden='true']");
    expect(lines.length).toBeGreaterThanOrEqual(2);
  });
});
