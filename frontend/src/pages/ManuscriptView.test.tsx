import { render, screen, fireEvent, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import ManuscriptView from "./ManuscriptView";
import type { NarrativeUnitResponse } from "../lib/api";

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

/** A minimal work-root with one scene and one fragment. */
const TREE_WITH_SCENE: NarrativeUnitResponse = {
  id: "work-1",
  typ: "work",
  title: "Mein Roman",
  content: null,
  position: 1,
  narrative_id: "nar-001",
  parent_id: null,
  children: [
    {
      id: "scene-1",
      typ: "scene",
      title: "Szene 1",
      content: null,
      position: 1,
      narrative_id: "nar-001",
      parent_id: "work-1",
      children: [
        {
          id: "frag-1",
          typ: "fragment",
          title: null,
          content: "Hallo Welt",
          position: 1,
          narrative_id: "nar-001",
          parent_id: "scene-1",
          children: [],
        },
      ],
    },
  ],
};

/** A work-root with one scene but zero fragments. */
const TREE_SCENE_NO_FRAGMENTS: NarrativeUnitResponse = {
  ...TREE_WITH_SCENE,
  children: [
    { ...TREE_WITH_SCENE.children[0], children: [] },
  ],
};

function renderManuscript(narrativeId = "nar-001") {
  return render(
    <MemoryRouter initialEntries={[`/narrative/${narrativeId}/manuscript`]}>
      <Routes>
        <Route path="/narrative/:narrativeId/manuscript" element={<ManuscriptView />} />
      </Routes>
    </MemoryRouter>
  );
}

/** Renders ManuscriptView at a route with no :narrativeId param. */
function renderManuscriptWithoutParam() {
  return render(
    <MemoryRouter initialEntries={["/manuscript"]}>
      <Routes>
        <Route path="/manuscript" element={<ManuscriptView />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ManuscriptView", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  beforeEach(async () => {
    vi.clearAllMocks();
    const { getNarrativeTree, createNarrativeUnit, updateNarrativeUnit } =
      await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValue({
      narrative_id: "nar-001",
      root: null,
    });
    vi.mocked(createNarrativeUnit).mockResolvedValue({
      id: "new-unit",
      typ: "scene",
      title: "Szene 1",
      content: null,
      position: 1,
      narrative_id: "nar-001",
      parent_id: "work-1",
      children: [],
    });
    vi.mocked(updateNarrativeUnit).mockResolvedValue({
      id: "frag-1",
      typ: "fragment",
      title: null,
      content: "updated",
      position: 1,
      narrative_id: "nar-001",
      parent_id: "scene-1",
      children: [],
    });
  });
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

  // ── Happy path ────────────────────────────────────────────────────────────────

  it("renders scene title and fragment textarea when tree has scenes and fragments", async () => {
    /** Expects: SceneBreak title and a pre-filled textarea are visible after load. */
    const { getNarrativeTree } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_WITH_SCENE,
    });

    renderManuscript();
    expect(await screen.findByText("Szene 1")).toBeInTheDocument();
    const textarea = screen.getByPlaceholderText("Schreib hier…");
    expect(textarea).toHaveValue("Hallo Welt");
  });

  it("renders '+ Szene hinzufügen' button when tree is loaded", async () => {
    /** Expects: the add-scene button is present once a work root exists. */
    const { getNarrativeTree } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_WITH_SCENE,
    });

    renderManuscript();
    expect(
      await screen.findByRole("button", { name: "+ Szene hinzufügen" })
    ).toBeInTheDocument();
  });

  // ── Edge cases ────────────────────────────────────────────────────────────────

  it("renders correctly when a scene has no fragments", async () => {
    /** Expects: SceneBreak title is shown and the '+ Absatz hinzufügen' button is present even with no fragments. */
    const { getNarrativeTree } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });

    renderManuscript();
    expect(await screen.findByText("Szene 1")).toBeInTheDocument();
    expect(
      screen.queryByPlaceholderText("Schreib hier…")
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "+ Absatz hinzufügen" })
    ).toBeInTheDocument();
  });

  it("does not crash when narrativeId is missing from the URL", async () => {
    /** Expects: component mounts without throwing and shows the loading spinner indefinitely
     *  (no narrativeId → useEffect returns early without resolving loading state).
     *  No API call must be made. */
    const { getNarrativeTree } = await import("../lib/api");

    // Should not throw
    renderManuscriptWithoutParam();

    // Loading spinner is visible (the early-return bug keeps it loading forever)
    expect(screen.getByText("Lädt…")).toBeInTheDocument();

    // Critically: the API was never called
    expect(vi.mocked(getNarrativeTree)).not.toHaveBeenCalled();
  });

  // ── Interactions ──────────────────────────────────────────────────────────────

  it("'Erstes Werk anlegen' button calls createNarrativeUnit with typ='work'", async () => {
    /** Expects: clicking the empty-state CTA fires createNarrativeUnit for a 'work' unit. */
    const { createNarrativeUnit } = await import("../lib/api");
    vi.mocked(createNarrativeUnit).mockResolvedValueOnce({
      id: "work-new",
      typ: "work",
      title: "Mein Werk",
      content: null,
      position: 1,
      narrative_id: "nar-001",
      parent_id: null,
      children: [],
    });

    renderManuscript();
    const button = await screen.findByRole("button", {
      name: "Erstes Werk anlegen",
    });
    await userEvent.click(button);

    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledWith(
      expect.objectContaining({ typ: "work", narrative_id: "nar-001" })
    );
  });

  it("'+ Szene hinzufügen' button calls createNarrativeUnit with typ='scene'", async () => {
    /** Expects: clicking the add-scene button fires createNarrativeUnit for a 'scene' unit. */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_WITH_SCENE,
    });
    vi.mocked(createNarrativeUnit).mockResolvedValueOnce({
      id: "scene-new",
      typ: "scene",
      title: "Szene 2",
      content: null,
      position: 2,
      narrative_id: "nar-001",
      parent_id: "work-1",
      children: [],
    });

    renderManuscript();
    const button = await screen.findByRole("button", {
      name: "+ Szene hinzufügen",
    });
    await userEvent.click(button);

    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledWith(
      expect.objectContaining({
        typ: "scene",
        parent_id: "work-1",
        narrative_id: "nar-001",
      })
    );
  });

  // ── Lazy-create ─────────────────────────────────────────────────────────────

  it("'+ Absatz hinzufügen' renders a pending textarea immediately without calling createNarrativeUnit", async () => {
    /** Expects: clicking the add-fragment button renders a textarea immediately via local
     *  pending state, without sending a POST request to the server. */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    expect(screen.getByPlaceholderText("Schreib hier…")).toBeInTheDocument();
    expect(vi.mocked(createNarrativeUnit)).not.toHaveBeenCalled();
  });

  it("typing non-empty content into a pending textarea calls createNarrativeUnit after debounce", async () => {
    /** Expects: when a pending fragment receives non-empty content, createNarrativeUnit is
     *  called exactly once after the 1.5s debounce — not on click, not immediately on change. */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });
    vi.mocked(createNarrativeUnit).mockResolvedValueOnce({
      id: "frag-server-1",
      typ: "fragment",
      title: null,
      content: "Erstes Wort",
      position: 1,
      narrative_id: "nar-001",
      parent_id: "scene-1",
      children: [],
    });

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    const textarea = screen.getByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    fireEvent.change(textarea, { target: { value: "Erstes Wort" } });
    expect(vi.mocked(createNarrativeUnit)).not.toHaveBeenCalled();

    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });

    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledTimes(1);
    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledWith(
      expect.objectContaining({
        typ: "fragment",
        content: "Erstes Wort",
        narrative_id: "nar-001",
        parent_id: "scene-1",
      })
    );
    vi.useRealTimers();
  });

  it("after the first save, further edits call updateNarrativeUnit with the server id", async () => {
    /** Expects: once a pending fragment has been persisted (CREATE), subsequent content changes
     *  call updateNarrativeUnit with the server-assigned id — createNarrativeUnit is called only once. */
    const { getNarrativeTree, createNarrativeUnit, updateNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });
    vi.mocked(createNarrativeUnit).mockResolvedValueOnce({
      id: "frag-server-1",
      typ: "fragment",
      title: null,
      content: "Erstes Wort",
      position: 1,
      narrative_id: "nar-001",
      parent_id: "scene-1",
      children: [],
    });

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    const textarea = screen.getByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    // Before first edit: no API call yet (lazy-create — click must not trigger POST)
    expect(vi.mocked(createNarrativeUnit)).not.toHaveBeenCalled();

    // First edit → triggers CREATE
    fireEvent.change(textarea, { target: { value: "Erstes Wort" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });
    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledTimes(1);

    // Second edit → triggers UPDATE with server id
    fireEvent.change(textarea, { target: { value: "Zweites Wort" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });

    expect(vi.mocked(updateNarrativeUnit)).toHaveBeenCalledWith(
      "frag-server-1",
      expect.objectContaining({ content: "Zweites Wort" })
    );
    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });

  it("leaving a pending textarea empty after debounce does not call createNarrativeUnit", async () => {
    /** Expects: if the user clicks '+ Absatz' but only enters whitespace, createNarrativeUnit
     *  is never called — empty content must not reach the backend (would cause 422). */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    const textarea = screen.getByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    fireEvent.change(textarea, { target: { value: "   " } }); // whitespace only
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });

    expect(vi.mocked(createNarrativeUnit)).not.toHaveBeenCalled();
    vi.useRealTimers();
  });

  it("clicking '+ Absatz' twice creates two independent pending textareas", async () => {
    /** Expects: each click on the add-fragment button adds a separate pending textarea with a
     *  unique pending id. Both are visible in the DOM independently, and createNarrativeUnit
     *  is still not called on either click. */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });

    await userEvent.click(button);
    await userEvent.click(button);

    const textareas = screen.getAllByPlaceholderText("Schreib hier…");
    expect(textareas).toHaveLength(2);
    expect(vi.mocked(createNarrativeUnit)).not.toHaveBeenCalled();
  });

  it("createNarrativeUnit failure on pending CREATE sets saveStatus to unsaved", async () => {
    /** Expects: when createNarrativeUnit rejects after the debounce for a pending fragment,
     *  saveStatus returns to 'unsaved' — evidenced by the AutosaveIndicator showing "Nicht gespeichert". */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });
    vi.mocked(createNarrativeUnit).mockRejectedValueOnce(new Error("Server error"));

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    const textarea = screen.getByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    fireEvent.change(textarea, { target: { value: "Neuer Text" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });

    expect(screen.getByText(/Nicht gespeichert/i)).toBeInTheDocument();
    vi.useRealTimers();
  });

  it("a rapid second edit before the first CREATE resolves does not trigger a second createNarrativeUnit", async () => {
    /** Expects: if two debounce windows complete back-to-back while the first CREATE is still
     *  in-flight (unresolved), the second debounce must wait for the resolved id and then UPDATE
     *  rather than firing a second CREATE. createNarrativeUnit must be called exactly once. */
    const { getNarrativeTree, createNarrativeUnit, updateNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });

    // Simulate a slow CREATE so we can interleave a second debounce before it resolves
    let resolveCreate!: (value: typeof fakeCreated) => void;
    const fakeCreated = {
      id: "frag-server-1",
      typ: "fragment" as const,
      title: null as null,
      content: "Erstes Wort",
      position: 1,
      narrative_id: "nar-001",
      parent_id: "scene-1",
      children: [] as NarrativeUnitResponse[],
    };
    vi.mocked(createNarrativeUnit).mockImplementationOnce(
      () => new Promise((res) => { resolveCreate = res; })
    );

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    const textarea = screen.getByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    // First edit: trigger first debounce window
    fireEvent.change(textarea, { target: { value: "Erstes Wort" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });
    // First CREATE is now in-flight and unresolved — resolvedIds.current is NOT yet set

    // Second edit: triggers second debounce window *while* first CREATE is still pending
    fireEvent.change(textarea, { target: { value: "Zweites Wort" } });
    // Advance second debounce *before* resolving the first CREATE
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });
    // At this point the second debounce callback ran, but resolvedIds.current is still empty
    // → the implementation would fire a second CREATE here if not guarded

    // Now resolve the first CREATE
    await act(async () => { resolveCreate(fakeCreated); });

    // CREATE must have been called exactly once (the second debounce must not fire another CREATE)
    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledTimes(1);
    // UPDATE should have been called with the server id for the second content
    expect(vi.mocked(updateNarrativeUnit)).toHaveBeenCalledWith(
      "frag-server-1",
      expect.objectContaining({ content: "Zweites Wort" })
    );
    vi.useRealTimers();
  });

  it("POST for a pending fragment includes the correct position field", async () => {
    /** Expects: createNarrativeUnit is called with position matching the fragment's place
     *  in the scene (1-based). This is the contract the backend requires. */
    const { getNarrativeTree, createNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_SCENE_NO_FRAGMENTS,
    });
    vi.mocked(createNarrativeUnit).mockResolvedValueOnce({
      id: "frag-server-1",
      typ: "fragment",
      title: null,
      content: "Text",
      position: 1,
      narrative_id: "nar-001",
      parent_id: "scene-1",
      children: [],
    });

    renderManuscript();
    const button = await screen.findByRole("button", { name: "+ Absatz hinzufügen" });
    await userEvent.click(button);

    const textarea = screen.getByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    fireEvent.change(textarea, { target: { value: "Text" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });

    expect(vi.mocked(createNarrativeUnit)).toHaveBeenCalledWith(
      expect.objectContaining({ position: 1 })
    );
    vi.useRealTimers();
  });

  it("typing in a textarea sets saveStatus to 'unsaved'", async () => {
    /** Expects: after a keystroke, the BottomBar receives saveStatus='unsaved', evidenced by the unsaved indicator text. */
    const { getNarrativeTree } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_WITH_SCENE,
    });

    renderManuscript();
    const textarea = await screen.findByPlaceholderText("Schreib hier…");
    await userEvent.type(textarea, "X");

    // BottomBar renders AutosaveIndicator which shows "Nicht gespeichert" for "unsaved"
    expect(await screen.findByText(/Nicht gespeichert/i)).toBeInTheDocument();
  });

  // ── Autosave debounce ─────────────────────────────────────────────────────

  it("autosave calls updateNarrativeUnit after debounce", async () => {
    /** Expects: updateNarrativeUnit is NOT called immediately on keystroke, but IS called
     *  after the 1.5s debounce window has elapsed. */
    const { getNarrativeTree, updateNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_WITH_SCENE,
    });

    renderManuscript();
    // Wait with real timers until DOM is ready (findBy* uses waitFor with setTimeout).
    const textarea = await screen.findByPlaceholderText("Schreib hier…");

    // Switch to fake timers only after DOM is stable.
    // Use fireEvent instead of userEvent to avoid internal timer usage.
    vi.useFakeTimers();
    fireEvent.change(textarea, { target: { value: "Hallo WeltX" } });

    expect(vi.mocked(updateNarrativeUnit)).not.toHaveBeenCalled(); // vor debounce

    // act wraps timer advancement so React flushes all pending state updates
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1500);
    });

    expect(vi.mocked(updateNarrativeUnit)).toHaveBeenCalledWith(
      "frag-1",
      expect.objectContaining({ content: "Hallo WeltX" })
    );
    vi.useRealTimers();
  });

  it("autosave failure resets saveStatus to unsaved", async () => {
    /** Expects: when updateNarrativeUnit rejects after the debounce, the AutosaveIndicator
     *  shows "Nicht gespeichert" (status=unsaved). */
    const { getNarrativeTree, updateNarrativeUnit } = await import("../lib/api");
    vi.mocked(getNarrativeTree).mockResolvedValueOnce({
      narrative_id: "nar-001",
      root: TREE_WITH_SCENE,
    });
    vi.mocked(updateNarrativeUnit).mockRejectedValueOnce(new Error("Timeout"));

    renderManuscript();
    // Wait with real timers until DOM is ready.
    const textarea = await screen.findByPlaceholderText("Schreib hier…");

    vi.useFakeTimers();
    fireEvent.change(textarea, { target: { value: "Hallo WeltX" } });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1500);
    });

    // After the rejected promise flushes, saveStatus should be "unsaved"
    expect(screen.getByText(/Nicht gespeichert/i)).toBeInTheDocument();
    vi.useRealTimers();
  });
});
