import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import CausalModelEditor from "./CausalModelEditor";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("../lib/api", () => ({
  api: {
    causalModels: {
      list: vi.fn().mockResolvedValue([
        { id: "cm1", title: "Test Modell", status: "draft", axioms: [], slots: [], relations: [], linked_narratives: [] },
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
        linked_narratives: [
          { id: "n1", title: "Klartext Narrativ" },
        ],
      }),
    },
  },
}));

function renderPage(modelId = "cm1") {
  return render(
    <MemoryRouter initialEntries={[`/causal-model/${modelId}`]}>
      <Routes>
        <Route path="/causal-model/:modelId" element={<CausalModelEditor />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("CausalModelEditor — extensions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("auto-selects model from URL param and shows its title as heading", async () => {
    renderPage("cm1");
    expect(await screen.findByRole("heading", { name: "Test Modell" })).toBeInTheDocument();
  });

  it("shows Slots section with slot identifier", async () => {
    renderPage("cm1");
    await waitFor(() => {
      expect(screen.getByText("co2_emissionen")).toBeInTheDocument();
    });
  });

  it("shows Kausalrelationen section with relation identifier", async () => {
    renderPage("cm1");
    await waitFor(() => {
      expect(screen.getByText("co2_to_temp")).toBeInTheDocument();
    });
  });

  it("shows Verknüpfte Narrative section with linked narrative from model API", async () => {
    renderPage("cm1");
    await waitFor(() => {
      expect(screen.getByText("Klartext Narrativ")).toBeInTheDocument();
    });
  });

  it("navigates to narrative detail when linked narrative is clicked", async () => {
    renderPage("cm1");
    const link = await screen.findByText("Klartext Narrativ");
    fireEvent.click(link);
    expect(mockNavigate).toHaveBeenCalledWith("/narrative/n1");
  });
});
