import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import NarrativeEditor from "./NarrativeEditor";

// Mock the entire api module
vi.mock("../lib/api", () => ({
  api: {
    narratives: {
      list: vi.fn().mockResolvedValue([
        { id: "n1", title: "Test Narrativ", causal_model_id: null },
      ]),
      get: vi.fn().mockResolvedValue({
        id: "n1",
        title: "Test Narrativ",
        causal_model_id: null,
        scenes: [{ id: "s1", title: "Szene 1", text: "Text.", position: 1 }],
        actors: [],
      }),
      analyse: vi.fn().mockResolvedValue({
        actors: [],
        claims: [],
      }),
    },
    causalModels: {
      list: vi.fn().mockResolvedValue([]),
    },
  },
}));

// Mock react-router-dom's useNavigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderEditor() {
  return render(
    <MemoryRouter>
      <NarrativeEditor />
    </MemoryRouter>
  );
}

describe("NarrativeEditor — Analysieren button", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("shows Analysieren button when a narrative is selected", async () => {
    renderEditor();

    // Wait for narrative list to load and click it
    const btn = await screen.findByText("Test Narrativ");
    fireEvent.click(btn);

    // Button should appear
    expect(await screen.findByText(/Analysieren/i)).toBeInTheDocument();
  });

  it("navigates to analyse screen after successful analysis", async () => {
    renderEditor();

    const narrativeBtn = await screen.findByText("Test Narrativ");
    fireEvent.click(narrativeBtn);

    const analyseBtn = await screen.findByText(/Analysieren/i);
    fireEvent.click(analyseBtn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        "/narrative/n1/analyse",
        expect.objectContaining({ state: expect.objectContaining({ narrative: { id: "n1", title: "Test Narrativ" } }) })
      );
    });
  });
});
