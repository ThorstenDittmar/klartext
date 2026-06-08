import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Breadcrumb } from ".";

describe("Breadcrumb", () => {
  it("renders all segment labels", () => {
    /** Expects: every segment's label is visible in the breadcrumb. */
    render(
      <Breadcrumb
        items={[
          { label: "Meine Werke" },
          { label: "Der Aufstand" },
          { label: "Kapitel 1" },
        ]}
      />
    );
    expect(screen.getByText("Meine Werke")).toBeInTheDocument();
    expect(screen.getByText("Der Aufstand")).toBeInTheDocument();
    expect(screen.getByText("Kapitel 1")).toBeInTheDocument();
  });

  it("marks last segment as current page", () => {
    /** Expects: only the last segment has aria-current='page'. */
    render(
      <Breadcrumb
        items={[
          { label: "Meine Werke", onClick: vi.fn() },
          { label: "Kapitel 1" },
        ]}
      />
    );
    expect(screen.getByText("Kapitel 1").closest("[aria-current='page']")).toBeInTheDocument();
    expect(screen.getByText("Meine Werke").closest("[aria-current='page']")).toBeNull();
  });

  it("calls onClick when a non-last segment is clicked", async () => {
    /** Expects: clicking a parent segment triggers its onClick handler. */
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(
      <Breadcrumb
        items={[
          { label: "Meine Werke", onClick: onNavigate },
          { label: "Kapitel 1" },
        ]}
      />
    );
    await user.click(screen.getByRole("button", { name: "Meine Werke" }));
    expect(onNavigate).toHaveBeenCalledOnce();
  });

  it("renders nav element for accessibility", () => {
    /** Expects: wraps the breadcrumb in a <nav> element with appropriate label. */
    const { container } = render(
      <Breadcrumb items={[{ label: "Startseite" }]} />
    );
    expect(container.querySelector("nav")).toBeInTheDocument();
  });

  it("renders a single segment without a separator", () => {
    /** Expects: no separator character when only one segment is shown. */
    render(<Breadcrumb items={[{ label: "Nur-Seite" }]} />);
    expect(screen.queryByText("›")).not.toBeInTheDocument();
  });

  it("renders slash separator when separator='slash' is specified", () => {
    /** Expects: slash separator replaces the default chevron. */
    render(
      <Breadcrumb
        items={[{ label: "A", onClick: vi.fn() }, { label: "B" }]}
        separator="slash"
      />
    );
    expect(screen.getByText("/")).toBeInTheDocument();
    expect(screen.queryByText("›")).not.toBeInTheDocument();
  });
});
