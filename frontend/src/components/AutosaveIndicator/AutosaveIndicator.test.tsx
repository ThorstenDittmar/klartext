import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AutosaveIndicator } from ".";

describe("AutosaveIndicator", () => {
  it("shows saved label when status is saved", () => {
    /** Expects: 'saved' status renders the default saved label. */
    render(<AutosaveIndicator status="saved" />);
    expect(screen.getByText("Gespeichert ✓")).toBeInTheDocument();
  });

  it("shows saving label when status is saving", () => {
    /** Expects: 'saving' status renders the default saving label. */
    render(<AutosaveIndicator status="saving" />);
    expect(screen.getByText("Speichert…")).toBeInTheDocument();
  });

  it("shows unsaved label when status is unsaved", () => {
    /** Expects: 'unsaved' status renders the default unsaved label. */
    render(<AutosaveIndicator status="unsaved" />);
    expect(screen.getByText("Nicht gespeichert ⚠")).toBeInTheDocument();
  });

  it("accepts custom labels", () => {
    /** Expects: custom labels override the defaults. */
    render(<AutosaveIndicator status="saved" savedLabel="Saved" />);
    expect(screen.getByText("Saved")).toBeInTheDocument();
  });

  it("has aria-live polite for screen reader announcements", () => {
    /** Expects: status region is announced by screen readers on change. */
    const { container } = render(<AutosaveIndicator status="saving" />);
    expect(container.firstChild).toHaveAttribute("aria-live", "polite");
  });
});
