import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api, CausalModel, NarrativeSummary } from "../lib/api";

// ---------------------------------------------------------------------------
// Colour constants for EpistemicStatus badges
// ---------------------------------------------------------------------------
const BADGE = {
  incomplete: { bg: "#FAEEDA", text: "#854F0B" },
  axiomatic: { bg: "#EAF3DE", text: "#3B6D11" },
} as const;

function EpistemicBadge({ status }: { status: string }) {
  const style = status === "axiomatic" ? BADGE.axiomatic : BADGE.incomplete;
  return (
    <span
      style={{
        fontSize: "11px",
        background: style.bg,
        color: style.text,
        padding: "0.1rem 0.4rem",
        borderRadius: 3,
      }}
    >
      {status}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Table styles (font-size 12px, tertiary header, tertiary row border)
// ---------------------------------------------------------------------------
const TABLE: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: "12px",
};

const TH: React.CSSProperties = {
  textAlign: "left",
  color: "#aaa",
  fontWeight: "normal",
  borderBottom: "1px solid #e0e0e0",
  paddingBottom: "0.4rem",
  paddingRight: "1rem",
};

const TD: React.CSSProperties = {
  padding: "0.4rem 1rem 0.4rem 0",
  borderBottom: "1px solid #f0f0f0",
  verticalAlign: "top",
};

// ---------------------------------------------------------------------------
// CausalModelEditor — Screen 4
// ---------------------------------------------------------------------------

export default function CausalModelEditor() {
  const location = useLocation();
  const navigate = useNavigate();
  const locationState = location.state as { selectedModelId?: string } | null;

  const [models, setModels] = useState<CausalModel[]>([]);
  const [selected, setSelected] = useState<CausalModel | null>(null);
  const [narratives, setNarratives] = useState<NarrativeSummary[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [axiomLabel, setAxiomLabel] = useState("");
  const [axiomDescription, setAxiomDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.causalModels.list(), api.narratives.list()])
      .then(([cms, narrs]) => {
        setModels(cms);
        setNarratives(narrs);
        // Auto-select model if navigated from Screen 3
        const targetId = locationState?.selectedModelId;
        if (targetId) {
          const match = cms.find((m) => m.id === targetId);
          if (match) {
            loadModel(targetId);
          }
        }
      })
      .catch(() => setError("API nicht erreichbar"));
  }, []);

  async function loadModel(id: string) {
    try {
      const model = await api.causalModels.get(id);
      setSelected(model);
    } catch {
      setError("Modell konnte nicht geladen werden.");
    }
  }

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

  const linkedNarratives = narratives.filter((n) => n.causal_model_id === selected?.id);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "2rem" }}>
      <aside>
        <h2 style={{ marginTop: 0 }}>Wirkmodelle</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <ul style={{ listStyle: "none", padding: 0 }}>
          {models.map((m) => (
            <li key={m.id}>
              <button
                onClick={() => loadModel(m.id)}
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
            style={{
              width: "100%",
              padding: "0.4rem",
              marginBottom: "0.5rem",
              boxSizing: "border-box",
            }}
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

            {/* Slots -------------------------------------------------------- */}
            <h3 style={{ marginBottom: "0.5rem" }}>Slots ({selected.slots.length})</h3>
            {selected.slots.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.85rem" }}>Keine Slots.</p>
            ) : (
              <table style={TABLE}>
                <thead>
                  <tr>
                    <th style={TH}>identifier</th>
                    <th style={TH}>slot_type</th>
                    <th style={TH}>epistemic_status</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.slots.map((s) => (
                    <tr key={s.id}>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{s.identifier}</td>
                      <td style={TD}>{s.slot_type}</td>
                      <td style={TD}>
                        <EpistemicBadge status={s.epistemic_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Relations ---------------------------------------------------- */}
            <h3 style={{ marginBottom: "0.5rem", marginTop: "2rem" }}>
              Kausalrelationen ({selected.relations.length})
            </h3>
            {selected.relations.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.85rem" }}>Keine Relationen.</p>
            ) : (
              <table style={TABLE}>
                <thead>
                  <tr>
                    <th style={TH}>Identifier</th>
                    <th style={TH}>Quelle</th>
                    <th style={TH}>Ziel</th>
                    <th style={TH}>Mechanismus</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.relations.map((r) => (
                    <tr key={r.id}>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{r.identifier}</td>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{r.source_slot_id}</td>
                      <td style={{ ...TD, fontFamily: "monospace" }}>{r.target_slot_id}</td>
                      <td style={TD}>{r.mechanism ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Axiome ------------------------------------------------------- */}
            <h3 style={{ marginTop: "2rem" }}>Axiome ({selected.axioms.length})</h3>
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

            {/* Add axiom form ----------------------------------------------- */}
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
                style={{
                  width: "100%",
                  padding: "0.4rem",
                  marginBottom: "0.5rem",
                  boxSizing: "border-box",
                }}
              />
              <textarea
                value={axiomDescription}
                onChange={(e) => setAxiomDescription(e.target.value)}
                placeholder="Beschreibung"
                rows={3}
                style={{
                  width: "100%",
                  padding: "0.4rem",
                  marginBottom: "0.5rem",
                  boxSizing: "border-box",
                }}
              />
              <button
                onClick={addAxiom}
                disabled={loading || !axiomLabel.trim() || !axiomDescription.trim()}
              >
                Axiom speichern
              </button>
            </div>

            {/* Verknüpfte Narrative ----------------------------------------- */}
            <h3 style={{ marginTop: "2rem" }}>
              Verknüpfte Narrative ({linkedNarratives.length})
            </h3>
            {linkedNarratives.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.85rem" }}>Keine verknüpften Narrative.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0 }}>
                {linkedNarratives.map((n) => (
                  <li key={n.id} style={{ marginBottom: "0.4rem" }}>
                    <button
                      onClick={() => navigate("/narrative")}
                      style={{
                        background: "none",
                        border: "1px solid #ddd",
                        borderRadius: 4,
                        padding: "0.4rem 0.75rem",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.4rem",
                      }}
                    >
                      <span>{n.title}</span>
                      <span>→</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </main>
    </div>
  );
}
