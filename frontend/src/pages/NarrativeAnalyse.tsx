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

const BORDER_OK = "3px solid #1D9E75";
const BORDER_NO = "3px solid #A32D2D";

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
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      {/* Header */}
      <button
        onClick={() => navigate(-1)}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "#4a7aff",
          marginBottom: "1rem",
          padding: 0,
          fontSize: "0.9rem",
        }}
      >
        ← Zurück zu Narrativ
      </button>

      <h2 style={{ marginTop: 0 }}>Analyse: {narrative.title}</h2>
      <p style={{ color: "#888", fontSize: "0.85rem", marginBottom: "2rem" }}>
        {analysis.actors.length} Akteure gefunden · {analysis.claims.length} Claims gefunden
      </p>

      {/* Actors */}
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}>
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
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}>
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
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem" }}>
        {error && (
          <p style={{ color: C.rejected.text, marginBottom: "0.5rem", fontSize: "0.85rem" }}>
            {error}
          </p>
        )}
        <button
          onClick={generateSuggestions}
          disabled={!anyClaimAccepted || suggesting}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            background: anyClaimAccepted ? "#1D9E75" : "#e0e0e0",
            color: anyClaimAccepted ? "#fff" : "#999",
            border: "none",
            borderRadius: 4,
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
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "1rem",
      }}
    >
      <h3
        style={{
          margin: 0,
          textTransform: "uppercase",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          color: "#888",
        }}
      >
        {label}
      </h3>
      <button onClick={onAcceptAll} style={{ fontSize: "0.8rem" }}>
        Alle bestätigen
      </button>
    </div>
  );
}

function borderForState(state: ConfirmState): string {
  if (state === "accepted") return BORDER_OK;
  if (state === "rejected") return BORDER_NO;
  return "1px solid #e0e0e0";
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
          background: state === "accepted" ? C.confirmed.bg : "none",
          border: "1px solid #ddd",
          borderRadius: 3,
          padding: "0.25rem 0.5rem",
          cursor: "pointer",
          fontSize: "0.85rem",
          color: state === "accepted" ? C.confirmed.text : "inherit",
        }}
      >
        ✓
      </button>
      <button
        onClick={onReject}
        style={{
          background: state === "rejected" ? C.rejected.bg : "none",
          border: "1px solid #ddd",
          borderRadius: 3,
          padding: "0.25rem 0.5rem",
          cursor: "pointer",
          fontSize: "0.85rem",
          color: state === "rejected" ? C.rejected.text : "inherit",
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
        border: borderForState(state),
        borderRadius: 4,
        padding: "0.75rem",
        marginBottom: "0.75rem",
        opacity: state === "rejected" ? 0.5 : 1,
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
            style={{ textDecoration: state === "rejected" ? "line-through" : "none" }}
          >
            {actor.label}
          </strong>
          <span style={{ fontSize: "0.75rem", color: "#888" }}>
            {ACTOR_TYPE_LABELS[actor.actor_type] ?? actor.actor_type}
          </span>
        </div>
        {actor.occurrences.length > 0 && (
          <p style={{ margin: "0 0 0.25rem", fontSize: "0.8rem", color: "#888" }}>
            {actor.occurrences.join(", ")}
          </p>
        )}
        {actor.entity_suggestion && (
          <span
            style={{
              fontSize: "0.75rem",
              background: C.entity.bg,
              color: C.entity.text,
              padding: "0.1rem 0.4rem",
              borderRadius: 3,
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
        border: borderForState(state),
        borderRadius: 4,
        padding: "0.75rem",
        marginBottom: "0.75rem",
        opacity: state === "rejected" ? 0.5 : 1,
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
            fontSize: "0.9rem",
          }}
        >
          {claim.label}
        </strong>
        <span
          style={{
            fontSize: "0.75rem",
            background: confStyle.bg,
            color: confStyle.text,
            padding: "0.1rem 0.4rem",
            borderRadius: 3,
            flexShrink: 0,
            marginLeft: "0.5rem",
          }}
        >
          {Math.round(claim.confidence * 100)}%
        </span>
      </div>

      <p
        style={{
          margin: "0 0 0.25rem",
          fontSize: "0.85rem",
          color: "#555",
          fontStyle: "italic",
        }}
      >
        "{claim.text}"
      </p>

      <div style={{ marginBottom: "0.25rem" }}>
        <span
          style={{
            fontSize: "0.75rem",
            background: "#e8f0fe",
            color: "#3c5bb5",
            padding: "0.1rem 0.4rem",
            borderRadius: 3,
          }}
        >
          {CLAIM_TYPE_LABELS[claim.claim_type] ?? claim.claim_type}
        </span>
      </div>

      {ws && (
        <p
          style={{
            margin: "0 0 0.25rem",
            fontSize: "0.8rem",
            color: "#888",
            fontStyle: "italic",
          }}
        >
          {ws.suggestion_type === "slot_zustand"
            ? `→ Slot: ${ws.slot ?? "?"} / ${ws.zustand ?? "?"}`
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
