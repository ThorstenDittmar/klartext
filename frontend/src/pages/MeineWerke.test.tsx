import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import MeineWerke from "./MeineWerke";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("../lib/api", () => ({
  api: {
    narratives: {
      list: vi.fn().mockResolvedValue([
        {
          id: "n1",
          title: "Mein Narrativ",
          causal_model_id: null,
          scene_count: 3,
          actor_count: 2,
          claim_count: 5,
        },
      ]),
      create: vi.fn().mockResolvedValue({ id: "n2", title: "Neues Narrativ", causal_model_id: null }),
      importFromPath: vi.fn().mockResolvedValue({ id: "n3", title: "Importiert", causal_model_id: null }),
    },
  },
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <MeineWerke />
    </MemoryRouter>
  );
}

describe("MeineWerke", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockReset();
  });

  it("renders narrative cards with title and counts", async () => {
    renderPage();
    expect(await screen.findByText("Mein Narrativ")).toBeInTheDocument();
    expect(screen.getByText("3 Szenen")).toBeInTheDocument();
    expect(screen.getByText("2 Akteure")).toBeInTheDocument();
    expect(screen.getByText("5 Claims")).toBeInTheDocument();
  });

  it("navigates to narrative detail on card click", async () => {
    renderPage();
    const card = await screen.findByText("Mein Narrativ");
    fireEvent.click(card);
    expect(mockNavigate).toHaveBeenCalledWith("/narrative/n1");
  });

  it("creates narrative and navigates to it", async () => {
    renderPage();
    await screen.findByText("Mein Narrativ"); // wait for load

    const input = screen.getByPlaceholderText("Titel");
    fireEvent.change(input, { target: { value: "Neues Werk" } });

    const btn = screen.getByRole("button", { name: /Anlegen/i });
    fireEvent.click(btn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/narrative/n2");
    });
  });

  it("imports narrative and navigates to it", async () => {
    const { api } = await import("../lib/api");
    renderPage();
    await screen.findByText("Mein Narrativ"); // wait for load

    const input = screen.getByPlaceholderText("Pfad zur .docx oder .md");
    fireEvent.change(input, { target: { value: "/some/path.md" } });

    const btn = screen.getByRole("button", { name: /Importieren/i });
    fireEvent.click(btn);

    await waitFor(() => {
      expect(api.narratives.importFromPath).toHaveBeenCalledWith("/some/path.md");
      expect(mockNavigate).toHaveBeenCalledWith("/narrative/n3");
    });
  });

  it("shows empty state when no narratives exist", async () => {
    const { api } = await import("../lib/api");
    vi.mocked(api.narratives.list).mockResolvedValueOnce([]);

    renderPage();

    expect(await screen.findByText("Noch keine Werke vorhanden.")).toBeInTheDocument();
  });
});
