import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import CausalModelEditor from "./CausalModelEditor";

vi.mock("../lib/api", () => ({
  api: {
    causalModels: {
      list: vi.fn().mockResolvedValue([
        { id: "cm1", title: "Test Modell", status: "draft", axioms: [], slots: [], relations: [] },
      ]),
      get: vi.fn().mockResolvedValue({
        id: "cm1",
        title: "Test Modell",
        status: "draft",
        axioms: [],
        slots: [
          { id: "s1", identifier: "co2_emissionen", slot_type: "physical_quantity", epistemic_status: "incomplete" },
        ],
        relations: [
          {
            id: "r1",
            identifier: "co2_to_temp",
            source_slot_id: "s1",
            target_slot_id: "s2",
            mechanism: "Treibhauseffekt",
            polarity: null,
            epistemic_status: "incomplete",
          },
        ],
      }),
    },
    narratives: {
      list: vi.fn().mockResolvedValue([
        { id: "n1", title: "Klartext Narrativ", causal_model_id: "cm1" },
        { id: "n2", title: "Anderes Narrativ", causal_model_id: null },
      ]),
    },
  },
}));

function renderWithSelectedModel(selectedModelId?: string) {
  return render(
    <MemoryRouter
      initialEntries={[
        { pathname: "/causal-model", state: selectedModelId ? { selectedModelId } : null },
      ]}
    >
      <Routes>
        <Route path="/causal-model" element={<CausalModelEditor />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("CausalModelEditor — extensions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("auto-selects model from location state and shows its title as heading", async () => {
    renderWithSelectedModel("cm1");
    expect(await screen.findByRole("heading", { name: "Test Modell" })).toBeInTheDocument();
  });

  it("shows Slots section with slot identifier", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("co2_emissionen")).toBeInTheDocument();
    });
  });

  it("shows Kausalrelationen section with relation identifier", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("co2_to_temp")).toBeInTheDocument();
    });
  });

  it("shows Verknüpfte Narrative section with linked narrative", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("Klartext Narrativ")).toBeInTheDocument();
    });
  });

  it("does not show unlinked narratives in Verknüpfte Narrative", async () => {
    renderWithSelectedModel("cm1");
    await waitFor(() => {
      expect(screen.getByText("Klartext Narrativ")).toBeInTheDocument();
    });
    expect(screen.queryByText("Anderes Narrativ")).not.toBeInTheDocument();
  });
});
