import { useEffect, useState } from "react";
import { api, CausalModel } from "../lib/api";

export default function CausalModelEditor() {
  const [models, setModels] = useState<CausalModel[]>([]);
  const [selected, setSelected] = useState<CausalModel | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [axiomLabel, setAxiomLabel] = useState("");
  const [axiomDescription, setAxiomDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.causalModels.list().then(setModels).catch(() => setError("API nicht erreichbar"));
  }, []);

  async function createModel() {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      const model = await api.causalModels.create(newTitle.trim());
      setModels((prev) => [...prev, model]);
      setSelected(model);
      setNewTitle("");
    } catch {
      setError("Modell konnte nicht erstellt werden.");
    } finally {
      setLoading(false);
    }
  }

  async function selectModel(id: string) {
    try {
      const model = await api.causalModels.get(id);
      setSelected(model);
    } catch {
      setError("Modell konnte nicht geladen werden.");
    }
  }

  async function addAxiom() {
    if (!selected || !axiomLabel.trim() || !axiomDescription.trim()) return;
    setLoading(true);
    try {
      await api.causalModels.addAxiom(selected.id, axiomLabel.trim(), axiomDescription.trim());
      const updated = await api.causalModels.get(selected.id);
      setSelected(updated);
      setAxiomLabel("");
      setAxiomDescription("");
    } catch {
      setError("Axiom konnte nicht hinzugefügt werden.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "2rem" }}>
      <aside>
        <h2 style={{ marginTop: 0 }}>Wirkmodelle</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <ul style={{ listStyle: "none", padding: 0 }}>
          {models.map((m) => (
            <li key={m.id}>
              <button
                onClick={() => selectModel(m.id)}
                style={{
                  background: selected?.id === m.id ? "#e8f0fe" : "none",
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  padding: "0.5rem 0.75rem",
                  marginBottom: "0.5rem",
                  cursor: "pointer",
                  width: "100%",
                  textAlign: "left",
                }}
              >
                {m.title}
              </button>
            </li>
          ))}
        </ul>

        <div style={{ marginTop: "1rem", borderTop: "1px solid #eee", paddingTop: "1rem" }}>
          <h3 style={{ marginTop: 0, fontSize: "0.9rem" }}>Neues Wirkmodell</h3>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Titel"
            style={{ width: "100%", padding: "0.4rem", marginBottom: "0.5rem", boxSizing: "border-box" }}
            onKeyDown={(e) => e.key === "Enter" && createModel()}
          />
          <button onClick={createModel} disabled={loading || !newTitle.trim()}>
            Anlegen
          </button>
        </div>
      </aside>

      <main>
        {!selected ? (
          <p style={{ color: "#888" }}>Wirkmodell auswählen oder neu anlegen.</p>
        ) : (
          <>
            <h2 style={{ marginTop: 0 }}>{selected.title}</h2>
            <p style={{ color: "#888", fontSize: "0.85rem" }}>Status: {selected.status}</p>

            <h3>Axiome ({selected.axioms.length})</h3>
            {selected.axioms.length === 0 ? (
              <p style={{ color: "#888" }}>Noch keine Axiome.</p>
            ) : (
              <ul style={{ paddingLeft: "1.2rem" }}>
                {selected.axioms.map((a) => (
                  <li key={a.id} style={{ marginBottom: "1rem" }}>
                    <strong>{a.label}</strong>
                    <p style={{ margin: "0.25rem 0 0", color: "#444" }}>{a.description}</p>
                  </li>
                ))}
              </ul>
            )}

            <div
              style={{
                marginTop: "2rem",
                padding: "1rem",
                border: "1px solid #ddd",
                borderRadius: 4,
                background: "#fafafa",
              }}
            >
              <h3 style={{ marginTop: 0 }}>Axiom hinzufügen</h3>
              <input
                value={axiomLabel}
                onChange={(e) => setAxiomLabel(e.target.value)}
                placeholder="Bezeichnung"
                style={{ width: "100%", padding: "0.4rem", marginBottom: "0.5rem", boxSizing: "border-box" }}
              />
              <textarea
                value={axiomDescription}
                onChange={(e) => setAxiomDescription(e.target.value)}
                placeholder="Beschreibung"
                rows={3}
                style={{ width: "100%", padding: "0.4rem", marginBottom: "0.5rem", boxSizing: "border-box" }}
              />
              <button
                onClick={addAxiom}
                disabled={loading || !axiomLabel.trim() || !axiomDescription.trim()}
              >
                Axiom speichern
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
