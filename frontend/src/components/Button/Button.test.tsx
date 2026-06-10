import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Button } from ".";

describe("Button", () => {
  it("renders children as accessible button", () => {
    /** Expects: a native <button> element with the given label. */
    render(<Button>Speichern</Button>);
    expect(screen.getByRole("button", { name: "Speichern" })).toBeInTheDocument();
  });

  it("calls onClick when clicked", async () => {
    /** Expects: onClick fires exactly once on click. */
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Klick</Button>);
    await user.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("does not call onClick when disabled", async () => {
    /** Expects: disabled button ignores click events. */
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button onClick={onClick} disabled>Gesperrt</Button>);
    await user.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });

  it("does not call onClick when loading", async () => {
    /** Expects: loading button ignores click events. */
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button onClick={onClick} isLoading>Speichern</Button>);
    await user.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });

  it("marks button as busy and disabled during loading", () => {
    /** Expects: isLoading sets disabled and aria-busy=true on the button element. */
    render(<Button isLoading>Speichern</Button>);
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
  });

  it("uses aria-label for icon-only buttons", () => {
    /** Expects: aria-label provides the accessible name when there is no visible text. */
    render(<Button aria-label="Schließen">✕</Button>);
    expect(screen.getByRole("button", { name: "Schließen" })).toBeInTheDocument();
  });

  it("renders all variants without crashing", () => {
    /** Expects: each variant renders a valid button element. */
    const variants = ["primary", "secondary", "ghost", "nav-item"] as const;
    for (const variant of variants) {
      const { unmount } = render(<Button variant={variant}>{variant}</Button>);
      expect(screen.getByRole("button", { name: variant })).toBeInTheDocument();
      unmount();
    }
  });

  it("renders nav-item as active", () => {
    /** Expects: isActive renders the nav-item button (visual state verified in Storybook). */
    render(<Button variant="nav-item" isActive>Szenenplan</Button>);
    expect(screen.getByRole("button", { name: "Szenenplan" })).toBeInTheDocument();
  });

  it("renders full-width when fullWidth is true", () => {
    /** Expects: fullWidth button has width 100% applied. */
    render(<Button fullWidth>Anlegen</Button>);
    const button = screen.getByRole("button");
    expect(button).toHaveStyle({ width: "100%" });
  });
});
