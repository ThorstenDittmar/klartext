import { useEffect, useState, type ReactNode } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api, type Actor, type Claim, type Narrative } from "../lib/api";

// ---------------------------------------------------------------------------
// Label maps
// ---------------------------------------------------------------------------

const STATUS_LABELS: Record<string, string> = {
  draft: "Entwurf",
  confirmed: "Bestätigt",
  linked: "Verknüpft",
  rejected: "Verworfen",
};

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  draft:     { bg: "var(--color-amber-bg)",  text: "var(--color-amber-text)" },
  confirmed: { bg: "var(--color-green-bg)",  text: "var(--color-green-text)" },
  linked:    { bg: "var(--color-teal-bg)",   text: "var(--color-teal-text)" },
  rejected:  { bg: "var(--color-red-bg)",    text: "var(--color-red-text)" },
};

const ACTOR_TYPE_LABELS: Record<string, string> = {
  individual:      "Figur",
  organisation:    "Organisation",
  group:           "Gruppe",
  institution:     "Institution",
  abstract_entity: "Abstrakte Entität",
};

const CLAIM_TYPE_LABELS: Record<string, string> = {
  empirical:      "Empirisch",
  causal:         "Kausal",
  definitional:   "Definitorisch",
  normative:      "Normativ",
  prognostic:     "Prognostisch",
  counterfactual: "Kontrafaktisch",
  methodological: "Methodisch",
  uncertainty:    "Unsicherheit",
};

type ViewMode = "scenes" | "fulltext";

// ---------------------------------------------------------------------------
// Text highlighting — marks actor names (green) and claim texts (amber)
// within a plain text string. Returns React nodes.
// Only active in fulltext mode.
// ---------------------------------------------------------------------------

function highlightText(
  text: string,
  actors: Actor[],
  claims: Claim[],
): ReactNode[] {
  type Highlight = {
    start: number;
    end: number;
    label: string;
    status: string;
    kind: "actor" | "claim";
  };

  const highlights: Highlight[] = [];

  // Actor names — case-insensitive substring search
  for (const actor of actors) {
    if (!actor.label) continue;
    const escaped = actor.label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(escaped, "gi");
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      highlights.push({
        start: m.index,
        end: m.index + m[0].length,
        label: actor.label,
        status: "confirmed",
        kind: "actor",
      });
    }
  }

  // Claim original texts — exact substring search
  for (const claim of claims) {
    if (!claim.text) continue;
    let idx = 0;
    while ((idx = text.indexOf(claim.text, idx)) !== -1) {
      highlights.push({
        start: idx,
        end: idx + claim.text.length,
        label: claim.label,
        status: claim.status,
        kind: "claim",
      });
      idx += claim.text.length;
    }
  }

  // Sort by start position; prefer longer match on ties
  highlights.sort((a, b) => a.start - b.start || b.end - a.end);

  // Remove overlapping highlights (keep first non-overlapping match)
  const noOverlap: Highlight[] = [];
  let cursor = 0;
  for (const h of highlights) {
    if (h.start >= cursor) {
      noOverlap.push(h);
      cursor = h.end;
    }
  }

  // Build React nodes: plain text between marks, <mark> for highlights
  const nodes: ReactNode[] = [];
  let pos = 0;
  for (const h of noOverlap) {
    if (h.start > pos) {
      nodes.push(text.slice(pos, h.start));
    }
    const bg    = h.kind === "actor" ? "var(--color-green-bg)"  : "var(--color-amber-bg)";
    const color = h.kind === "actor" ? "var(--color-green-text)" : "var(--color-amber-text)";
    const statusLabel = STATUS_LABELS[h.status] ?? h.status;
    nodes.push(
      <mark
        key={`${h.start}-${h.end}`}
        title={`${h.label} · ${statusLabel}`}
        style={{
          background: bg,
          color,
          borderRadius: "2px",
          padding: "1px 0",
          cursor: "help",
          fontStyle: "inherit",
        }}
      >
        {text.slice(h.start, h.end)}
      </mark>,
    );
    pos = h.end;
  }
  if (pos < text.length) nodes.push(text.slice(pos));
  return nodes;
}

// ---------------------------------------------------------------------------
// NarrativeDetail — Screen 1
// ---------------------------------------------------------------------------

export default function NarrativeDetail() {
  const { narrativeId } = useParams<{ narrativeId: string }>();
  const navigate = useNavigate();

  const [narrative, setNarrative] = useState<Narrative | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [expandedSceneId, setExpandedSceneId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("scenes");
  const [analysing, setAnalysing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!narrativeId) return;
    Promise.all([
      api.narratives.get(narrativeId),
      api.narratives.getClaims(narrativeId),
    ])
      .then(([narr, cls]) => {
        setNarrative(narr);
        setClaims(cls);
      })
      .catch(() => setError("Narrativ konnte nicht geladen werden."));
  }, [narrativeId]);

  async function analyseNarrative() {
    if (!narrativeId || !narrative) return;
    setAnalysing(true);
    setError(null);
    try {
      const analysis = await api.narratives.analyse(narrativeId);
      navigate(`/narrative/${narrativeId}/analyse`, {
        state: { analysis, narrative: { id: narrativeId, title: narrative.title } },
      });
    } catch {
      setError("Analyse fehlgeschlagen. Bitte erneut versuchen.");
    } finally {
      setAnalysing(false);
    }
  }

  if (error && !narrative) {
    return <p style={{ color: "var(--color-red-text)", padding: "32px 24px" }}>{error}</p>;
  }
  if (!narrative) {
    return <p style={{ color: "var(--color-text-tertiary)", padding: "32px 24px" }}>Lade…</p>;
  }

  const sortedScenes = [...narrative.scenes].sort((a, b) => a.position - b.position);
  const hasHighlightableContent = narrative.actors.length > 0 || claims.length > 0;

  return (
    <div style={{ maxWidth: "760px", margin: "0 auto", padding: "32px 24px" }}>
      {/* Back */}
      <button
        onClick={() => navigate("/")}
        style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--color-text-secondary)", marginBottom: "20px",
          padding: "0", fontSize: "13px",
        }}
      >
        ← Meine Werke
      </button>

      {/* Header */}
      <h1 style={{
        fontSize: "24px", fontWeight: "700", marginTop: "0",
        marginBottom: "4px", color: "var(--color-text-primary)",
      }}>
        {narrative.title}
      </h1>
      <p style={{ fontSize: "13px", color: "var(--color-text-secondary)", margin: "0 0 32px" }}>
        {narrative.scenes.length} Szenen · {narrative.actors.length} Akteure · {claims.length} Claims
        {narrative.causal_model_id && " · 🔗 Wirkgefüge verknüpft"}
      </p>

      {/* ------------------------------------------------------------------ */}
      {/* Scenes section — with view-mode toggle                             */}
      {/* ------------------------------------------------------------------ */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "16px", borderTop: "1px solid var(--color-border)", marginBottom: "10px" }}>
        <h3 style={{
          fontSize: "11px", fontWeight: "600", textTransform: "uppercase",
          letterSpacing: "0.06em", color: "var(--color-text-tertiary)", margin: "0",
        }}>
          Szenen ({narrative.scenes.length})
        </h3>

        {/* Segmented toggle: Szenen / Volltext */}
        {narrative.scenes.length > 0 && (
          <div
            role="group"
            aria-label="Ansichtsmodus"
            style={{
              display: "flex",
              gap: "2px",
              background: "var(--color-bg-subtle)",
              borderRadius: "6px",
              padding: "2px",
            }}
          >
            {(["scenes", "fulltext"] as ViewMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                aria-pressed={viewMode === mode}
                style={{
                  padding: "4px 12px",
                  fontSize: "12px",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  background: viewMode === mode ? "var(--color-bg)" : "transparent",
                  color: viewMode === mode ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                  fontWeight: viewMode === mode ? "500" : "400",
                  boxShadow: viewMode === mode ? "0 1px 2px rgba(0,0,0,0.08)" : "none",
                  transition: "background 0.1s, color 0.1s",
                }}
              >
                {mode === "scenes" ? "Szenen" : "Volltext"}
              </button>
            ))}
          </div>
        )}
      </div>

      {narrative.scenes.length === 0 ? (
        <EmptyHint>Keine Szenen vorhanden.</EmptyHint>
      ) : viewMode === "scenes" ? (
        /* ---- Szenen-Modus: aufklappbare Liste ---- */
        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 28px" }}>
          {sortedScenes.map((scene) => (
            <li key={scene.id} style={{ marginBottom: "6px" }}>
              <button
                onClick={() => setExpandedSceneId(expandedSceneId === scene.id ? null : scene.id)}
                style={{
                  width: "100%", background: "none",
                  border: "1px solid var(--color-border)", borderRadius: "6px",
                  padding: "10px 14px", cursor: "pointer", textAlign: "left",
                  fontSize: "13px", color: "var(--color-text-primary)",
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                }}
              >
                <span>
                  <span style={{ color: "var(--color-text-tertiary)", marginRight: "8px" }}>{scene.position}.</span>
                  {scene.title}
                </span>
                <span style={{ color: "var(--color-text-tertiary)", fontSize: "11px" }}>
                  {expandedSceneId === scene.id ? "▲" : "▼"}
                </span>
              </button>
              {expandedSceneId === scene.id && (
                <div style={{
                  padding: "12px 14px",
                  borderLeft: "3px solid var(--color-blue-text)",
                  background: "var(--color-bg-subtle)",
                  fontSize: "13px", lineHeight: "1.7",
                  color: "var(--color-text-secondary)",
                  whiteSpace: "pre-wrap",
                }}>
                  {scene.text}
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        /* ---- Volltext-Modus: kontinuierlicher Fliesstext ---- */
        <div style={{ marginBottom: "28px" }}>
          {hasHighlightableContent && (
            <p style={{
              fontSize: "11px", color: "var(--color-text-tertiary)",
              margin: "0 0 12px", fontStyle: "italic",
            }}>
              Akteure und Claims sind im Text markiert — hover für Details.
            </p>
          )}
          {sortedScenes.map((scene) => (
            <p
              key={scene.id}
              style={{
                fontSize: "15px",
                lineHeight: "1.8",
                color: "var(--color-text-primary)",
                margin: "0 0 20px",
                whiteSpace: "pre-wrap",
              }}
            >
              {hasHighlightableContent
                ? highlightText(scene.text, narrative.actors, claims)
                : scene.text}
            </p>
          ))}
        </div>
      )}

      {/* Actors */}
      <SectionHeader label={`Akteure (${narrative.actors.length})`} />
      {narrative.actors.length === 0 ? (
        <EmptyHint style={{ marginBottom: "28px" }}>Noch keine Akteure bestätigt.</EmptyHint>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 28px" }}>
          {narrative.actors.map((actor) => (
            <li key={actor.id} style={{
              display: "flex", alignItems: "center", gap: "8px",
              padding: "8px 0", borderBottom: "1px solid var(--color-border)",
            }}>
              <span style={{ fontSize: "13px", color: "var(--color-text-primary)", flex: 1 }}>
                👤 {actor.label}
              </span>
              <span style={{
                fontSize: "11px", padding: "2px 8px", borderRadius: "10px",
                background: "var(--color-bg-subtle)", color: "var(--color-text-secondary)",
              }}>
                {ACTOR_TYPE_LABELS[actor.actor_type] ?? actor.actor_type}
              </span>
            </li>
          ))}
        </ul>
      )}

      {/* Claims */}
      <SectionHeader label={`Claims (${claims.length})`} />
      {claims.length === 0 ? (
        <EmptyHint style={{ marginBottom: "28px" }}>Noch keine Claims. Erst "Analysieren" klicken.</EmptyHint>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 28px" }}>
          {claims.map((claim) => {
            const statusColor = STATUS_COLORS[claim.status] ?? STATUS_COLORS["draft"];
            return (
              <li key={claim.id} style={{
                padding: "10px 0", borderBottom: "1px solid var(--color-border)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <span style={{
                    fontSize: "13px", fontWeight: "500",
                    color: "var(--color-text-primary)", flex: 1,
                  }}>
                    {claim.label}
                  </span>
                  <span style={{
                    fontSize: "11px", padding: "2px 8px", borderRadius: "10px",
                    background: statusColor.bg, color: statusColor.text,
                  }}>
                    {STATUS_LABELS[claim.status] ?? claim.status}
                  </span>
                  <span style={{
                    fontSize: "11px", padding: "2px 8px", borderRadius: "10px",
                    background: "var(--color-bg-subtle)", color: "var(--color-text-secondary)",
                  }}>
                    {CLAIM_TYPE_LABELS[claim.typ] ?? claim.typ}
                  </span>
                </div>
                <p style={{
                  margin: 0, fontSize: "12px",
                  color: "var(--color-text-secondary)", fontStyle: "italic",
                }}>
                  "{claim.text}"
                </p>
              </li>
            );
          })}
        </ul>
      )}

      {/* Analysieren */}
      <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "24px", marginTop: "8px" }}>
        <button
          onClick={analyseNarrative}
          disabled={analysing}
          style={{
            width: "100%", padding: "12px 16px", fontSize: "14px",
            fontWeight: "500", border: "none", borderRadius: "8px",
            cursor: analysing ? "not-allowed" : "pointer",
            background: analysing ? "var(--color-bg-subtle)" : "var(--color-text-primary)",
            color: analysing ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
          }}
        >
          {analysing ? "⏳ Analyse läuft…" : "Analysieren →"}
        </button>
        {error && (
          <p style={{ color: "var(--color-red-text)", fontSize: "13px", marginTop: "8px" }}>{error}</p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SectionHeader({ label }: { label: string }) {
  return (
    <h3 style={{
      fontSize: "11px", fontWeight: "600", textTransform: "uppercase",
      letterSpacing: "0.06em", color: "var(--color-text-tertiary)",
      margin: "0 0 10px", padding: "16px 0 8px",
      borderTop: "1px solid var(--color-border)",
    }}>
      {label}
    </h3>
  );
}

function EmptyHint({ children, style }: { children: ReactNode; style?: React.CSSProperties }) {
  return (
    <p style={{ color: "var(--color-text-tertiary)", fontSize: "13px", margin: "0 0 28px", ...style }}>
      {children}
    </p>
  );
}
