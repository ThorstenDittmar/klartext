import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, NarrativeSummary } from "../lib/api";

// ---------------------------------------------------------------------------
// MeineWerke — Screen 0 — entry point, lists all narratives
// ---------------------------------------------------------------------------

export default function MeineWerke() {
  const [summaries, setSummaries] = useState<NarrativeSummary[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [importPath, setImportPath] = useState("");
  const [creating, setCreating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.narratives.list()
      .then(setSummaries)
      .catch(() => setError("API nicht erreichbar"));
  }, []);

  async function createNarrative() {
    if (!newTitle.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const narrative = await api.narratives.create(newTitle.trim());
      setNewTitle("");
      navigate(`/narrative/${narrative.id}`);
    } catch {
      setError("Narrativ konnte nicht erstellt werden.");
    } finally {
      setCreating(false);
    }
  }

  async function importNarrative() {
    if (!importPath.trim()) return;
    setImporting(true);
    setError(null);
    try {
      const narrative = await api.narratives.importFromPath(importPath.trim());
      setImportPath("");
      navigate(`/narrative/${narrative.id}`);
    } catch {
      setError("Import fehlgeschlagen. Pfad prüfen.");
    } finally {
      setImporting(false);
    }
  }

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "40px 24px" }}>
      <h1 style={{ fontSize: "24px", fontWeight: "700", marginTop: "0", marginBottom: "8px", color: "var(--color-text-primary)" }}>
        Meine Werke
      </h1>
      <p style={{ fontSize: "14px", color: "var(--color-text-secondary)", margin: "0 0 32px" }}>
        {summaries.length === 0 ? "Noch keine Werke vorhanden." : `${summaries.length} Narrative`}
      </p>

      {error && (
        <p style={{ color: "var(--color-red-text)", fontSize: "13px", marginBottom: "16px" }}>{error}</p>
      )}

      {/* Narrative grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: "12px",
          marginBottom: "40px",
        }}
      >
        {summaries.map((n) => (
          <button
            key={n.id}
            onClick={() => navigate(`/narrative/${n.id}`)}
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: "8px",
              padding: "16px 20px",
              cursor: "pointer",
              background: "var(--color-bg)",
              textAlign: "left",
              display: "block",
              width: "100%",
            }}
          >
            <h3
              style={{
                margin: "0 0 10px",
                fontSize: "15px",
                fontWeight: "600",
                color: "var(--color-text-primary)",
              }}
            >
              {n.title}
            </h3>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              <Chip>{n.scene_count} Szenen</Chip>
              <Chip>{n.actor_count} Akteure</Chip>
              <Chip>{n.claim_count} Claims</Chip>
              {n.causal_model_id && (
                <Chip variant="teal">Wirkgefüge</Chip>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Create + Import side by side */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Create */}
        <div
          style={{
            border: "1px solid var(--color-border)",
            borderRadius: "8px",
            padding: "20px",
            background: "var(--color-bg-subtle)",
          }}
        >
          <h3
            style={{
              margin: "0 0 12px",
              fontSize: "11px",
              fontWeight: "600",
              color: "var(--color-text-tertiary)",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
            }}
          >
            Neues Narrativ
          </h3>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createNarrative()}
            placeholder="Titel"
            style={inputStyle}
          />
          <button
            onClick={createNarrative}
            disabled={creating || !newTitle.trim()}
            style={primaryButtonStyle(creating || !newTitle.trim())}
          >
            {creating ? "Erstelle…" : "Anlegen"}
          </button>
        </div>

        {/* Import */}
        <div
          style={{
            border: "1px solid var(--color-border)",
            borderRadius: "8px",
            padding: "20px",
            background: "var(--color-bg-subtle)",
          }}
        >
          <h3
            style={{
              margin: "0 0 12px",
              fontSize: "11px",
              fontWeight: "600",
              color: "var(--color-text-tertiary)",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
            }}
          >
            Aus Datei importieren
          </h3>
          <input
            value={importPath}
            onChange={(e) => setImportPath(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && importNarrative()}
            placeholder="Pfad zur .docx oder .md"
            style={inputStyle}
          />
          <button
            onClick={importNarrative}
            disabled={importing || !importPath.trim()}
            style={primaryButtonStyle(importing || !importPath.trim())}
          >
            {importing ? "Importiere…" : "Importieren"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components and style helpers
// ---------------------------------------------------------------------------

function Chip({ children, variant = "default" }: { children: React.ReactNode; variant?: "default" | "teal" }) {
  const styles = {
    default: { bg: "var(--color-bg-subtle)", text: "var(--color-text-secondary)" },
    teal:    { bg: "var(--color-teal-bg)",   text: "var(--color-teal-text)" },
  } as const;
  const c = styles[variant];
  return (
    <span
      style={{
        fontSize: "11px",
        padding: "2px 8px",
        borderRadius: "10px",
        background: c.bg,
        color: c.text,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "8px 10px",
  marginBottom: "8px",
  boxSizing: "border-box",
  fontSize: "13px",
  border: "1px solid var(--color-border)",
  borderRadius: "6px",
  fontFamily: "var(--font-sans)",
  outline: "none",
  background: "var(--color-bg)",
  color: "var(--color-text-primary)",
};

function primaryButtonStyle(disabled: boolean): React.CSSProperties {
  return {
    width: "100%",
    padding: "8px 16px",
    fontSize: "13px",
    fontWeight: "500",
    border: "none",
    borderRadius: "6px",
    cursor: disabled ? "not-allowed" : "pointer",
    background: disabled ? "var(--color-bg)" : "var(--color-text-primary)",
    color: disabled ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
    outline: disabled ? "1px solid var(--color-border)" : "none",
  };
}
