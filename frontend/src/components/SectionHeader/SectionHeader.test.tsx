import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { SectionHeader } from ".";

describe("SectionHeader", () => {
  it("renders the title", () => {
    /** Expects: title text is visible. */
    render(<SectionHeader title="Szenen" onToggle={vi.fn()} />);
    expect(screen.getByText("Szenen")).toBeInTheDocument();
  });

  it("shows count badge when count is provided", () => {
    /** Expects: count appears next to the title. */
    render(<SectionHeader title="Szenen" count={12} onToggle={vi.fn()} />);
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("does not show count when count is null", () => {
    /** Expects: no count element when count prop is omitted. */
    render(<SectionHeader title="Szenen" onToggle={vi.fn()} />);
    // No digit next to the title
    expect(screen.queryByLabelText(/szenen/i)).not.toBeInTheDocument();
  });

  it("calls onToggle when the header is clicked", async () => {
    /** Expects: clicking the header fires onToggle. */
    const user = userEvent.setup();
    const onToggle = vi.fn();
    render(<SectionHeader title="Szenen" onToggle={onToggle} />);
    await user.click(screen.getByRole("button", { name: /szenen/i }));
    expect(onToggle).toHaveBeenCalledOnce();
  });

  it("shows add button when onAdd is provided", () => {
    /** Expects: a '+' action button appears when onAdd is set. */
    render(<SectionHeader title="Szenen" onToggle={vi.fn()} onAdd={vi.fn()} />);
    expect(screen.getByRole("button", { name: /hinzufügen/i })).toBeInTheDocument();
  });

  it("calls onAdd when the add button is clicked without triggering toggle", async () => {
    /** Expects: add button click fires onAdd and does not fire onToggle. */
    const user = userEvent.setup();
    const onToggle = vi.fn();
    const onAdd = vi.fn();
    render(<SectionHeader title="Szenen" onToggle={onToggle} onAdd={onAdd} />);
    await user.click(screen.getByRole("button", { name: /hinzufügen/i }));
    expect(onAdd).toHaveBeenCalledOnce();
    expect(onToggle).not.toHaveBeenCalled();
  });

  it("sets aria-expanded correctly", () => {
    /** Expects: aria-expanded reflects the isCollapsed prop. */
    const { rerender } = render(
      <SectionHeader title="Szenen" onToggle={vi.fn()} isCollapsed={false} />
    );
    expect(screen.getByRole("button", { name: /szenen/i })).toHaveAttribute("aria-expanded", "true");

    rerender(<SectionHeader title="Szenen" onToggle={vi.fn()} isCollapsed={true} />);
    expect(screen.getByRole("button", { name: /szenen/i })).toHaveAttribute("aria-expanded", "false");
  });

  it("does not render toggle button when isCollapsible is false", () => {
    /** Expects: static variant is not a button — just a heading. */
    render(<SectionHeader title="Szenen" onToggle={vi.fn()} isCollapsible={false} />);
    expect(screen.queryByRole("button", { name: /szenen/i })).not.toBeInTheDocument();
    expect(screen.getByText("Szenen")).toBeInTheDocument();
  });
});
