import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, vi } from "vitest";
import App from "./App";

// Mock all page components so we don't need full API/router setup
vi.mock("./pages/MeineWerke", () => ({ default: () => <div>MeineWerke</div> }));
vi.mock("./pages/NarrativeDetail", () => ({ default: () => <div>NarrativeDetail</div> }));
vi.mock("./pages/NarrativeAnalyse", () => ({ default: () => <div>NarrativeAnalyse</div> }));
vi.mock("./pages/WirkgefuegeVorschlag", () => ({ default: () => <div>WirkgefuegeVorschlag</div> }));
vi.mock("./pages/CausalModelEditor", () => ({ default: () => <div>CausalModelEditor</div> }));
vi.mock("./pages/Login", () => ({ default: () => <div>Login</div> }));

describe("App routing", () => {
  it("renders without crashing", async () => {
    render(<App />);
    await waitFor(() => {
      screen.getByText("MeineWerke");
    });
  });
});
