import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { WordCountLabel } from ".";

describe("WordCountLabel", () => {
  it("displays the word count with default suffix", () => {
    /** Expects: count is shown as 'N Wörter' with the German suffix by default. */
    render(<WordCountLabel count={42} />);
    expect(screen.getByText("42 Wörter")).toBeInTheDocument();
  });

  it("formats large counts with locale separators", () => {
    /** Expects: 1240 is displayed as '1.240 Wörter' (German locale). */
    render(<WordCountLabel count={1240} />);
    expect(screen.getByText("1.240 Wörter")).toBeInTheDocument();
  });

  it("displays zero count", () => {
    /** Expects: count of 0 renders as '0 Wörter', not empty. */
    render(<WordCountLabel count={0} />);
    expect(screen.getByText("0 Wörter")).toBeInTheDocument();
  });

  it("accepts a custom suffix", () => {
    /** Expects: a custom suffix replaces the default 'Wörter'. */
    render(<WordCountLabel count={5} suffix="words" />);
    expect(screen.getByText("5 words")).toBeInTheDocument();
  });
});
