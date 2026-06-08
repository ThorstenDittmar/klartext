import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { BottomBar } from ".";

describe("BottomBar", () => {
  it("renders word count", () => {
    /** Expects: the word count label is visible. */
    render(<BottomBar wordCount={42} saveStatus="saved" />);
    expect(screen.getByText("42 Wörter")).toBeInTheDocument();
  });

  it("renders autosave indicator", () => {
    /** Expects: the autosave status indicator is visible. */
    render(<BottomBar wordCount={0} saveStatus="saving" />);
    expect(screen.getByText("Speichert…")).toBeInTheDocument();
  });

  it("shows saved status when saveStatus is saved", () => {
    /** Expects: 'saved' status renders saved confirmation text. */
    render(<BottomBar wordCount={100} saveStatus="saved" />);
    expect(screen.getByText("Gespeichert ✓")).toBeInTheDocument();
  });

  it("shows unsaved status when saveStatus is unsaved", () => {
    /** Expects: 'unsaved' status renders warning text. */
    render(<BottomBar wordCount={50} saveStatus="unsaved" />);
    expect(screen.getByText("Nicht gespeichert ⚠")).toBeInTheDocument();
  });

  it("renders as a footer element", () => {
    /** Expects: uses semantic <footer> element for accessibility. */
    const { container } = render(<BottomBar wordCount={0} saveStatus="saved" />);
    expect(container.querySelector("footer")).toBeInTheDocument();
  });
});
