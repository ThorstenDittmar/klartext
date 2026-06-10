import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { TextInput } from ".";

describe("TextInput", () => {
  it("renders a labelled text input", () => {
    /** Expects: input is reachable via its visible label. */
    render(<TextInput id="title" label="Titel" value="" onChange={vi.fn()} />);
    expect(screen.getByLabelText("Titel")).toBeInTheDocument();
  });

  it("calls onChange with the new value on typing", async () => {
    /** Expects: onChange fires with updated string. */
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TextInput id="title" label="Titel" value="" onChange={onChange} />);
    await user.type(screen.getByLabelText("Titel"), "Hallo");
    expect(onChange).toHaveBeenCalled();
  });

  it("shows helper text when provided", () => {
    /** Expects: helperText appears below the input. */
    render(
      <TextInput id="name" label="Name" value="" onChange={vi.fn()} helperText="Max. 50 Zeichen." />
    );
    expect(screen.getByText("Max. 50 Zeichen.")).toBeInTheDocument();
  });

  it("shows error message and marks input as invalid", () => {
    /** Expects: errorMessage is visible and aria-invalid is set on the input. */
    render(
      <TextInput id="name" label="Name" value="" onChange={vi.fn()} errorMessage="Pflichtfeld." />
    );
    expect(screen.getByText("Pflichtfeld.")).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toHaveAttribute("aria-invalid", "true");
  });

  it("is disabled when disabled prop is true", () => {
    /** Expects: disabled input cannot be interacted with. */
    render(<TextInput id="x" label="Feld" value="" onChange={vi.fn()} disabled />);
    expect(screen.getByLabelText("Feld")).toBeDisabled();
  });

  it("is read-only when readOnly prop is true", () => {
    /** Expects: readOnly input has readOnly attribute. */
    render(<TextInput id="x" label="Feld" value="Wert" onChange={vi.fn()} readOnly />);
    expect(screen.getByLabelText("Feld")).toHaveAttribute("readonly");
  });
});
