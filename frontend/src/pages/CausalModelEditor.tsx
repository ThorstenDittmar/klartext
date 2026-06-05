import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { api, CausalModel } from "../lib/api";
import { EpistemicBadge } from "../components/EpistemicBadge";

// ---------------------------------------------------------------------------
// Table styles (font-size 12px, tertiary header, tertiary row border)
// ---------------------------------------------------------------------------
const TABLE: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: "13px",
};

const TH: React.CSSProperties = {
  textAlign: "left",
  fontSize: "11px",
  fontWeight: "600",
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  color: "var(--color-text-tertiary)",
  borderBottom: "1px solid var(--color-border)",
  paddingBottom: "8px",
  paddingRight: "16px",
};

const TD: React.CSSProperties = {
  padding: "10px 16px 10px 0",
  borderBottom: "1px solid var(--color-border-subtle)",
  verticalAlign: "top",
  fontSize: "13px",
  color: "var(--color-text-primary)",
};

// ---------------------------------------------------------------------------
// CausalModelEditor — Screen 4
// ---------------------------------------------------------------------------

export default function CausalModelEditor() {
  const location = useLocation();
  const navigate = useNavigate();
  const { modelId } = useParams<{ modelId: string }>();
  const locationState = location.state as { selectedModelId?: string } | null;

  const [models, setModels] = useState<CausalModel[]>([]);
  const [selected, setSelected] = useState<CausalModel | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [axiomLabel, setAxiomLabel] = useState("");
  const [axiomDescription, setAxiomDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const targetId = modelId ?? locationState?.selectedModelId;
    if (!targetId) {
      // No model ID — just load the list so the user can pick one
      api.causalModels.list()
        .then(setModels)
        .catch(() => setError("API nicht erreichbar"));
      return;
    }
    Promise.all([api.causalModels.list(), api.causalModels.get(targetId)])
      .then(([cms, model]) => {
        setModels(cms);
        setSelected(model);
      })
      .catch(() => setError("API nicht erreichbar"));
  }, [modelId]);

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

  const linkedNarratives = selected?.linked_narratives ?? [];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", minHeight: "calc(100vh - 4rem)" }}>
      <aside style={{ background: "var(--color-bg-subtle)", borderRight: "1px solid var(--color-border)", padding: "16px 12px", overflowY: "auto" }}>
        <h2 style={{ fontSize: "12px", fontWeight: "600", color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.06em", margin: "0 0 12px" }}>Wirkmodelle</h2>
        {error && <p style={{ color: "var(--color-red-text)" }}>{error}</p>}
        <ul style={{ listStyle: "none", padding: 0 }}>
          {models.map((m) => (
            <li key={m.id}>
              <button
                onClick={() => loadModel(m.id)}
                style={{
                  background: selected?.id === m.id ? "var(--color-blue-bg)" : "none",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 10px",
                  marginBottom: "2px",
                  cursor: "pointer",
                  width: "100%",
                  textAlign: "left" as const,
                  fontSize: "13px",
                  color: selected?.id === m.id ? "var(--color-blue-text)" : "var(--color-text-primary)",
                  fontWeight: selected?.id === m.id ? "500" : "normal",
                }}
              >
                {m.title}
              </button>
            </li>
          ))}
        </ul>

        <div style={{ marginTop: "16px", borderTop: "1px solid var(--color-border)", paddingTop: "16px" }}>
          <h3 style={{ fontSize: "11px", color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.06em", margin: "16px 0 8px", fontWeight: "600" }}>Neues Wirkmodell</h3>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Titel"
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: "6px",
              padding: "8px 10px",
              fontSize: "13px",
              width: "100%",
              marginBottom: "8px",
              fontFamily: "var(--font-sans)",
              boxSizing: "border-box" as const,
            }}
            onKeyDown={(e) => e.key === "Enter" && createModel()}
          />
          <button
            onClick={createModel}
            disabled={loading || !newTitle.trim()}
            style={{
              background: loading || !newTitle.trim() ? "var(--color-bg-subtle)" : "var(--color-text-primary)",
              color: loading || !newTitle.trim() ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
              border: "none",
              borderRadius: "6px",
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: "500",
              cursor: "pointer",
              width: "100%",
            }}
          >
            Anlegen
          </button>
        </div>
      </aside>

      <main style={{ padding: "24px 32px", background: "var(--color-bg)", overflowY: "auto" }}>
        {!selected ? (
          <p style={{ color: "var(--color-text-tertiary)" }}>Wirkmodell auswählen oder neu anlegen.</p>
        ) : (
          <>
            <h2 style={{ fontSize: "20px", fontWeight: "600", marginTop: "0", marginBottom: "4px" }}>{selected.title}</h2>
            <p style={{ fontSize: "12px", color: "var(--color-text-secondary)", margin: "0 0 24px" }}>Status: {selected.status}</p>

            {/* Slots -------------------------------------------------------- */}
            <h3 style={{ fontSize: "11px", fontWeight: "600", textTransform: "uppercase" as const, letterSpacing: "0.06em", color: "var(--color-text-tertiary)", margin: "24px 0 10px" }}>Slots ({selected.slots.length})</h3>
            {selected.slots.length === 0 ? (
              <p style={{ fontSize: "13px", color: "var(--color-text-tertiary)" }}>Keine Slots.</p>
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
            <h3 style={{ fontSize: "11px", fontWeight: "600", textTransform: "uppercase" as const, letterSpacing: "0.06em", color: "var(--color-text-tertiary)", margin: "24px 0 10px" }}>
              Kausalrelationen ({selected.relations.length})
            </h3>
            {selected.relations.length === 0 ? (
              <p style={{ fontSize: "13px", color: "var(--color-text-tertiary)" }}>Keine Relationen.</p>
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
            <h3 style={{ fontSize: "11px", fontWeight: "600", textTransform: "uppercase" as const, letterSpacing: "0.06em", color: "var(--color-text-tertiary)", margin: "24px 0 10px" }}>Axiome ({selected.axioms.length})</h3>
            {selected.axioms.length === 0 ? (
              <p style={{ fontSize: "13px", color: "var(--color-text-tertiary)" }}>Noch keine Axiome.</p>
            ) : (
              <ul style={{ paddingLeft: "1.2rem" }}>
                {selected.axioms.map((a) => (
                  <li key={a.id} style={{ marginBottom: "12px", fontSize: "13px" }}>
                    <strong style={{ color: "var(--color-text-primary)", fontSize: "13px" }}>{a.label}</strong>
                    <p style={{ margin: "2px 0 0", color: "var(--color-text-secondary)", fontSize: "13px" }}>{a.description}</p>
                  </li>
                ))}
              </ul>
            )}

            {/* Add axiom form ----------------------------------------------- */}
            <div
              style={{
                marginTop: "24px",
                padding: "16px",
                border: "1px solid var(--color-border)",
                borderRadius: "8px",
                background: "var(--color-bg-subtle)",
              }}
            >
              <h3 style={{ fontSize: "11px", fontWeight: "600", textTransform: "uppercase" as const, letterSpacing: "0.06em", color: "var(--color-text-tertiary)", margin: "0 0 10px" }}>Axiom hinzufügen</h3>
              <input
                value={axiomLabel}
                onChange={(e) => setAxiomLabel(e.target.value)}
                placeholder="Bezeichnung"
                style={{
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "8px 10px",
                  fontSize: "13px",
                  width: "100%",
                  marginBottom: "8px",
                  fontFamily: "var(--font-sans)",
                  boxSizing: "border-box" as const,
                }}
              />
              <textarea
                value={axiomDescription}
                onChange={(e) => setAxiomDescription(e.target.value)}
                placeholder="Beschreibung"
                rows={3}
                style={{
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "8px 10px",
                  fontSize: "13px",
                  width: "100%",
                  marginBottom: "8px",
                  fontFamily: "var(--font-sans)",
                  boxSizing: "border-box" as const,
                }}
              />
              <button
                onClick={addAxiom}
                disabled={loading || !axiomLabel.trim() || !axiomDescription.trim()}
                style={{
                  background: loading || !axiomLabel.trim() || !axiomDescription.trim() ? "var(--color-bg-subtle)" : "var(--color-text-primary)",
                  color: loading || !axiomLabel.trim() || !axiomDescription.trim() ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 16px",
                  fontSize: "13px",
                  fontWeight: "500",
                  cursor: "pointer",
                  width: "100%",
                }}
              >
                Axiom speichern
              </button>
            </div>

            {/* Verknüpfte Narrative ----------------------------------------- */}
            <h3 style={{ fontSize: "11px", fontWeight: "600", textTransform: "uppercase" as const, letterSpacing: "0.06em", color: "var(--color-text-tertiary)", margin: "24px 0 10px" }}>
              Verknüpfte Narrative ({linkedNarratives.length})
            </h3>
            {linkedNarratives.length === 0 ? (
              <p style={{ fontSize: "13px", color: "var(--color-text-tertiary)" }}>Keine verknüpften Narrative.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0 }}>
                {linkedNarratives.map((n) => (
                  <li key={n.id} style={{ marginBottom: "0.4rem" }}>
                    <button
                      onClick={() => navigate(`/narrative/${n.id}`)}
                      style={{
                        background: "none",
                        border: "1px solid var(--color-border)",
                        borderRadius: "6px",
                        padding: "8px 12px",
                        cursor: "pointer",
                        fontSize: "13px",
                        color: "var(--color-text-primary)",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
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
