import { useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { api, SuggestWirkgefuegeResponse } from "../lib/api";

// ---------------------------------------------------------------------------
// Colour constants from ui_experiment_scope.md
// ---------------------------------------------------------------------------
const C = {
  confirmed: { bg: "#EAF3DE", text: "#3B6D11" },
  rejected: { bg: "#FCEBEB", text: "#A32D2D" },
} as const;

const SLOT_TYPES = [
  "physical_quantity",
  "social_quantity",
  "entity_state",
  "trend",
  "process",
];

const EPISTEMIC_STATUS_OPTIONS = ["incomplete", "axiomatic"];

type SlotEdit = {
  identifier: string;
  slot_type: string;
  rejected: boolean;
};

type RelationEdit = {
  source: string;
  target: string;
  mechanism: string;
  epistemic_status: string;
  rejected: boolean;
};

// ---------------------------------------------------------------------------
// WirkgefuegeVorschlag — Screen 3
// ---------------------------------------------------------------------------

export default function WirkgefuegeVorschlag() {
  const navigate = useNavigate();
  const location = useLocation();
  const { narrativeId } = useParams<{ narrativeId: string }>();

  const state = location.state as {
    suggestion: SuggestWirkgefuegeResponse;
    narrative: { id: string; title: string };
  } | null;

  const suggestion = state?.suggestion ?? null;
  const narrative = state?.narrative ?? null;

  const [slots, setSlots] = useState<SlotEdit[]>(
    () =>
      (suggestion?.suggested_slots ?? []).map((s) => ({
        identifier: s.identifier,
        slot_type: s.slot_type,
        rejected: false,
      }))
  );

  const [relations, setRelations] = useState<RelationEdit[]>(
    () =>
      (suggestion?.suggested_relations ?? []).map((r) => ({
        source: r.source,
        target: r.target,
        mechanism: r.mechanism ?? "",
        epistemic_status: r.epistemic_status,
        rejected: false,
      }))
  );

  const [modelName, setModelName] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!suggestion || !narrative) {
    return (
      <p style={{ color: "#888" }}>
        Bitte Wirkgefüge-Vorschlag vom Analyse-Screen starten.
      </p>
    );
  }

  const fromClaims = suggestion.from_claims;
  const acceptedSlotCount = slots.filter((s) => !s.rejected).length;
  const acceptedRelationCount = relations.filter((r) => !r.rejected).length;

  async function save() {
    if (!modelName.trim()) return;
    setSaving(true);
    setError(null);
    try {
      // 1. Create CausalModel
      const newModel = await api.causalModels.create(modelName.trim());

      // 2. Create accepted slots — build identifier → id map
      const slotIdMap: Record<string, string> = {};
      for (const slot of slots) {
        if (!slot.rejected) {
          const created = await api.causalModels.addSlot(
            newModel.id,
            slot.identifier,
            slot.slot_type,
          );
          slotIdMap[slot.identifier] = created.id;
        }
      }

      // 3. Create accepted relations
      for (const rel of relations) {
        if (rel.rejected) continue;
        const sourceId = slotIdMap[rel.source];
        const targetId = slotIdMap[rel.target];
        if (!sourceId || !targetId) continue; // skip if referenced slot was rejected
        const identifier = `${rel.source}_to_${rel.target}`;
        const created = await api.causalModels.addRelation(
          newModel.id,
          identifier,
          sourceId,
          targetId,
          rel.mechanism.trim() || null,
        );
        if (rel.epistemic_status !== "incomplete") {
          await api.causalModels.updateRelation(
            newModel.id,
            created.id,
            rel.mechanism.trim() || null,
            null,
            rel.epistemic_status,
          );
        }
      }

      // 4. Link narrative to causal model
      await api.narratives.linkToCausalModel(narrativeId!, newModel.id);

      // 5. Link DRAFT claims to this causal model (sets status → LINKED)
      for (const claimId of fromClaims) {
        await api.claims.linkToWirkgefuege(claimId, newModel.id);
      }

      // 6. Navigate to CausalModelEditor
      navigate("/causal-model", { state: { selectedModelId: newModel.id } });
    } catch {
      setError("Speichern fehlgeschlagen. Bitte erneut versuchen.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
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
        ← Zurück zur Analyse
      </button>

      <h2 style={{ marginTop: 0 }}>Wirkgefüge-Vorschlag für: {narrative.title}</h2>

      {/* Slots */}
      <div
        style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}
      >
        <h3
          style={{
            textTransform: "uppercase",
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            color: "#888",
            marginTop: 0,
          }}
        >
          Slots ({acceptedSlotCount})
        </h3>

        {slots.map((slot, i) => (
          <div
            key={i}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 4,
              padding: "0.75rem",
              marginBottom: "0.75rem",
              opacity: slot.rejected ? 0.4 : 1,
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
            }}
          >
            <div style={{ flex: 1 }}>
              <input
                value={slot.identifier}
                onChange={(e) =>
                  setSlots((prev) =>
                    prev.map((s, j) => (j === i ? { ...s, identifier: e.target.value } : s))
                  )
                }
                disabled={slot.rejected}
                style={{
                  fontFamily: "monospace",
                  border: "1px solid #ddd",
                  borderRadius: 3,
                  padding: "0.2rem 0.4rem",
                  fontSize: "0.9rem",
                  width: "100%",
                  boxSizing: "border-box",
                  marginBottom: "0.25rem",
                }}
              />
              <select
                value={slot.slot_type}
                onChange={(e) =>
                  setSlots((prev) =>
                    prev.map((s, j) => (j === i ? { ...s, slot_type: e.target.value } : s))
                  )
                }
                disabled={slot.rejected}
                style={{ fontSize: "0.8rem", padding: "0.2rem" }}
              >
                {SLOT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={() =>
                setSlots((prev) =>
                  prev.map((s, j) => (j === i ? { ...s, rejected: !s.rejected } : s))
                )
              }
              style={{
                background: slot.rejected ? C.rejected.bg : "none",
                border: "1px solid #ddd",
                borderRadius: 3,
                padding: "0.25rem 0.5rem",
                cursor: "pointer",
                fontSize: "0.85rem",
                color: slot.rejected ? C.rejected.text : "inherit",
                flexShrink: 0,
              }}
            >
              ✗
            </button>
          </div>
        ))}
      </div>

      {/* Relations */}
      <div
        style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem", marginBottom: "2rem" }}
      >
        <h3
          style={{
            textTransform: "uppercase",
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            color: "#888",
            marginTop: 0,
          }}
        >
          Kausalrelationen ({acceptedRelationCount})
        </h3>

        {relations.map((rel, i) => (
          <div
            key={i}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 4,
              padding: "0.75rem",
              marginBottom: "0.75rem",
              opacity: rel.rejected ? 0.4 : 1,
            }}
          >
            <p
              style={{
                margin: "0 0 0.5rem",
                fontFamily: "monospace",
                fontSize: "0.85rem",
              }}
            >
              {rel.source} → {rel.target}
            </p>

            <div
              style={{
                display: "flex",
                gap: "0.75rem",
                alignItems: "center",
                marginBottom: "0.25rem",
              }}
            >
              <label style={{ fontSize: "0.8rem", color: "#888", flexShrink: 0 }}>
                Mechanismus:
              </label>
              <input
                value={rel.mechanism}
                onChange={(e) =>
                  setRelations((prev) =>
                    prev.map((r, j) => (j === i ? { ...r, mechanism: e.target.value } : r))
                  )
                }
                disabled={rel.rejected}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: 3,
                  padding: "0.2rem 0.4rem",
                  fontSize: "0.8rem",
                  flex: 1,
                }}
              />
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <label style={{ fontSize: "0.8rem", color: "#888" }}>EpistemicStatus:</label>
                <select
                  value={rel.epistemic_status}
                  onChange={(e) =>
                    setRelations((prev) =>
                      prev.map((r, j) =>
                        j === i ? { ...r, epistemic_status: e.target.value } : r
                      )
                    )
                  }
                  disabled={rel.rejected}
                  style={{ fontSize: "0.8rem", padding: "0.2rem" }}
                >
                  {EPISTEMIC_STATUS_OPTIONS.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={() =>
                  setRelations((prev) =>
                    prev.map((r, j) => (j === i ? { ...r, rejected: !r.rejected } : r))
                  )
                }
                style={{
                  background: rel.rejected ? C.rejected.bg : "none",
                  border: "1px solid #ddd",
                  borderRadius: 3,
                  padding: "0.25rem 0.5rem",
                  cursor: "pointer",
                  fontSize: "0.85rem",
                  color: rel.rejected ? C.rejected.text : "inherit",
                }}
              >
                ✗
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Model name + save */}
      <div style={{ borderTop: "2px solid #e0e0e0", paddingTop: "1rem" }}>
        <label
          style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.25rem" }}
        >
          Modellname
        </label>
        <input
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          placeholder="Modellname eingeben…"
          style={{
            width: "100%",
            padding: "0.4rem",
            marginBottom: "1rem",
            boxSizing: "border-box",
            fontSize: "0.9rem",
          }}
        />
        <button
          onClick={save}
          disabled={saving || !modelName.trim()}
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            background: modelName.trim() ? "#1D9E75" : "#e0e0e0",
            color: modelName.trim() ? "#fff" : "#999",
            border: "none",
            borderRadius: 4,
            cursor: modelName.trim() ? "pointer" : "not-allowed",
            width: "100%",
          }}
        >
          {saving ? "Speichere…" : "CausalModel anlegen und speichern →"}
        </button>
        {error && (
          <p style={{ color: C.rejected.text, marginTop: "0.5rem", fontSize: "0.85rem" }}>
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
