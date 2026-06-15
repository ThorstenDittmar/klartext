import type { CSSProperties } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createNarrativeUnit,
  errorMessage,
  getNarrativeTree,
  type NarrativeUnitResponse,
  updateNarrativeUnit,
} from "../lib/api";
import { BottomBar } from "../components/BottomBar";
import { Breadcrumb } from "../components/Breadcrumb";
import { SceneBreak } from "../components/SceneBreak";
import { countWords } from "../utils/wordCount";
import { type AutosaveStatus } from "../components/AutosaveIndicator";

const AUTOSAVE_DELAY_MS = 1500;
// Prefix for locally-pending fragments that have not yet been persisted to the server.
const PENDING_PREFIX = "pending-";

/**
 * ManuscriptView — continuous prose editor for a Narrative.
 *
 * One <textarea> per Fragment (the atomic editing unit).
 * Lazy-create: clicking "+ Absatz" adds a local pending fragment immediately.
 * The POST only fires after the first non-empty debounce — never with empty content.
 * After the first save the pending id maps to the server id; subsequent edits use PATCH.
 */
export default function ManuscriptView() {
  const { narrativeId } = useParams<{ narrativeId: string }>();
  const navigate = useNavigate();

  const [tree, setTree] = useState<NarrativeUnitResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<AutosaveStatus>("saved");
  const [addingScene, setAddingScene] = useState(false);

  // Local content overrides: fragment id → current text (optimistic UI)
  const [contentMap, setContentMap] = useState<Record<string, string>>({});

  // One debounce timer per fragment (keyed by fragment id, including pending ids)
  const timers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  // Metadata for pending fragments: pending-id → { parent_id, position, narrative_id }
  const pendingMeta = useRef<Record<string, { parent_id: string; position: number; narrative_id: string }>>({});

  // After first successful CREATE: pending-id → server-assigned id
  const resolvedIds = useRef<Record<string, string>>({});

  // In-flight CREATE promise per pending id — prevents a second CREATE when a debounce
  // fires before the first CREATE resolves.
  const inFlightCreate = useRef<Partial<Record<string, Promise<string>>>>({});

  // Load tree on mount
  useEffect(() => {
    if (!narrativeId) return;
    setLoading(true);
    getNarrativeTree(narrativeId)
      .then((response) => {
        setTree(response.root);
        if (response.root) {
          const initial: Record<string, string> = {};
          collectFragments(response.root).forEach((f) => {
            initial[f.id] = f.content ?? "";
          });
          setContentMap(initial);
        }
      })
      .catch((err: unknown) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [narrativeId]);

  // Debounced autosave per fragment.
  // Pending fragments (id starts with PENDING_PREFIX) use CREATE on first non-empty save,
  // then UPDATE via the resolved server id on all subsequent saves.
  const handleFragmentChange = useCallback(
    (fragmentId: string, newContent: string) => {
      setContentMap((prev) => ({ ...prev, [fragmentId]: newContent }));
      setSaveStatus("unsaved");

      if (timers.current[fragmentId]) {
        clearTimeout(timers.current[fragmentId]);
      }
      timers.current[fragmentId] = setTimeout(async () => {
        if (!newContent.trim()) {
          // Empty content must never reach the backend (422). Reset to saved state.
          setSaveStatus("saved");
          return;
        }
        setSaveStatus("saving");
        try {
          if (fragmentId.startsWith(PENDING_PREFIX)) {
            const resolved = resolvedIds.current[fragmentId];
            if (resolved) {
              await updateNarrativeUnit(resolved, { content: newContent });
            } else if (inFlightCreate.current[fragmentId]) {
              // A CREATE is already in-flight — wait for the server id, then UPDATE.
              const serverId = await inFlightCreate.current[fragmentId];
              await updateNarrativeUnit(serverId, { content: newContent });
            } else {
              const meta = pendingMeta.current[fragmentId];
              const promise = createNarrativeUnit({
                typ: "fragment",
                content: newContent,
                position: meta.position,
                parent_id: meta.parent_id,
                narrative_id: meta.narrative_id,
              }).then((created) => {
                resolvedIds.current[fragmentId] = created.id;
                return created.id;
              });
              inFlightCreate.current[fragmentId] = promise;
              await promise;
            }
          } else {
            await updateNarrativeUnit(fragmentId, { content: newContent });
          }
          setSaveStatus("saved");
        } catch (err) {
          console.error("Autosave failed:", err);
          setSaveStatus("unsaved");
        }
      }, AUTOSAVE_DELAY_MS);
    },
    []
  );

  // Add a new Scene under the Work root
  const handleAddScene = async () => {
    if (!narrativeId || !tree || addingScene) return;
    setAddingScene(true);
    try {
      const sceneCount = tree.children.filter((c) => c.typ === "scene").length;
      const created = await createNarrativeUnit({
        typ: "scene",
        title: `Szene ${sceneCount + 1}`, // TODO(i18n)
        position: sceneCount + 1,
        parent_id: tree.id,
        narrative_id: narrativeId,
      });
      setTree((prev) =>
        prev ? { ...prev, children: [...prev.children, created] } : prev
      );
    } finally {
      setAddingScene(false);
    }
  };

  // Add a new Fragment to a Scene — synchronous, no API call.
  // The fragment is pending until the user types non-empty content and the debounce fires.
  const handleAddFragment = (
    sceneId: string,
    sceneChildren: NarrativeUnitResponse[]
  ) => {
    if (!narrativeId) return;
    const fragmentCount = sceneChildren.filter((c) => c.typ === "fragment").length;
    const pendingId = `${PENDING_PREFIX}${Date.now()}`;
    const position = fragmentCount + 1;

    pendingMeta.current[pendingId] = { parent_id: sceneId, position, narrative_id: narrativeId };

    const pendingFragment: NarrativeUnitResponse = {
      id: pendingId,
      typ: "fragment",
      title: null,
      content: "",
      position,
      narrative_id: narrativeId,
      parent_id: sceneId,
      children: [],
    };

    setContentMap((prev) => ({ ...prev, [pendingId]: "" }));
    setTree((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        children: prev.children.map((scene) =>
          scene.id === sceneId
            ? { ...scene, children: [...scene.children, pendingFragment] }
            : scene
        ),
      };
    });
  };

  const totalWordCount = countWords(Object.values(contentMap).join(" "));

  // ── Loading ────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={loadingStyle}>
        <span style={{ color: "var(--color-text-secondary)" }}>Lädt…</span>
      </div>
    );
  }

  // ── Error ──────────────────────────────────────────────────────────────────

  if (error) {
    return (
      <div style={errorContainerStyle}>
        <p style={{ color: "var(--color-error)" }}>Fehler: {error}</p>
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div style={pageStyle}>
      {/* Sticky top bar with breadcrumb */}
      <div style={topBarStyle}>
        <Breadcrumb
          items={[
            { label: "Meine Werke", onClick: () => navigate("/") }, // TODO(i18n)
            { label: tree?.title ?? "Manuskript" }, // TODO(i18n)
          ]}
        />
      </div>

      {/* Manuscript content area */}
      <main style={mainStyle}>
        {!tree ? (
          <EmptyManuscript
            narrativeId={narrativeId!}
            onWorkCreated={setTree}
          />
        ) : (
          <>
            {tree.children
              .filter((child) => child.typ === "scene")
              .map((scene) => (
                <section key={scene.id}>
                  <SceneBreak title={scene.title ?? "Szene"} />
                  {scene.children
                    .filter((child) => child.typ === "fragment")
                    .map((fragment) => (
                      <textarea
                        key={fragment.id}
                        value={contentMap[fragment.id] ?? fragment.content ?? ""}
                        onChange={(e) =>
                          handleFragmentChange(fragment.id, e.target.value)
                        }
                        placeholder="Schreib hier…" // TODO(i18n)
                        style={textareaStyle}
                      />
                    ))}
                  <button
                    onClick={() => handleAddFragment(scene.id, scene.children)}
                    style={addButtonStyle}
                  >
                    + Absatz hinzufügen {/* TODO(i18n) */}
                  </button>
                </section>
              ))}
            <div style={{ marginTop: "var(--space-8)" }}>
              <button
                onClick={handleAddScene}
                disabled={addingScene}
                style={addButtonStyle}
              >
                {addingScene ? "…" : "+ Szene hinzufügen" /* TODO(i18n) */}
              </button>
            </div>
          </>
        )}
      </main>

      <BottomBar wordCount={totalWordCount} saveStatus={saveStatus} />
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Recursively collects all Fragment nodes from a unit subtree. */
function collectFragments(
  unit: NarrativeUnitResponse
): NarrativeUnitResponse[] {
  const fragments: NarrativeUnitResponse[] = [];
  if (unit.typ === "fragment") fragments.push(unit);
  for (const child of unit.children) {
    fragments.push(...collectFragments(child));
  }
  return fragments;
}

// ─── Empty state ──────────────────────────────────────────────────────────────

function EmptyManuscript({
  narrativeId,
  onWorkCreated,
}: {
  narrativeId: string;
  onWorkCreated: (tree: NarrativeUnitResponse) => void;
}) {
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const work = await createNarrativeUnit({
        typ: "work",
        title: "Mein Werk", // TODO(i18n)
        position: 1,
        narrative_id: narrativeId,
      });
      onWorkCreated(work);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div style={emptyStateStyle}>
      <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-4)" }}>
        Noch kein Inhalt. Beginne mit dem ersten Werk. {/* TODO(i18n) */}
      </p>
      <button
        onClick={handleCreate}
        disabled={creating}
        style={primaryButtonStyle}
      >
        {creating ? "…" : "Erstes Werk anlegen" /* TODO(i18n) */}
      </button>
    </div>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const loadingStyle: CSSProperties = {
  padding: "var(--space-8)",
  textAlign: "center",
};

const errorContainerStyle: CSSProperties = {
  padding: "var(--space-8)",
};

const pageStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  minHeight: "100vh",
  backgroundColor: "var(--color-background)",
};

const topBarStyle: CSSProperties = {
  position: "sticky",
  top: 0,
  backgroundColor: "var(--color-surface)",
  borderBottom: "1px solid var(--color-border)",
  padding: "var(--space-2) var(--space-4)",
  zIndex: 10,
};

const mainStyle: CSSProperties = {
  flex: 1,
  maxWidth: "var(--prose-column-width)",
  width: "100%",
  margin: "0 auto",
  padding: "var(--space-8) var(--space-4)",
  paddingBottom: "calc(var(--bottom-bar-height) + var(--space-8))",
};

const textareaStyle: CSSProperties = {
  width: "100%",
  minHeight: 120,
  resize: "vertical",
  border: "none",
  outline: "none",
  backgroundColor: "transparent",
  fontFamily: "var(--font-family-prose)",
  fontSize: "var(--font-size-prose)",
  lineHeight: "var(--line-height-prose)",
  color: "var(--color-text-primary)",
  padding: "var(--space-2) 0",
};

const addButtonStyle: CSSProperties = {
  display: "block",
  marginTop: "var(--space-2)",
  background: "none",
  border: "1px dashed var(--color-border)",
  borderRadius: "var(--radius-sm)",
  padding: "var(--space-1) var(--space-3)",
  cursor: "pointer",
  color: "var(--color-text-secondary)",
  fontSize: "var(--font-size-sm)",
};

const emptyStateStyle: CSSProperties = {
  textAlign: "center",
  padding: "var(--space-16) var(--space-4)",
};

const primaryButtonStyle: CSSProperties = {
  padding: "var(--space-2) var(--space-6)",
  backgroundColor: "var(--color-accent)",
  color: "var(--color-on-accent)",
  border: "none",
  borderRadius: "var(--radius-md)",
  cursor: "pointer",
  fontSize: "var(--font-size-base)",
};
