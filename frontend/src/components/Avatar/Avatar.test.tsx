import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Avatar } from ".";

describe("Avatar", () => {
  it("renders an image when imageUrl is provided", () => {
    /** Expects: img element with the name as alt text. */
    render(<Avatar name="Anna Bauer" imageUrl="https://example.com/avatar.jpg" />);
    expect(screen.getByRole("img", { name: "Anna Bauer" })).toBeInTheDocument();
  });

  it("shows initials when no imageUrl is given but name is provided", () => {
    /** Expects: first letters of first and last name are displayed. */
    render(<Avatar name="Anna Bauer" />);
    expect(screen.getByText("AB")).toBeInTheDocument();
  });

  it("shows single initial for single-word name", () => {
    /** Expects: one-word name produces a single-character initial. */
    render(<Avatar name="Thorsten" />);
    expect(screen.getByText("T")).toBeInTheDocument();
  });

  it("renders placeholder when neither name nor imageUrl is given", () => {
    /** Expects: a decorative placeholder icon renders, with aria-hidden. */
    const { container } = render(<Avatar />);
    const element = container.firstChild as HTMLElement;
    expect(element).toBeInTheDocument();
    expect(element.getAttribute("aria-hidden")).toBe("true");
  });

  it("applies the correct size class", () => {
    /** Expects: size prop controls the rendered dimensions. */
    const sizes = { xs: "20px", sm: "24px", md: "32px", lg: "48px" } as const;
    for (const [size, px] of Object.entries(sizes)) {
      const { container, unmount } = render(<Avatar name="AB" size={size as keyof typeof sizes} />);
      const el = container.firstChild as HTMLElement;
      expect(el.style.width).toBe(px);
      unmount();
    }
  });

  it("renders same initial colour for same name", () => {
    /** Expects: deterministic color — same name always produces same background. */
    const { container: a } = render(<Avatar name="Anna Bauer" />);
    const { container: b } = render(<Avatar name="Anna Bauer" />);
    const bgA = (a.firstChild as HTMLElement).style.background;
    const bgB = (b.firstChild as HTMLElement).style.background;
    expect(bgA).toBe(bgB);
  });
});
