import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import NarrativeDetail from "./NarrativeDetail";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("../lib/api", () => ({
  api: {
    narratives: {
      get: vi.fn().mockResolvedValue({
        id: "n1",
        title: "Test Narrativ",
        causal_model_id: null,
        scenes: [
          { id: "s1", title: "Szene 1", text: "Szenentext.", position: 1 },
        ],
        actors: [
          { id: "a1", label: "Max Mustermann", actor_type: "individual", notes: null, entity_ref: null },
        ],
      }),
      getClaims: vi.fn().mockResolvedValue([
        {
          id: "c1",
          label: "Geldmenge treibt Inflation",
          text: "Die Geldmenge hat Einfluss auf die Inflation.",
          typ: "causal",
          confidence: 0.9,
          status: "draft",
          wirkgefuege_ref: null,
        },
      ]),
      analyse: vi.fn().mockResolvedValue({ actors: [], claims: [] }),
    },
  },
}));

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/narrative/n1"]}>
      <Routes>
        <Route path="/narrative/:narrativeId" element={<NarrativeDetail />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("NarrativeDetail", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("renders narrative title and scene", async () => {
    renderPage();
    expect(await screen.findByText("Test Narrativ")).toBeInTheDocument();
    expect(screen.getByText("Szene 1")).toBeInTheDocument();
  });

  it("renders actor", async () => {
    renderPage();
    expect(await screen.findByText(/Max Mustermann/)).toBeInTheDocument();
  });

  it("renders claim with label and status", async () => {
    renderPage();
    expect(await screen.findByText("Geldmenge treibt Inflation")).toBeInTheDocument();
    expect(screen.getByText("Entwurf")).toBeInTheDocument();
  });

  it("shows Analysieren button and navigates after click", async () => {
    renderPage();
    await screen.findByText("Test Narrativ"); // wait for load

    const btn = screen.getByRole("button", { name: /Analysieren/i });
    fireEvent.click(btn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        "/narrative/n1/analyse",
        expect.objectContaining({ state: expect.objectContaining({ narrative: { id: "n1", title: "Test Narrativ" } }) })
      );
    });
  });
});
