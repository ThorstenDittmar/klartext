import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { SearchInput } from ".";

describe("SearchInput", () => {
  it("renders with a search role", () => {
    /** Expects: input has type=search for semantic correctness. */
    render(<SearchInput value="" onChange={vi.fn()} />);
    expect(screen.getByRole("searchbox")).toBeInTheDocument();
  });

  it("shows placeholder text", () => {
    /** Expects: placeholder is visible when value is empty. */
    render(<SearchInput value="" onChange={vi.fn()} placeholder="Szene suchen…" />);
    expect(screen.getByPlaceholderText("Szene suchen…")).toBeInTheDocument();
  });

  it("calls onChange with the new value on input", async () => {
    /** Expects: typing triggers onChange with the updated string. */
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<SearchInput value="" onChange={onChange} />);
    await user.type(screen.getByRole("searchbox"), "Held");
    expect(onChange).toHaveBeenCalled();
    expect(onChange).toHaveBeenCalledWith(expect.stringContaining("H"));
  });

  it("does not show clear button when value is empty", () => {
    /** Expects: no clear button when there is no text to clear. */
    render(<SearchInput value="" onChange={vi.fn()} />);
    expect(screen.queryByRole("button", { name: /löschen/i })).not.toBeInTheDocument();
  });

  it("shows clear button when value is not empty", () => {
    /** Expects: a clear button appears when the search field has a value. */
    render(<SearchInput value="Held" onChange={vi.fn()} />);
    expect(screen.getByRole("button", { name: /löschen/i })).toBeInTheDocument();
  });

  it("calls onChange with empty string when clear button is clicked", async () => {
    /** Expects: clicking the clear button resets the value to an empty string. */
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<SearchInput value="Held" onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: /löschen/i }));
    expect(onChange).toHaveBeenCalledWith("");
  });

  it("is disabled when disabled prop is true", () => {
    /** Expects: disabled SearchInput cannot be interacted with. */
    render(<SearchInput value="" onChange={vi.fn()} disabled />);
    expect(screen.getByRole("searchbox")).toBeDisabled();
  });
});
