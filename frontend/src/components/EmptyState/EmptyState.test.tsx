import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { EmptyState } from ".";

describe("EmptyState", () => {
  it("renders title", () => {
    /** Expects: title is visible. */
    render(<EmptyState title="Keine Szenen vorhanden" />);
    expect(screen.getByText("Keine Szenen vorhanden")).toBeInTheDocument();
  });

  it("renders subtitle when provided", () => {
    /** Expects: subtitle appears below the title. */
    render(<EmptyState title="Leer" subtitle="Leg eine Szene an um zu beginnen." />);
    expect(screen.getByText("Leg eine Szene an um zu beginnen.")).toBeInTheDocument();
  });

  it("does not render subtitle when not provided", () => {
    /** Expects: no subtitle element when subtitle prop is omitted. */
    const { container } = render(<EmptyState title="Leer" />);
    expect(container.querySelectorAll("p").length).toBe(0);
  });

  it("renders an action button when actionLabel and onAction are provided", () => {
    /** Expects: a clickable button with the actionLabel text. */
    render(
      <EmptyState
        title="Leer"
        actionLabel="Szene erstellen"
        onAction={vi.fn()}
      />
    );
    expect(screen.getByRole("button", { name: "Szene erstellen" })).toBeInTheDocument();
  });

  it("does not render an action button when actionLabel is omitted", () => {
    /** Expects: no button when actionLabel is not provided. */
    render(<EmptyState title="Leer" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("calls onAction when the button is clicked", async () => {
    /** Expects: onAction fires once on button click. */
    const user = userEvent.setup();
    const onAction = vi.fn();
    render(
      <EmptyState title="Leer" actionLabel="Anlegen" onAction={onAction} />
    );
    await user.click(screen.getByRole("button"));
    expect(onAction).toHaveBeenCalledOnce();
  });
});
