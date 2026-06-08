import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, it, expect, vi } from "vitest";
import ManuscriptView from "./ManuscriptView";

vi.mock("../lib/api", async (importOriginal) => {
  const original = await importOriginal<typeof import("../lib/api")>();
  return {
    ...original,
    getNarrativeTree: vi.fn().mockResolvedValue({
      narrative_id: "nar-001",
      root: null,
    }),
    createNarrativeUnit: vi.fn(),
    updateNarrativeUnit: vi.fn(),
    deleteNarrativeUnit: vi.fn(),
  };
});

function renderManuscript(narrativeId = "nar-001") {
  return render(
    <MemoryRouter initialEntries={[`/narrative/${narrativeId}/manuscript`]}>
      <Routes>
        <Route path="/narrative/:narrativeId/manuscript" element={<ManuscriptView />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ManuscriptView", () => {
  it("shows loading indicator on initial render", () => {
    /** Expects: a loading message is visible before the API call resolves. */
    renderManuscript();
    expect(screen.getByText("Lädt…")).toBeInTheDocument();
  });

  it("shows empty state after load when tree is null", async () => {
    /** Expects: when getNarrativeTree returns root=null, the empty state message is visible. */
    renderManuscript();
    const emptyText = await screen.findByText(/Noch kein Inhalt/);
    expect(emptyText).toBeInTheDocument();
  });

  it("shows error message when API call fails", async () => {
    /** Expects: when getNarrativeTree rejects, an error message is displayed instead of a spinner. */
    const { getNarrativeTree } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockRejectedValueOnce(new Error("Netzwerkfehler"));

    renderManuscript();
    const errorText = await screen.findByText(/Fehler:/);
    expect(errorText).toBeInTheDocument();
  });
});
