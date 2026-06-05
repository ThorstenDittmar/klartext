import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import WirkgefuegeVorschlag from "./WirkgefuegeVorschlag";
import type { SuggestWirkgefuegeResponse } from "../lib/api";

vi.mock("../lib/api", () => ({
  api: {
    causalModels: {
      create: vi.fn().mockResolvedValue({ id: "cm1", title: "Test Modell", status: "draft", axioms: [], slots: [], relations: [] }),
      addSlot: vi.fn().mockResolvedValue({ id: "s1", identifier: "co2_emissionen", slot_type: "physical_quantity", epistemic_status: "incomplete" }),
      addRelation: vi.fn().mockResolvedValue({ id: "r1", identifier: "co2_to_global", source_slot_id: "s1", target_slot_id: "s2", mechanism: null, polarity: null, epistemic_status: "incomplete" }),
      updateRelation: vi.fn().mockResolvedValue({}),
    },
    narratives: {
      linkToCausalModel: vi.fn().mockResolvedValue({}),
    },
    claims: {
      linkToWirkgefuege: vi.fn().mockResolvedValue(undefined),
    },
  },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockSuggestion: SuggestWirkgefuegeResponse = {
  suggested_slots: [
    { identifier: "co2_emissionen", slot_type: "physical_quantity" },
    { identifier: "global_temperatur", slot_type: "physical_quantity" },
  ],
  suggested_relations: [
    {
      source: "co2_emissionen",
      target: "global_temperatur",
      source_condition: "hoch",
      target_effect: "steigend",
      mechanism: "Treibhauseffekt",
      epistemic_status: "incomplete",
    },
  ],
  from_claims: ["claim-1"],
};

function renderWithState(suggestion: SuggestWirkgefuegeResponse | null) {
  return render(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/narrative/test-id/wirkgefuege-vorschlag",
          state: suggestion
            ? { suggestion, narrative: { id: "test-id", title: "Test Narrativ" } }
            : null,
        },
      ]}
    >
      <Routes>
        <Route
          path="/narrative/:narrativeId/wirkgefuege-vorschlag"
          element={<WirkgefuegeVorschlag />}
        />
      </Routes>
    </MemoryRouter>
  );
}

describe("WirkgefuegeVorschlag", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("shows error state when suggestion is not in location state", () => {
    renderWithState(null);
    expect(
      screen.getByText(/Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten/i)
    ).toBeInTheDocument();
  });

  it("renders slot identifiers as input values", () => {
    renderWithState(mockSuggestion);
    expect(screen.getByDisplayValue("co2_emissionen")).toBeInTheDocument();
    expect(screen.getByDisplayValue("global_temperatur")).toBeInTheDocument();
  });

  it("renders relation source → target text", () => {
    renderWithState(mockSuggestion);
    expect(screen.getByText(/co2_emissionen → global_temperatur/)).toBeInTheDocument();
  });

  it("save button is disabled when model name is empty", () => {
    renderWithState(mockSuggestion);
    const btn = screen.getByText(/CausalModel anlegen und speichern/i);
    expect(btn).toBeDisabled();
  });

  it("navigates to /causal-model after successful save", async () => {
    renderWithState(mockSuggestion);
    const input = screen.getByPlaceholderText(/Modellname eingeben/i);
    fireEvent.change(input, { target: { value: "Mein Modell" } });
    const btn = screen.getByText(/CausalModel anlegen und speichern/i);
    fireEvent.click(btn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/causal-model/cm1");
    });
  });
});
