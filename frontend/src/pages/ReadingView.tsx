import { useEffect, useState } from "react";
import { api, CausalModel, ConsistencyResult, Narrative, Scene } from "../lib/api";

export default function Leseansicht() {
  const [narratives, setNarratives] = useState<{ id: string; title: string }[]>([]);
  const [narrative, setNarrative] = useState<Narrative | null>(null);
  const [models, setModels] = useState<CausalModel[]>([]);
  const [selectedScene, setSelectedScene] = useState<Scene | null>(null);
  const [selectedModelId, setSelectedModelId] = useState<string>("");
  const [result, setResult] = useState<ConsistencyResult | null>(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.narratives.list(), api.causalModels.list()])
      .then(([narrs, mods]) => {
        setNarratives(narrs);
        setModels(mods);
        if (mods.length > 0) setSelectedModelId(mods[0].id);
        if (narrs.length > 0) return api.narratives.get(narrs[0].id);
      })
      .then((narr) => { if (narr) setNarrative(narr); })
      .catch(() => setError("API nicht erreichbar"));
  }, []);

  async function check() {
    if (!selectedScene || !selectedModelId) return;
    setChecking(true);
    setResult(null);
    try {
      const res = await api.causalModels.checkConsistency(selectedModelId, selectedScene.text);
      setResult(res);
    } catch {
      setError("Konsistenzprüfung fehlgeschlagen.");
    } finally {
      setChecking(false);
    }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Leseansicht</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
        {/* Szenenauswahl */}
        <div>
          <h3>Narrativ</h3>
          {narratives.length > 1 && (
            <select
              onChange={(e) => {
                api.narratives.get(e.target.value).then(setNarrative);
                setSelectedScene(null);
                setResult(null);
              }}
              style={{ marginBottom: "1rem", padding: "0.4rem" }}
            >
              {narratives.map((n) => (
                <option key={n.id} value={n.id}>{n.title}</option>
              ))}
            </select>
          )}

          {narrative?.scenes.map((scene) => (
            <div
              key={scene.id}
              onClick={() => { setSelectedScene(scene); setResult(null); }}
              style={{
                padding: "0.75rem",
                marginBottom: "0.75rem",
                border: `2px solid ${selectedScene?.id === scene.id ? "#4a7aff" : "#ddd"}`,
                borderRadius: 4,
                cursor: "pointer",
                background: selectedScene?.id === scene.id ? "#f0f4ff" : "white",
              }}
            >
              <strong>{scene.title}</strong>
              <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#555", whiteSpace: "pre-wrap" }}>
                {scene.text.slice(0, 200)}…
              </p>
            </div>
          ))}
        </div>

        {/* Konsistenzprüfung */}
        <div>
          <h3>Konsistenzprüfung</h3>

          {selectedScene ? (
            <>
              <p style={{ fontSize: "0.85rem", color: "#555", whiteSpace: "pre-wrap", marginBottom: "1rem" }}>
                {selectedScene.text}
              </p>

              <label style={{ display: "block", marginBottom: "0.5rem" }}>
                Wirkmodell:
                <select
                  value={selectedModelId}
                  onChange={(e) => setSelectedModelId(e.target.value)}
                  style={{ marginLeft: "0.5rem", padding: "0.4rem" }}
                >
                  {models.map((m) => (
                    <option key={m.id} value={m.id}>{m.title}</option>
                  ))}
                </select>
              </label>

              <button onClick={check} disabled={checking || !selectedModelId}>
                {checking ? "Prüfe…" : "Konsistenz prüfen"}
              </button>

              {result && (
                <div style={{ marginTop: "1.5rem" }}>
                  <div
                    style={{
                      padding: "0.75rem 1rem",
                      borderRadius: 4,
                      background: result.consistent ? "#e6f4ea" : "#fce8e6",
                      color: result.consistent ? "#1e7e34" : "#c5221f",
                      fontWeight: "bold",
                      marginBottom: "1rem",
                    }}
                  >
                    {result.consistent ? "✓ Konsistent" : `✗ ${result.conflicts.length} Konflikt${result.conflicts.length !== 1 ? "e" : ""}`}
                  </div>

                  {result.conflicts.map((c, i) => (
                    <div
                      key={i}
                      style={{
                        marginBottom: "1rem",
                        padding: "0.75rem",
                        border: "1px solid #f5c6c6",
                        borderRadius: 4,
                        background: "#fffafa",
                      }}
                    >
                      <strong style={{ fontSize: "0.85rem", color: "#888" }}>Axiom</strong>
                      <p style={{ margin: "0.15rem 0 0.5rem", fontStyle: "italic" }}>{c.axiom_label}</p>
                      <strong style={{ fontSize: "0.85rem", color: "#888" }}>Problem</strong>
                      <p style={{ margin: "0.15rem 0 0.5rem" }}>{c.description}</p>
                      {c.suggestion && (
                        <>
                          <strong style={{ fontSize: "0.85rem", color: "#888" }}>Vorschlag</strong>
                          <p style={{ margin: "0.15rem 0 0" }}>{c.suggestion}</p>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <p style={{ color: "#888" }}>Szene auswählen um die Konsistenz zu prüfen.</p>
          )}
        </div>
      </div>
    </div>
  );
}
