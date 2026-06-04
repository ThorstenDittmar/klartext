import { useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import {
  api,
  AnalyseNarrativeResponse,
  ActorSuggestion,
  ClaimSuggestion,
} from "../lib/api";

// ---------------------------------------------------------------------------
// Colour constants from ui_experiment_scope.md
// ---------------------------------------------------------------------------
const C = {
  confirmed: { bg: "#EAF3DE", text: "#3B6D11" },
  draft: { bg: "#FAEEDA", text: "#854F0B" },
  rejected: { bg: "#FCEBEB", text: "#A32D2D" },
  entity: { bg: "#E1F5EE", text: "#0F6E56" },
} as const;

type ConfirmState = "pending" | "accepted" | "rejected";

const ACTOR_TYPE_LABELS: Record<string, string> = {
  individual: "Figur",
  organisation: "Organisation",
  group: "Gruppe",
  institution: "Institution",
  abstract_entity: "Abstrakte Entität",
};

const CLAIM_TYPE_LABELS: Record<string, string> = {
  empirical: "Empirisch",
  causal: "Kausal",
  definitional: "Definitorisch",
  normative: "Normativ",
  prognostic: "Prognostisch",
  counterfactual: "Kontrafaktisch",
  methodological: "Methodisch",
  uncertainty: "Unsicherheit",
};

// ---------------------------------------------------------------------------
// NarrativeAnalyse — Screen 2
// ---------------------------------------------------------------------------

export default function NarrativeAnalyse() {
  const navigate = useNavigate();
  const location = useLocation();
  const { narrativeId } = useParams<{ narrativeId: string }>();

  const state = location.state as {
    analysis: AnalyseNarrativeResponse;
    narrative: { id: string; title: string };
  } | null;

  const analysis = state?.analysis ?? null;
  const narrative = state?.narrative ?? null;

  const [actorStates, setActorStates] = useState<ConfirmState[]>(
    () => (analysis?.actors ?? []).map(() => "pending" as ConfirmState)
  );
  const [claimStates, setClaimStates] = useState<ConfirmState[]>(
    () => (analysis?.claims ?? []).map(() => "pending" as ConfirmState)
  );
  const [suggesting, setSuggesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!analysis || !narrative) {
    return (
      <p style={{ color: "#888" }}>
        Bitte Analyse vom Narrativ-Editor starten.
      </p>
    );
  }

  const anyClaimAccepted = claimStates.some((s) => s === "accepted");

  async function generateSuggestions() {
    setSuggesting(true);
    setError(null);
    try {
      const suggestion = await api.narratives.suggestWirkgefuege(narrativeId!);
      navigate(`/narrative/${narrativeId}/wirkgefuege-vorschlag`, {
        state: { suggestion, narrative },
      });
    } catch {
      setError("Wirkgefüge-Vorschläge konnten nicht generiert werden.");
    } finally {
      setSuggesting(false);
    }
  }

  return (
    <div style={{ maxWidth: "760px", margin: "0 auto", padding: "32px 24px" }}>
      {/* Header */}
      <button
        onClick={() => navigate(-1)}
        style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--color-text-secondary)", marginBottom: "20px", padding: "0",
          fontSize: "13px",
        }}
      >
        ← Zurück zu Narrativ
      </button>

      <h2 style={{ fontSize: "22px", fontWeight: "600", marginTop: "0", marginBottom: "4px", color: "var(--color-text-primary)" }}>Analyse: {narrative.title}</h2>
      <p style={{ fontSize: "13px", color: "var(--color-text-secondary)", marginBottom: "24px", marginTop: "0" }}>
        {analysis.actors.length} Akteure gefunden · {analysis.claims.length} Claims gefunden
      </p>

      {/* Actors */}
      <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "1rem", marginBottom: "2rem" }}>
        <SectionHeader
          label="Akteure"
          onAcceptAll={() => setActorStates(analysis.actors.map(() => "accepted"))}
        />
        {analysis.actors.map((actor, i) => (
          <ActorCard
            key={i}
            actor={actor}
            state={actorStates[i]}
            onAccept={() =>
              setActorStates((prev) => prev.map((s, j) => (j === i ? "accepted" : s)))
            }
            onReject={() =>
              setActorStates((prev) => prev.map((s, j) => (j === i ? "rejected" : s)))
            }
          />
        ))}
      </div>

      {/* Claims */}
      <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "1rem", marginBottom: "2rem" }}>
        <SectionHeader
          label="Claims"
          onAcceptAll={() => setClaimStates(analysis.claims.map(() => "accepted"))}
        />
        {analysis.claims.map((claim, i) => (
          <ClaimCard
            key={i}
            claim={claim}
            state={claimStates[i]}
            onAccept={() =>
              setClaimStates((prev) => prev.map((s, j) => (j === i ? "accepted" : s)))
            }
            onReject={() =>
              setClaimStates((prev) => prev.map((s, j) => (j === i ? "rejected" : s)))
            }
          />
        ))}
      </div>

      {/* Generate button */}
      <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "1rem" }}>
        {error && (
          <p style={{ color: "var(--color-red-text)", marginBottom: "8px", fontSize: "13px", margin: "0 0 8px" }}>
            {error}
          </p>
        )}
        <button
          onClick={generateSuggestions}
          disabled={!anyClaimAccepted || suggesting}
          style={{
            background: anyClaimAccepted ? "#1A1A1A" : "var(--color-bg-subtle)",
            color: anyClaimAccepted ? "#FFFFFF" : "var(--color-text-tertiary)",
            border: "none",
            borderRadius: "6px",
            padding: "10px 16px",
            fontSize: "14px",
            fontWeight: "500",
            cursor: anyClaimAccepted ? "pointer" : "not-allowed",
            width: "100%",
          }}
        >
          {suggesting ? "Generiere…" : "Wirkgefüge-Vorschläge generieren →"}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SectionHeader({
  label,
  onAcceptAll,
}: {
  label: string;
  onAcceptAll: () => void;
}) {
  return (
    <div
      style={{
        display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px",
        padding: "16px 0 8px", borderTop: "1px solid var(--color-border)",
      }}
    >
      <h3
        style={{
          margin: "0", fontSize: "11px", textTransform: "uppercase" as const,
          letterSpacing: "0.06em", color: "var(--color-text-tertiary)", fontWeight: "600",
        }}
      >
        {label}
      </h3>
      <button onClick={onAcceptAll} style={{ fontSize: "12px", padding: "5px 12px", border: "1px solid var(--color-border)", borderRadius: "6px", background: "var(--color-bg)", cursor: "pointer", color: "var(--color-text-secondary)" }}>
        Alle bestätigen
      </button>
    </div>
  );
}

function ConfirmButtons({
  state,
  onAccept,
  onReject,
}: {
  state: ConfirmState;
  onAccept: () => void;
  onReject: () => void;
}) {
  return (
    <div style={{ display: "flex", gap: "0.5rem", flexShrink: 0 }}>
      <button
        onClick={onAccept}
        style={{
          background: state === "accepted" ? "var(--color-green-bg)" : "var(--color-bg)",
          border: state === "accepted" ? "1px solid #3B6D11" : "1px solid var(--color-border)",
          borderRadius: "6px",
          padding: "0",
          cursor: "pointer",
          fontSize: "14px",
          color: state === "accepted" ? "var(--color-green-text)" : "var(--color-text-secondary)",
          width: "30px",
          height: "30px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        ✓
      </button>
      <button
        onClick={onReject}
        style={{
          background: state === "rejected" ? "var(--color-red-bg)" : "var(--color-bg)",
          border: state === "rejected" ? "1px solid #A32D2D" : "1px solid var(--color-border)",
          borderRadius: "6px",
          padding: "0",
          cursor: "pointer",
          fontSize: "14px",
          color: state === "rejected" ? "var(--color-red-text)" : "var(--color-text-secondary)",
          width: "30px",
          height: "30px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        ✗
      </button>
    </div>
  );
}

function ActorCard({
  actor,
  state,
  onAccept,
  onReject,
}: {
  actor: ActorSuggestion;
  state: ConfirmState;
  onAccept: () => void;
  onReject: () => void;
}) {
  return (
    <div
      style={{
        border: "1px solid var(--color-border)",
        borderLeft: state === "accepted" ? "3px solid #3B6D11" : "1px solid var(--color-border)",
        borderRadius: "8px",
        padding: "14px 16px",
        marginBottom: "8px",
        background: "var(--color-bg)",
        opacity: state === "rejected" ? 0.4 : 1,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
      }}
    >
      <div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            marginBottom: "0.25rem",
          }}
        >
          <span>👤</span>
          <strong
            style={{ textDecoration: state === "rejected" ? "line-through" : "none", fontSize: "14px", fontWeight: "500", color: "var(--color-text-primary)" }}
          >
            {actor.label}
          </strong>
          <span style={{ fontSize: "11px", color: "var(--color-text-secondary)", background: "var(--color-bg-subtle)", padding: "2px 8px", borderRadius: "10px", marginLeft: "6px" }}>
            {ACTOR_TYPE_LABELS[actor.actor_type] ?? actor.actor_type}
          </span>
        </div>
        {actor.occurrences.length > 0 && (
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "var(--color-text-secondary)" }}>
            {actor.occurrences.join(", ")}
          </p>
        )}
        {actor.entity_suggestion && (
          <span
            style={{
              fontSize: "12px", background: "var(--color-teal-bg)", color: "var(--color-teal-text)",
              padding: "2px 8px", borderRadius: "10px", display: "inline-block", marginTop: "6px",
            }}
          >
            → Entity-Vorschlag: "{actor.entity_suggestion}"
          </span>
        )}
      </div>
      <ConfirmButtons state={state} onAccept={onAccept} onReject={onReject} />
    </div>
  );
}

function confidenceStyle(conf: number) {
  if (conf >= 0.8) return C.confirmed;
  if (conf >= 0.6) return C.draft;
  return C.rejected;
}

function ClaimCard({
  claim,
  state,
  onAccept,
  onReject,
}: {
  claim: ClaimSuggestion;
  state: ConfirmState;
  onAccept: () => void;
  onReject: () => void;
}) {
  const confStyle = confidenceStyle(claim.confidence);
  const ws = claim.wirkgefuege_suggestion;

  return (
    <div
      style={{
        border: "1px solid var(--color-border)",
        borderLeft: state === "accepted" ? "3px solid #3B6D11" : "1px solid var(--color-border)",
        borderRadius: "8px",
        padding: "14px 16px",
        marginBottom: "8px",
        background: "var(--color-bg)",
        opacity: state === "rejected" ? 0.4 : 1,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "0.25rem",
        }}
      >
        <strong
          style={{
            textDecoration: state === "rejected" ? "line-through" : "none",
            fontSize: "14px", fontWeight: "500", color: "var(--color-text-primary)",
          }}
        >
          {claim.label}
        </strong>
        <span
          style={{
            fontSize: "12px", fontWeight: "500", padding: "2px 7px", borderRadius: "10px",
            background: confStyle.bg, color: confStyle.text, flexShrink: 0, marginLeft: "8px",
          }}
        >
          {Math.round(claim.confidence * 100)}%
        </span>
      </div>

      <p
        style={{
          margin: "4px 0 4px", fontSize: "13px", color: "var(--color-text-secondary)", fontStyle: "italic",
        }}
      >
        "{claim.text}"
      </p>

      <div style={{ marginBottom: "0.25rem" }}>
        <span
          style={{
            fontSize: "11px", background: "var(--color-bg-subtle)", color: "var(--color-text-secondary)",
            padding: "2px 8px", borderRadius: "10px",
          }}
        >
          {CLAIM_TYPE_LABELS[claim.claim_type] ?? claim.claim_type}
        </span>
      </div>

      {ws && (
        <p
          style={{
            margin: "4px 0 0", fontSize: "12px", color: "var(--color-text-tertiary)", fontStyle: "italic",
          }}
        >
          {ws.suggestion_type === "slot_state"
            ? `→ Slot: ${ws.slot ?? "?"} / ${ws.slot_state ?? "?"}`
            : `→ ${ws.source_slot ?? "?"} → ${ws.target_slot ?? "?"}`}
        </p>
      )}

      <div
        style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", marginTop: "0.5rem" }}
      >
        <ConfirmButtons state={state} onAccept={onAccept} onReject={onReject} />
      </div>
    </div>
  );
}
