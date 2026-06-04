import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App";
import { Routes, Route } from "react-router-dom";
import { MemoryRouter } from "react-router-dom";
import NarrativeAnalyse from "./pages/NarrativeAnalyse";
import WirkgefuegeVorschlag from "./pages/WirkgefuegeVorschlag";

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

describe("App routing — new screens", () => {
  it("renders NarrativeAnalyse for /narrative/:id/analyse route", () => {
    render(
      <MemoryRouter initialEntries={["/narrative/test-id/analyse"]}>
        <Routes>
          <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
        </Routes>
      </MemoryRouter>
    );
    expect(
      screen.getByText(/Bitte Analyse vom Narrativ-Editor starten/i)
    ).toBeInTheDocument();
  });

  it("renders WirkgefuegeVorschlag for /narrative/:id/wirkgefuege-vorschlag route", () => {
    render(
      <MemoryRouter initialEntries={["/narrative/test-id/wirkgefuege-vorschlag"]}>
        <Routes>
          <Route
            path="/narrative/:narrativeId/wirkgefuege-vorschlag"
            element={<WirkgefuegeVorschlag />}
          />
        </Routes>
      </MemoryRouter>
    );
    expect(
      screen.getByText(/Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten/i)
    ).toBeInTheDocument();
  });
});
