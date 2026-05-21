import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App";

// Supabase client requires env vars – stub them for tests
vi.mock("./lib/supabase", () => ({
  supabase: {
    auth: { getSession: vi.fn().mockResolvedValue({ data: { session: null } }) },
  },
}));

describe("App routing", () => {
  it("renders Login screen at /", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /login/i })).toBeInTheDocument();
  });
});
