import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import NarrativeAnalyse from "./NarrativeAnalyse";
import type { AnalyseNarrativeResponse } from "../lib/api";

vi.mock("../lib/api", () => ({
  api: {
    narratives: {
      suggestWirkgefuege: vi.fn().mockResolvedValue({
        suggested_slots: [],
        suggested_relations: [],
        from_claims: [],
      }),
      addActor: vi.fn().mockResolvedValue({ id: "a1", label: "Test", actor_type: "individual", notes: null, entity_ref: null }),
    },
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockAnalysis: AnalyseNarrativeResponse = {
  actors: [
    {
      label: "EZB",
      actor_type: "institution",
      occurrences: [{ scene_title: "Szene 1", start_offset: null, end_offset: null }],
      entity_suggestion: "ecb",
    },
  ],
  claims: [
    {
      label: "Inflation steigt",
      text: "Die Inflation stieg auf 8%.",
      claim_type: "empirical",
      confidence: 0.9,
      wirkgefuege_suggestion: null,
      scene_title: "Szene 1",
      start_offset: null,
      end_offset: null,
    },
  ],
};

function renderWithState(analysis: AnalyseNarrativeResponse | null) {
  return render(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/narrative/test-id/analyse",
          state: analysis
            ? { analysis, narrative: { id: "test-id", title: "Test Narrativ" } }
            : null,
        },
      ]}
    >
      <Routes>
        <Route path="/narrative/:narrativeId/analyse" element={<NarrativeAnalyse />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("NarrativeAnalyse", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("shows error state when analysis is not in location state", () => {
    renderWithState(null);
    expect(
      screen.getByText(/Bitte Analyse vom Narrativ-Editor starten/i)
    ).toBeInTheDocument();
  });

  it("renders actor label and claim label from analysis", () => {
    renderWithState(mockAnalysis);
    expect(screen.getByText("EZB")).toBeInTheDocument();
    expect(screen.getByText("Inflation steigt")).toBeInTheDocument();
  });

  it("Wirkgefüge button is disabled until a claim is accepted", () => {
    renderWithState(mockAnalysis);
    const btn = screen.getByText(/Wirkgefüge-Vorschläge generieren/i);
    expect(btn).toBeDisabled();
  });

  it("Wirkgefüge button becomes enabled after accepting a claim", async () => {
    renderWithState(mockAnalysis);
    // Accept the claim (✓ button for claims section — the last ✓ since actors come first)
    const acceptButtons = screen.getAllByText("✓");
    fireEvent.click(acceptButtons[acceptButtons.length - 1]); // last ✓ = claim
    const btn = screen.getByText(/Wirkgefüge-Vorschläge generieren/i);
    expect(btn).not.toBeDisabled();
  });

  it("navigates to wirkgefuege screen after generating suggestions", async () => {
    renderWithState(mockAnalysis);
    const acceptButtons = screen.getAllByText("✓");
    fireEvent.click(acceptButtons[acceptButtons.length - 1]);
    const btn = screen.getByText(/Wirkgefüge-Vorschläge generieren/i);
    fireEvent.click(btn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        "/narrative/test-id/wirkgefuege-vorschlag",
        expect.anything()
      );
    });
  });

  it("calls addActor API when actor is accepted", async () => {
    const { api } = await import("../lib/api");
    renderWithState(mockAnalysis);

    const acceptButtons = screen.getAllByText("✓");
    fireEvent.click(acceptButtons[0]); // first ✓ = actor

    await waitFor(() => {
      expect(api.narratives.addActor).toHaveBeenCalledWith(
        "test-id",
        "EZB",
        "institution",
        null,
        "ecb",
      );
    });
  });
});
