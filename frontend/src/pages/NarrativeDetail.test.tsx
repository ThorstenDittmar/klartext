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
          { id: "s1", title: "Szene 1", text: "Max Mustermann war dabei.", position: 1 },
          { id: "s2", title: "Szene 2", text: "Eine zweite Szene ohne Akteur.", position: 2 },
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

  // --- Volltext-Modus ---

  it("renders Szenen / Volltext toggle", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");
    expect(screen.getByRole("button", { name: "Szenen" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Volltext" })).toBeInTheDocument();
  });

  it("scenes mode shows accordion items, not raw text", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");
    // Scene title visible as button, but raw text not visible (collapsed)
    expect(screen.getByText("Szene 1")).toBeInTheDocument();
    expect(screen.queryByText("Max Mustermann war dabei.")).not.toBeInTheDocument();
  });

  it("switching to Volltext shows scene text directly", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    // Both scene texts visible as prose. Scene 1 may be split across <mark>/text nodes
    // so we check body.textContent which concatenates all descendant text.
    expect(document.body.textContent).toContain("Max Mustermann war dabei.");
    expect(document.body.textContent).toContain("Eine zweite Szene ohne Akteur.");
  });

  it("Volltext hides the accordion buttons for individual scenes", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    // "Szene 1" accordion button no longer rendered — text rendered directly
    expect(screen.queryByText("Szene 1")).not.toBeInTheDocument();
  });

  it("actor name appears as highlighted mark in Volltext mode", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    // The actor "Max Mustermann" appears in scene text → rendered as <mark>
    const marks = document.querySelectorAll("mark");
    const actorMark = Array.from(marks).find((m) => m.textContent === "Max Mustermann");
    expect(actorMark).toBeTruthy();
    // Tooltip includes actor label and status
    expect(actorMark?.getAttribute("title")).toContain("Max Mustermann");
  });

  it("switching back to Szenen restores accordion", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));
    fireEvent.click(screen.getByRole("button", { name: "Szenen" }));

    // Accordion button for Szene 1 visible again
    expect(screen.getByText("Szene 1")).toBeInTheDocument();
    // Scene prose gone — body text no longer contains the raw scene text
    expect(document.body.textContent).not.toContain("Max Mustermann war dabei.");
  });

  // --- Dezente Highlights (Änderung 1) ---

  it("actor mark uses dotted underline, no background color", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    const marks = document.querySelectorAll("mark");
    const actorMark = Array.from(marks).find((m) => m.textContent === "Max Mustermann");
    expect(actorMark).toBeTruthy();

    // Must have dotted underline decoration
    expect(actorMark?.getAttribute("style")).toContain("text-decoration");
    expect(actorMark?.getAttribute("style")).toContain("dotted");

    // Must NOT have a solid background color — either empty or explicitly "none"
    const style = (actorMark as HTMLElement)?.style;
    expect(style?.backgroundColor).toBe("");
    // background: "none" is the correct way to suppress the default mark yellow
    const bg = style?.background ?? "";
    expect(bg === "" || bg === "none").toBe(true);
  });

  // --- Claim-Markierungen im Text (Änderung 2) ---

  it("claim text appears as highlighted mark in Volltext mode", async () => {
    // The mock claim has text "Die Geldmenge hat Einfluss auf die Inflation."
    // but that text is NOT in any scene text, so we need a scene that contains it.
    // Re-mock with matching scene text.
    const { api: mockApi } = await import("../lib/api");
    (mockApi.narratives.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      id: "n1",
      title: "Test Narrativ",
      causal_model_id: null,
      scenes: [
        { id: "s1", title: "Szene 1", text: "Die Geldmenge hat Einfluss auf die Inflation.", position: 1 },
      ],
      actors: [],
    });
    (mockApi.narratives.getClaims as ReturnType<typeof vi.fn>).mockResolvedValueOnce([
      {
        id: "c1",
        label: "Geldmenge treibt Inflation",
        text: "Die Geldmenge hat Einfluss auf die Inflation.",
        typ: "causal",
        confidence: 0.9,
        status: "draft",
        wirkgefuege_ref: null,
      },
    ]);

    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    const marks = document.querySelectorAll("mark");
    const claimMark = Array.from(marks).find((m) =>
      m.textContent === "Die Geldmenge hat Einfluss auf die Inflation."
    );
    expect(claimMark).toBeTruthy();
    expect(claimMark?.getAttribute("title")).toContain("Geldmenge treibt Inflation");
  });

  // --- Zwei-Spalten-Layout mit Kacheln (Änderung 3) ---

  it("Volltext mode shows actor tile in left panel", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    // The left panel must contain a tile for "Max Mustermann"
    // Use data-testid or check for the tile structure
    const tiles = document.querySelectorAll("[data-testid='actor-tile']");
    expect(tiles.length).toBeGreaterThan(0);
    expect(tiles[0].textContent).toContain("Max Mustermann");
  });

  it("Volltext mode shows claim tile in left panel", async () => {
    renderPage();
    await screen.findByText("Test Narrativ");

    fireEvent.click(screen.getByRole("button", { name: "Volltext" }));

    const tiles = document.querySelectorAll("[data-testid='claim-tile']");
    expect(tiles.length).toBeGreaterThan(0);
    expect(tiles[0].textContent).toContain("Geldmenge treibt Inflation");
  });
});
