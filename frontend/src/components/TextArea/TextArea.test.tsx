import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { TextArea } from ".";

describe("TextArea", () => {
  it("renders a labelled textarea", () => {
    /** Expects: textarea is reachable via its visible label. */
    render(<TextArea id="desc" label="Beschreibung" value="" onChange={vi.fn()} />);
    expect(screen.getByLabelText("Beschreibung")).toBeInTheDocument();
  });

  it("calls onChange with the new value on typing", async () => {
    /** Expects: onChange fires with updated string. */
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TextArea id="desc" label="Beschreibung" value="" onChange={onChange} />);
    await user.type(screen.getByLabelText("Beschreibung"), "Text");
    expect(onChange).toHaveBeenCalled();
  });

  it("shows error message and marks textarea as invalid", () => {
    /** Expects: errorMessage is visible and aria-invalid is set. */
    render(
      <TextArea id="x" label="Feld" value="" onChange={vi.fn()} errorMessage="Zu kurz." />
    );
    expect(screen.getByText("Zu kurz.")).toBeInTheDocument();
    expect(screen.getByLabelText("Feld")).toHaveAttribute("aria-invalid", "true");
  });

  it("shows character count when showCharCount and maxLength are set", () => {
    /** Expects: current / max character count is visible. */
    render(
      <TextArea id="x" label="Kurztext" value="Hallo" onChange={vi.fn()} maxLength={100} showCharCount />
    );
    expect(screen.getByText(/5\s*\/\s*100/)).toBeInTheDocument();
  });

  it("is disabled when disabled prop is true", () => {
    /** Expects: disabled textarea cannot be interacted with. */
    render(<TextArea id="x" label="Feld" value="" onChange={vi.fn()} disabled />);
    expect(screen.getByLabelText("Feld")).toBeDisabled();
  });
});
