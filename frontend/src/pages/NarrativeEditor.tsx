import { useEffect, useState } from "react";
import { api, Claim, Narrative, NarrativeSummary, Scene } from "../lib/api";

// ---------------------------------------------------------------------------
// Claim type labels (German — user-facing)
// ---------------------------------------------------------------------------

const CLAIM_TYPE_LABELS: Record<string, string> = {
  empirischer_claim: "Empirisch",
  kausaler_claim: "Kausal",
  definitorischer_claim: "Definitorisch",
  normativer_claim: "Normativ",
  prognostischer_claim: "Prognostisch",
  kontrafaktischer_claim: "Kontrafaktisch",
  methodischer_claim: "Methodisch",
  unsicherheitsclaim: "Unsicherheit",
};

// ---------------------------------------------------------------------------
// SceneCard — displays a single scene with its claims
// ---------------------------------------------------------------------------

interface SceneCardProps {
  scene: Scene;
  narrativeId: string;
  isSelected: boolean;
  onSelect: () => void;
}

function SceneCard({ scene, narrativeId, isSelected, onSelect }: SceneCardProps) {
  const [claims, setClaims] = useState<Claim[] | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [claimError, setClaimError] = useState<string | null>(null);

  // Load already-extracted claims when the card is expanded.
  useEffect(() => {
    if (!isSelected) return;
    api.narratives
      .getSceneClaims(narrativeId, scene.id)
      .then(setClaims)
      .catch(() => setClaims([]));
  }, [isSelected, narrativeId, scene.id]);

  async function extractClaims() {
    setExtracting(true);
    setClaimError(null);
    try {
      const result = await api.narratives.extractClaims(narrativeId, scene.id);
      setClaims(result.claims);
    } catch {
      setClaimError("Claims konnten nicht extrahiert werden.");
    } finally {
      setExtracting(false);
    }
  }

  return (
    <div
      style={{
        marginBottom: "0.75rem",
        border: `2px solid ${isSelected ? "#4a7aff" : "#ddd"}`,
        borderRadius: 4,
        overflow: "hidden",
      }}
    >
      {/* Scene header — always visible */}
      <div
        onClick={onSelect}
        style={{
          padding: "0.75rem 1rem",
          background: isSelected ? "#f0f4ff" : "white",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <strong>{scene.title}</strong>
          <span style={{ marginLeft: "0.5rem", fontSize: "0.8rem", color: "#888" }}>
            Szene {scene.position}
          </span>
        </div>
        <span style={{ fontSize: "0.75rem", color: "#aaa" }}>{isSelected ? "▲" : "▼"}</span>
      </div>

      {/* Expanded content */}
      {isSelected && (
        <div style={{ padding: "1rem", borderTop: "1px solid #eee", background: "white" }}>
          {/* Scene text */}
          <p style={{ margin: "0 0 1rem", whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
            {scene.text}
          </p>

          {/* Claims section */}
          <div style={{ borderTop: "1px solid #f0f0f0", paddingTop: "0.75rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
              <strong style={{ fontSize: "0.85rem" }}>
                Claims {claims !== null ? `(${claims.length})` : ""}
              </strong>
              <button
                onClick={extractClaims}
                disabled={extracting}
                style={{ fontSize: "0.8rem", padding: "0.25rem 0.6rem" }}
              >
                {extracting ? "Extrahiere…" : "Claims extrahieren"}
              </button>
            </div>

            {claimError && (
              <p style={{ color: "red", fontSize: "0.85rem", margin: "0.25rem 0" }}>{claimError}</p>
            )}

            {claims !== null && claims.length === 0 && !extracting && (
              <p style={{ color: "#888", fontSize: "0.85rem", margin: 0 }}>
                Noch keine Claims extrahiert.
              </p>
            )}

            {claims !== null && claims.length > 0 && (
              <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
                {claims.map((c, i) => (
                  <li
                    key={i}
                    style={{
                      display: "flex",
                      gap: "0.5rem",
                      alignItems: "flex-start",
                      marginBottom: "0.4rem",
                      fontSize: "0.85rem",
                    }}
                  >
                    <span
                      style={{
                        flexShrink: 0,
                        background: "#e8f0fe",
                        color: "#3c5bb5",
                        borderRadius: 3,
                        padding: "0.1rem 0.4rem",
                        fontSize: "0.75rem",
                        marginTop: "0.1rem",
                      }}
                    >
                      {CLAIM_TYPE_LABELS[c.typ] ?? c.typ}
                    </span>
                    <span style={{ color: "#333" }}>{c.text}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// NarrativeEditor — main page
// ---------------------------------------------------------------------------

export default function NarrativeEditor() {
  const [summaries, setSummaries] = useState<NarrativeSummary[]>([]);
  const [selected, setSelected] = useState<Narrative | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [sceneTitle, setSceneTitle] = useState("");
  const [sceneText, setSceneText] = useState("");
  const [expandedSceneId, setExpandedSceneId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.narratives.list().then(setSummaries).catch(() => setError("API nicht erreichbar"));
  }, []);

  async function createNarrative() {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      const narrative = await api.narratives.create(newTitle.trim());
      setSummaries((prev) => [...prev, { id: narrative.id, title: narrative.title }]);
      setSelected(narrative);
      setNewTitle("");
    } catch {
      setError("Narrativ konnte nicht erstellt werden.");
    } finally {
      setLoading(false);
    }
  }

  async function selectNarrative(id: string) {
    try {
      const narrative = await api.narratives.get(id);
      setSelected(narrative);
      setExpandedSceneId(null);
    } catch {
      setError("Narrativ konnte nicht geladen werden.");
    }
  }

  async function addScene() {
    if (!selected || !sceneTitle.trim() || !sceneText.trim()) return;
    setLoading(true);
    try {
      const scene = await api.narratives.addScene(selected.id, sceneTitle.trim(), sceneText.trim());
      setSelected((prev) =>
        prev ? { ...prev, scenes: [...prev.scenes, scene] } : prev
      );
      setExpandedSceneId(scene.id);
      setSceneTitle("");
      setSceneText("");
    } catch {
      setError("Szene konnte nicht hinzugefügt werden.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "2rem" }}>
      {/* Sidebar */}
      <aside>
        <h2 style={{ marginTop: 0 }}>Narrative</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}

        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {summaries.map((n) => (
            <li key={n.id}>
              <button
                onClick={() => selectNarrative(n.id)}
                style={{
                  background: selected?.id === n.id ? "#e8f0fe" : "none",
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  padding: "0.5rem 0.75rem",
                  marginBottom: "0.5rem",
                  cursor: "pointer",
                  width: "100%",
                  textAlign: "left",
                }}
              >
                {n.title}
              </button>
            </li>
          ))}
        </ul>

        <div style={{ marginTop: "1rem", borderTop: "1px solid #eee", paddingTop: "1rem" }}>
          <h3 style={{ marginTop: 0, fontSize: "0.9rem" }}>Neues Narrativ</h3>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Titel"
            style={{ width: "100%", padding: "0.4rem", marginBottom: "0.5rem", boxSizing: "border-box" }}
            onKeyDown={(e) => e.key === "Enter" && createNarrative()}
          />
          <button onClick={createNarrative} disabled={loading || !newTitle.trim()}>
            Anlegen
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main>
        {!selected ? (
          <p style={{ color: "#888" }}>Narrativ auswählen oder neu anlegen.</p>
        ) : (
          <>
            <h2 style={{ marginTop: 0 }}>{selected.title}</h2>
            <p style={{ color: "#888", fontSize: "0.85rem", marginTop: "-0.5rem", marginBottom: "1.5rem" }}>
              {selected.scenes.length}{" "}
              {selected.scenes.length === 1 ? "Szene" : "Szenen"}
            </p>

            {/* Scene list */}
            {selected.scenes.length === 0 ? (
              <p style={{ color: "#888" }}>Noch keine Szenen. Erste Szene unten hinzufügen.</p>
            ) : (
              selected.scenes.map((scene) => (
                <SceneCard
                  key={scene.id}
                  scene={scene}
                  narrativeId={selected.id}
                  isSelected={expandedSceneId === scene.id}
                  onSelect={() =>
                    setExpandedSceneId((prev) => (prev === scene.id ? null : scene.id))
                  }
                />
              ))
            )}

            {/* Add scene form */}
            <div
              style={{
                marginTop: "2rem",
                padding: "1rem",
                border: "1px solid #ddd",
                borderRadius: 4,
                background: "#fafafa",
              }}
            >
              <h3 style={{ marginTop: 0 }}>Szene hinzufügen</h3>
              <input
                value={sceneTitle}
                onChange={(e) => setSceneTitle(e.target.value)}
                placeholder="Titel der Szene"
                style={{ width: "100%", padding: "0.4rem", marginBottom: "0.5rem", boxSizing: "border-box" }}
              />
              <textarea
                value={sceneText}
                onChange={(e) => setSceneText(e.target.value)}
                placeholder="Text der Szene…"
                rows={6}
                style={{
                  width: "100%",
                  padding: "0.4rem",
                  marginBottom: "0.5rem",
                  boxSizing: "border-box",
                  lineHeight: 1.6,
                }}
              />
              <button
                onClick={addScene}
                disabled={loading || !sceneTitle.trim() || !sceneText.trim()}
              >
                Szene speichern
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
