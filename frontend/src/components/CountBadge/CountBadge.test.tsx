import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { CountBadge } from ".";

describe("CountBadge", () => {
  it("renders the count as text", () => {
    /** Expects: count is displayed as visible text. */
    render(<CountBadge count={5} />);
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("is hidden by default when count is zero", () => {
    /** Expects: count=0 renders nothing when hideWhenZero is true (default). */
    const { container } = render(<CountBadge count={0} />);
    expect(container.firstChild).toBeNull();
  });

  it("shows zero when hideWhenZero is false", () => {
    /** Expects: count=0 is displayed when hideWhenZero is explicitly false. */
    render(<CountBadge count={0} hideWhenZero={false} />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("caps display at max and shows + suffix", () => {
    /** Expects: count above max shows '{max}+' instead of the exact number. */
    render(<CountBadge count={150} max={99} />);
    expect(screen.getByText("99+")).toBeInTheDocument();
  });

  it("shows exact number when at or below max", () => {
    /** Expects: count=42 with max=99 renders '42'. */
    render(<CountBadge count={42} max={99} />);
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("dot variant renders without the count text", () => {
    /** Expects: dot variant renders a dot indicator, not the number. */
    render(<CountBadge count={5} variant="dot" />);
    expect(screen.queryByText("5")).not.toBeInTheDocument();
  });

  it("has accessible label describing the count", () => {
    /** Expects: inline variant has aria-label for screen readers. */
    render(<CountBadge count={3} aria-label="3 Szenen" />);
    expect(screen.getByLabelText("3 Szenen")).toBeInTheDocument();
  });
});
