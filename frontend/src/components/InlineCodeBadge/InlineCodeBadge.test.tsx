import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { InlineCodeBadge } from ".";

describe("InlineCodeBadge", () => {
  it("renders the code text", () => {
    /** Expects: content is displayed as visible text inside a <code> element. */
    render(<InlineCodeBadge>ANTHROPIC_API_KEY</InlineCodeBadge>);
    expect(screen.getByText("ANTHROPIC_API_KEY")).toBeInTheDocument();
  });

  it("uses a <code> element for semantic correctness", () => {
    /** Expects: renders using the semantic <code> HTML element. */
    const { container } = render(<InlineCodeBadge>npm install</InlineCodeBadge>);
    expect(container.querySelector("code")).toBeInTheDocument();
  });

  it("does not render a copy button by default", () => {
    /** Expects: no copy button when copyable is false (default). */
    render(<InlineCodeBadge>SOME_KEY</InlineCodeBadge>);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("renders a copy button when copyable is true", () => {
    /** Expects: a copy button appears next to the code text. */
    render(<InlineCodeBadge copyable>SOME_KEY</InlineCodeBadge>);
    expect(screen.getByRole("button", { name: /kopieren/i })).toBeInTheDocument();
  });

  it("copy button writes text to clipboard", async () => {
    /** Expects: clicking copy writes the code content to the clipboard. */
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });
    render(<InlineCodeBadge copyable>MY_SECRET_KEY</InlineCodeBadge>);
    await user.click(screen.getByRole("button", { name: /kopieren/i }));
    expect(writeText).toHaveBeenCalledWith("MY_SECRET_KEY");
  });
});
