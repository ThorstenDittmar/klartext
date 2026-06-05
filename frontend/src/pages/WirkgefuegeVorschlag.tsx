import { useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { api, SuggestWirkgefuegeResponse } from "../lib/api";

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
      <p style={{ color: "var(--color-text-tertiary)" }}>
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
      navigate(`/causal-model/${newModel.id}`);
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
          background: "none", border: "none", cursor: "pointer",
          color: "var(--color-text-secondary)", marginBottom: "20px", padding: "0",
          fontSize: "13px",
        }}
      >
        ← Zurück zur Analyse
      </button>

      <h2 style={{ fontSize: "22px", fontWeight: "600", marginTop: "0", marginBottom: "24px" }}>Wirkgefüge-Vorschlag für: {narrative.title}</h2>

      {/* Slots */}
      <div
        style={{ borderTop: "1px solid var(--color-border)", paddingTop: "16px", marginBottom: "32px" }}
      >
        <h3
          style={{
            textTransform: "uppercase" as const, fontSize: "11px", letterSpacing: "0.06em",
            color: "var(--color-text-tertiary)", marginTop: "0", fontWeight: "600",
            padding: "16px 0 8px", borderTop: "1px solid var(--color-border)",
          }}
        >
          Slots ({acceptedSlotCount})
        </h3>

        {slots.map((slot, i) => (
          <div
            key={i}
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: "8px",
              padding: "14px 16px",
              marginBottom: "8px",
              opacity: slot.rejected ? 0.4 : 1,
              display: "flex",
              alignItems: "center",
              gap: "12px",
              background: "var(--color-bg)",
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
                  fontFamily: "var(--font-sans)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "6px 10px",
                  fontSize: "14px",
                  fontWeight: "500",
                  width: "100%",
                  boxSizing: "border-box" as const,
                  marginBottom: "6px",
                  color: "var(--color-text-primary)",
                  background: slot.rejected ? "var(--color-bg-subtle)" : "var(--color-bg)",
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
                style={{
                  fontSize: "11px",
                  padding: "2px 6px",
                  border: "1px solid var(--color-border)",
                  borderRadius: "10px",
                  background: "var(--color-bg-subtle)",
                  color: "var(--color-text-secondary)",
                  cursor: "pointer",
                }}
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
                background: slot.rejected ? "var(--color-red-bg)" : "none",
                border: "1px solid var(--color-border)",
                borderRadius: "6px",
                padding: "0",
                cursor: "pointer",
                fontSize: "14px",
                color: slot.rejected ? "var(--color-red-text)" : "var(--color-text-tertiary)",
                width: "30px",
                height: "30px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
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
        style={{ borderTop: "1px solid var(--color-border)", paddingTop: "16px", marginBottom: "32px" }}
      >
        <h3
          style={{
            textTransform: "uppercase" as const, fontSize: "11px", letterSpacing: "0.06em",
            color: "var(--color-text-tertiary)", marginTop: "0", fontWeight: "600",
            padding: "16px 0 8px", borderTop: "1px solid var(--color-border)",
          }}
        >
          Kausalrelationen ({acceptedRelationCount})
        </h3>

        {relations.map((rel, i) => (
          <div
            key={i}
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: "8px",
              padding: "14px 16px",
              marginBottom: "8px",
              opacity: rel.rejected ? 0.4 : 1,
              background: "var(--color-bg)",
            }}
          >
            <p
              style={{
                margin: "0 0 10px",
                fontFamily: "var(--font-sans)",
                fontSize: "14px",
                fontWeight: "500",
                color: "var(--color-text-primary)",
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
              <label style={{ fontSize: "12px", color: "var(--color-text-secondary)", flexShrink: 0 }}>
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
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "6px 10px",
                  fontSize: "13px",
                  fontStyle: "italic",
                  flex: 1,
                  fontFamily: "var(--font-sans)",
                  color: "var(--color-text-secondary)",
                  background: rel.rejected ? "var(--color-bg-subtle)" : "var(--color-bg)",
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
                <label style={{ fontSize: "12px", color: "var(--color-text-secondary)" }}>EpistemicStatus:</label>
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
                  style={{
                    fontSize: "11px",
                    padding: "2px 6px",
                    border: "1px solid var(--color-border)",
                    borderRadius: "10px",
                    background: "var(--color-bg-subtle)",
                    color: "var(--color-text-secondary)",
                    cursor: "pointer",
                  }}
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
                  background: rel.rejected ? "var(--color-red-bg)" : "none",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "0",
                  cursor: "pointer",
                  fontSize: "14px",
                  color: rel.rejected ? "var(--color-red-text)" : "var(--color-text-tertiary)",
                  width: "30px",
                  height: "30px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                ✗
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Model name + save */}
      <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "16px" }}>
        <label
          style={{ fontSize: "12px", color: "var(--color-text-secondary)", display: "block", marginBottom: "6px" }}
        >
          Modellname
        </label>
        <input
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          placeholder="Modellname eingeben…"
          style={{
            width: "100%",
            padding: "10px 12px",
            marginBottom: "12px",
            boxSizing: "border-box" as const,
            fontSize: "14px",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            fontFamily: "var(--font-sans)",
            color: "var(--color-text-primary)",
          }}
        />
        <button
          onClick={save}
          disabled={saving || !modelName.trim()}
          style={{
            background: modelName.trim() ? "var(--color-text-primary)" : "var(--color-bg-subtle)",
            color: modelName.trim() ? "var(--color-text-inverse)" : "var(--color-text-tertiary)",
            border: "none",
            borderRadius: "6px",
            padding: "10px 16px",
            fontSize: "14px",
            fontWeight: "500",
            cursor: modelName.trim() ? "pointer" : "not-allowed",
            width: "100%",
          }}
        >
          {saving ? "Speichere…" : "CausalModel anlegen und speichern →"}
        </button>
        {error && (
          <p style={{ color: "var(--color-red-text)", marginTop: "8px", fontSize: "13px" }}>
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
