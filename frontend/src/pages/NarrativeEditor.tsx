import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Actor,
  AnalyseNarrativeResponse,
  api,
  CausalModel,
  Claim,
  ConsistencyResult,
  Narrative,
  NarrativeSummary,
  Scene,
} from "../lib/api";

// ---------------------------------------------------------------------------
// Claim type labels (German — user-facing)
// ---------------------------------------------------------------------------

const ACTOR_TYPE_LABELS: Record<string, string> = {
  individual: "Figur",
  organisation: "Organisation",
  group: "Gruppe",
  institution: "Institution",
  abstract_entity: "Abstrakte Entität",
};

const ACTOR_TYPES = Object.entries(ACTOR_TYPE_LABELS);

const CLAIM_TYPE_LABELS: Record<string, string> = {
  empirischer_claim: "Empirisch",
  kausaler_claim: "Kausal",
  definitorischer_claim: "Definitorisch",
  normativer_claim: "Normativ",
  prognostischer_claim: "Prognostisch",
  kontrafaktischer_claim: "Kontrafaktisch",
  methodischer_claim: "Methodisch",
  unsicherheitsclaim: "Unsicherheit",
};

// ---------------------------------------------------------------------------
// NarrativeEditor — three-column author environment
//
// Column 1: Narrative list + create form
// Column 2: Scene list for selected narrative
// Column 3: Selected scene — full text, claim extraction, consistency check
// ---------------------------------------------------------------------------

export default function NarrativeEditor() {
  // Narratives
  const [summaries, setSummaries] = useState<NarrativeSummary[]>([]);
  const [selected, setSelected] = useState<Narrative | null>(null);

  // Scene selection
  const [selectedSceneId, setSelectedSceneId] = useState<string | null>(null);
  const [showAddScene, setShowAddScene] = useState(false);

  // Claims — loaded per scene on demand
  const [claimsByScene, setClaimsByScene] = useState<Record<string, Claim[]>>({});
  const [extracting, setExtracting] = useState(false);

  // Consistency check
  const [causalModels, setCausalModels] = useState<CausalModel[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>("");
  const [consistencyResult, setConsistencyResult] = useState<ConsistencyResult | null>(null);
  const [checking, setChecking] = useState(false);

  // Create narrative form
  const [newTitle, setNewTitle] = useState("");

  // Import narrative form
  const [importPath, setImportPath] = useState("");
  const [importing, setImporting] = useState(false);

  // Add scene form
  const [sceneTitle, setSceneTitle] = useState("");
  const [sceneText, setSceneText] = useState("");

  // Actor interaction
  const [selectedActorId, setSelectedActorId] = useState<string | null>(null);
  const [showAddActor, setShowAddActor] = useState(false);

  // Add / edit actor form
  const [actorLabel, setActorLabel] = useState("");
  const [actorType, setActorType] = useState("individual");
  const [actorNotes, setActorNotes] = useState("");

  // UI state
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // Analyse narrative
  const [analysing, setAnalysing] = useState(false);
  const [analyseError, setAnalyseError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.narratives.list(), api.causalModels.list()])
      .then(([narrs, models]) => {
        setSummaries(narrs);
        setCausalModels(models);
        if (models.length > 0) setSelectedModelId(models[0].id);
      })
      .catch(() => setError("API nicht erreichbar"));
  }, []);

  // Loads a narrative by ID and resets per-scene state.
  async function selectNarrative(id: string) {
    try {
      const narrative = await api.narratives.get(id);
      setSelected(narrative);
      setSelectedSceneId(null);
      setShowAddScene(false);
      setConsistencyResult(null);
    } catch {
      setError("Narrativ konnte nicht geladen werden.");
    }
  }

  async function importNarrative() {
    if (!importPath.trim()) return;
    setImporting(true);
    setError(null);
    try {
      const narrative = await api.narratives.importFromPath(importPath.trim());
      setSummaries((prev) => [...prev, { id: narrative.id, title: narrative.title, causal_model_id: narrative.causal_model_id }]);
      setSelected(narrative);
      setSelectedSceneId(null);
      setShowAddScene(false);
      setImportPath("");
    } catch {
      setError("Import fehlgeschlagen. Pfad prüfen.");
    } finally {
      setImporting(false);
    }
  }

  async function createNarrative() {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      const narrative = await api.narratives.create(newTitle.trim());
      setSummaries((prev) => [...prev, { id: narrative.id, title: narrative.title, causal_model_id: narrative.causal_model_id }]);
      setSelected(narrative);
      setSelectedSceneId(null);
      setShowAddScene(false);
      setNewTitle("");
    } catch {
      setError("Narrativ konnte nicht erstellt werden.");
    } finally {
      setLoading(false);
    }
  }

  // Selects a scene and lazily loads its claims if not already cached.
  function selectScene(scene: Scene) {
    setSelectedSceneId(scene.id);
    setShowAddScene(false);
    setConsistencyResult(null);

    if (!(scene.id in claimsByScene)) {
      api.narratives
        .getSceneClaims(selected!.id, scene.id)
        .then((claims) =>
          setClaimsByScene((prev) => ({ ...prev, [scene.id]: claims }))
        )
        .catch(() =>
          setClaimsByScene((prev) => ({ ...prev, [scene.id]: [] }))
        );
    }
  }

  async function extractClaims() {
    if (!selected || !selectedSceneId) return;
    setExtracting(true);
    try {
      const result = await api.narratives.extractClaims(selected.id, selectedSceneId);
      setClaimsByScene((prev) => ({ ...prev, [selectedSceneId]: result.claims }));
    } catch {
      setError("Claims konnten nicht extrahiert werden.");
    } finally {
      setExtracting(false);
    }
  }

  async function checkConsistency() {
    if (!selected || !selectedSceneId || !selectedModelId) return;
    const scene = selected.scenes.find((s) => s.id === selectedSceneId);
    if (!scene) return;
    setChecking(true);
    setConsistencyResult(null);
    try {
      const result = await api.causalModels.checkConsistency(selectedModelId, scene.text);
      setConsistencyResult(result);
    } catch {
      setError("Konsistenzprüfung fehlgeschlagen.");
    } finally {
      setChecking(false);
    }
  }

  async function addScene() {
    if (!selected || !sceneTitle.trim() || !sceneText.trim()) return;
    setLoading(true);
    try {
      const scene = await api.narratives.addScene(
        selected.id,
        sceneTitle.trim(),
        sceneText.trim()
      );
      setSelected((prev) =>
        prev ? { ...prev, scenes: [...prev.scenes, scene] } : prev
      );
      setClaimsByScene((prev) => ({ ...prev, [scene.id]: [] }));
      setSelectedSceneId(scene.id);
      setShowAddScene(false);
      setSceneTitle("");
      setSceneText("");
    } catch {
      setError("Szene konnte nicht hinzugefügt werden.");
    } finally {
      setLoading(false);
    }
  }

  function openAddActor() {
    setShowAddActor(true);
    setSelectedActorId(null);
    setSelectedSceneId(null);
    setShowAddScene(false);
    setActorLabel("");
    setActorType("individual");
    setActorNotes("");
  }

  function selectActor(actor: Actor) {
    setSelectedActorId(actor.id);
    setShowAddActor(false);
    setSelectedSceneId(null);
    setShowAddScene(false);
    setActorLabel(actor.label);
    setActorType(actor.actor_type);
    setActorNotes(actor.notes ?? "");
  }

  function cancelActorForm() {
    setShowAddActor(false);
    setSelectedActorId(null);
    setActorLabel("");
    setActorType("individual");
    setActorNotes("");
  }

  async function addActor() {
    if (!selected || !actorLabel.trim()) return;
    setLoading(true);
    try {
      const actor = await api.narratives.addActor(
        selected.id,
        actorLabel.trim(),
        actorType,
        actorNotes.trim() || null,
      );
      setSelected((prev) => prev ? { ...prev, actors: [...prev.actors, actor] } : prev);
      setSelectedActorId(actor.id);
      setShowAddActor(false);
    } catch {
      setError("Akteur konnte nicht hinzugefügt werden.");
    } finally {
      setLoading(false);
    }
  }

  async function updateActor() {
    if (!selected || !selectedActorId || !actorLabel.trim()) return;
    setLoading(true);
    try {
      const updated = await api.narratives.updateActor(
        selected.id,
        selectedActorId,
        actorLabel.trim(),
        actorType,
        actorNotes.trim() || null,
      );
      setSelected((prev) =>
        prev
          ? { ...prev, actors: prev.actors.map((a) => (a.id === updated.id ? updated : a)) }
          : prev
      );
    } catch {
      setError("Akteur konnte nicht gespeichert werden.");
    } finally {
      setLoading(false);
    }
  }

  async function removeActor(actorId: string) {
    if (!selected) return;
    if (!window.confirm("Akteur wirklich löschen?")) return;
    try {
      await api.narratives.removeActor(selected.id, actorId);
      setSelected((prev) =>
        prev ? { ...prev, actors: prev.actors.filter((a) => a.id !== actorId) } : prev
      );
      if (selectedActorId === actorId) cancelActorForm();
    } catch {
      setError("Akteur konnte nicht gelöscht werden.");
    }
  }

  async function analyseNarrative() {
    if (!selected) return;
    setAnalysing(true);
    setAnalyseError(null);
    try {
      const analysis: AnalyseNarrativeResponse = await api.narratives.analyse(selected.id);
      navigate(`/narrative/${selected.id}/analyse`, {
        state: { analysis, narrative: { id: selected.id, title: selected.title } },
      });
    } catch {
      setAnalyseError("Analyse fehlgeschlagen. Bitte erneut versuchen.");
    } finally {
      setAnalysing(false);
    }
  }

  const selectedScene = selected?.scenes.find((s) => s.id === selectedSceneId) ?? null;
  const selectedClaims = selectedSceneId ? (claimsByScene[selectedSceneId] ?? null) : null;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "260px 200px 1fr",
        minHeight: "calc(100vh - 4rem)",
      }}
    >
      {/* ------------------------------------------------------------------ */}
      {/* Column 1: Narrative list                                            */}
      {/* ------------------------------------------------------------------ */}
      <aside
        style={{
          background: "var(--color-bg-subtle)",
          borderRight: "1px solid var(--color-border)",
          padding: "16px 12px",
          overflowY: "auto",
        }}
      >
        <h2 style={{ fontSize: "12px", fontWeight: "600", color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.06em", margin: "0 0 12px" }}>Narrative</h2>
        {error && <p style={{ color: "var(--color-red-text)", fontSize: "12px" }}>{error}</p>}

        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 1.5rem" }}>
          {summaries.map((n) => (
            <li key={n.id}>
              <button
                onClick={() => selectNarrative(n.id)}
                style={{
                  background: selected?.id === n.id ? "var(--color-blue-bg)" : "none",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 10px",
                  marginBottom: "2px",
                  cursor: "pointer",
                  width: "100%",
                  textAlign: "left",
                  fontSize: "13px",
                  color: selected?.id === n.id ? "var(--color-blue-text)" : "var(--color-text-primary)",
                  fontWeight: selected?.id === n.id ? "500" : "normal",
                }}
              >
                {n.title}
              </button>
            </li>
          ))}
        </ul>

        <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "16px" }}>
          <p style={{ margin: "0 0 6px", fontSize: "11px", color: "var(--color-text-tertiary)", textTransform: "uppercase" as const, letterSpacing: "0.06em" }}>
            Neues Narrativ
          </p>
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Titel"
            style={{
              width: "100%",
              padding: "8px 10px",
              marginBottom: "8px",
              boxSizing: "border-box" as const,
              fontSize: "13px",
              border: "1px solid var(--color-border)",
              borderRadius: "6px",
              fontFamily: "var(--font-sans)",
              outline: "none",
            }}
            onKeyDown={(e) => e.key === "Enter" && createNarrative()}
          />
          <button
            onClick={createNarrative}
            disabled={loading || !newTitle.trim()}
            style={{
              fontSize: "13px",
              background: loading ? "var(--color-bg-subtle)" : "var(--color-text-primary)",
              color: loading ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
              border: "none",
              borderRadius: "6px",
              padding: "8px 16px",
              cursor: "pointer",
              width: "100%",
              fontWeight: "500",
            }}
          >
            Anlegen
          </button>
        </div>

        <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "16px", marginTop: "16px" }}>
          <p style={{ margin: "0 0 6px", fontSize: "11px", color: "var(--color-text-tertiary)", textTransform: "uppercase" as const, letterSpacing: "0.06em" }}>
            Aus Datei importieren
          </p>
          <input
            value={importPath}
            onChange={(e) => setImportPath(e.target.value)}
            placeholder="Pfad zur .docx oder .md"
            style={{
              width: "100%",
              padding: "8px 10px",
              marginBottom: "8px",
              boxSizing: "border-box" as const,
              fontSize: "13px",
              border: "1px solid var(--color-border)",
              borderRadius: "6px",
              fontFamily: "var(--font-sans)",
              outline: "none",
            }}
            onKeyDown={(e) => e.key === "Enter" && importNarrative()}
          />
          <button
            onClick={importNarrative}
            disabled={importing || !importPath.trim()}
            style={{
              fontSize: "13px",
              background: importing ? "var(--color-bg-subtle)" : "var(--color-text-primary)",
              color: importing ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
              border: "none",
              borderRadius: "6px",
              padding: "8px 16px",
              cursor: "pointer",
              width: "100%",
              fontWeight: "500",
            }}
          >
            {importing ? "Importiere…" : "Importieren"}
          </button>
        </div>
      </aside>

      {/* ------------------------------------------------------------------ */}
      {/* Column 2: Scene list                                                */}
      {/* ------------------------------------------------------------------ */}
      <div
        style={{
          borderRight: "1px solid var(--color-border)",
          padding: "16px 12px",
          overflowY: "auto",
          background: "var(--color-bg-subtle)",
        }}
      >
        {!selected ? (
          <p style={{ color: "var(--color-text-tertiary)", fontSize: "13px" }}>Narrativ auswählen</p>
        ) : (
          <>
            <p
              style={{
                margin: "0 0 8px",
                fontSize: "11px",
                color: "var(--color-text-tertiary)",
                textTransform: "uppercase" as const,
                letterSpacing: "0.06em",
              }}
            >
              Szenen
            </p>

            <ul style={{ listStyle: "none", padding: 0, margin: "0 0 1rem" }}>
              {selected.scenes.map((scene) => (
                <li key={scene.id}>
                  <button
                    onClick={() => selectScene(scene)}
                    style={{
                      background: selectedSceneId === scene.id ? "var(--color-blue-bg)" : "none",
                      border: "none",
                      borderRadius: "6px",
                      padding: "8px 10px",
                      marginBottom: "2px",
                      cursor: "pointer",
                      width: "100%",
                      textAlign: "left",
                      fontSize: "13px",
                      color: selectedSceneId === scene.id ? "var(--color-blue-text)" : "var(--color-text-primary)",
                    }}
                  >
                    <span style={{ color: "var(--color-text-tertiary)", marginRight: "0.4rem" }}>
                      {scene.position}.
                    </span>
                    {scene.title}
                  </button>
                </li>
              ))}
            </ul>

            <button
              onClick={() => {
                setShowAddScene(true);
                setSelectedSceneId(null);
                setSelectedActorId(null);
                setShowAddActor(false);
              }}
              style={{
                fontSize: "13px",
                background: "var(--color-bg)",
                border: "1px solid var(--color-border)",
                borderRadius: "6px",
                padding: "6px 14px",
                cursor: "pointer",
                width: "100%",
                color: "var(--color-text-primary)",
              }}
            >
              + Szene hinzufügen
            </button>

            {/* ------------------------------------------------------------ */}
            {/* Actors                                                         */}
            {/* ------------------------------------------------------------ */}
            <div style={{ borderTop: "1px solid var(--color-border)", marginTop: "24px", paddingTop: "16px" }}>
              <p
                style={{
                  margin: "0 0 8px",
                  fontSize: "11px",
                  color: "var(--color-text-tertiary)",
                  textTransform: "uppercase" as const,
                  letterSpacing: "0.06em",
                }}
              >
                Akteure
              </p>

              <ul style={{ listStyle: "none", padding: 0, margin: "0 0 1rem" }}>
                {selected.actors.map((actor) => (
                  <li
                    key={actor.id}
                    style={{ display: "flex", alignItems: "center", gap: "0.25rem", marginBottom: "0.3rem" }}
                  >
                    <button
                      onClick={() => selectActor(actor)}
                      style={{
                        flex: 1,
                        background: selectedActorId === actor.id ? "var(--color-blue-bg)" : "none",
                        border: "none",
                        borderRadius: "6px",
                        padding: "8px 10px",
                        cursor: "pointer",
                        textAlign: "left",
                        fontSize: "13px",
                        color: selectedActorId === actor.id ? "var(--color-blue-text)" : "var(--color-text-primary)",
                        overflow: "hidden",
                        whiteSpace: "nowrap",
                        textOverflow: "ellipsis",
                      }}
                      title={actor.label}
                    >
                      {actor.label}
                      <span style={{ color: "var(--color-text-tertiary)", marginLeft: "0.3rem", fontSize: "0.7rem" }}>
                        {ACTOR_TYPE_LABELS[actor.actor_type] ?? actor.actor_type}
                      </span>
                    </button>
                    <button
                      onClick={() => removeActor(actor.id)}
                      title="Löschen"
                      style={{
                        flexShrink: 0,
                        background: "none",
                        border: "1px solid var(--color-border)",
                        borderRadius: "4px",
                        padding: "4px 6px",
                        cursor: "pointer",
                        color: "var(--color-text-tertiary)",
                        fontSize: "12px",
                        lineHeight: "1",
                      }}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>

              <button
                onClick={openAddActor}
                style={{
                  fontSize: "13px",
                  background: "var(--color-bg)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  padding: "6px 14px",
                  cursor: "pointer",
                  width: "100%",
                  color: "var(--color-text-primary)",
                }}
              >
                + Akteur hinzufügen
              </button>
            </div>
          </>
        )}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Column 3: Scene content                                             */}
      {/* ------------------------------------------------------------------ */}
      <main style={{ padding: "24px 32px", overflowY: "auto", background: "var(--color-bg)" }}>
        {/* Empty states */}
        {!selected && (
          <p style={{ color: "var(--color-text-tertiary)" }}>Narrativ auswählen oder neu anlegen.</p>
        )}
        {selected && !selectedScene && !showAddScene && (
          <p style={{ color: "var(--color-text-tertiary)" }}>
            Szene auswählen oder neue Szene hinzufügen.
          </p>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* Add scene form                                                    */}
        {/* ---------------------------------------------------------------- */}
        {showAddScene && (
          <div>
            <h2 style={{ marginTop: 0 }}>Neue Szene</h2>
            <input
              value={sceneTitle}
              onChange={(e) => setSceneTitle(e.target.value)}
              placeholder="Titel der Szene"
              style={{
                width: "100%",
                padding: "0.4rem",
                marginBottom: "0.75rem",
                boxSizing: "border-box",
              }}
            />
            <textarea
              value={sceneText}
              onChange={(e) => setSceneText(e.target.value)}
              placeholder="Text der Szene…"
              rows={12}
              style={{
                width: "100%",
                padding: "0.4rem",
                marginBottom: "0.75rem",
                boxSizing: "border-box",
                lineHeight: 1.7,
                resize: "vertical",
              }}
            />
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                onClick={addScene}
                disabled={loading || !sceneTitle.trim() || !sceneText.trim()}
              >
                Szene speichern
              </button>
              <button
                onClick={() => setShowAddScene(false)}
                style={{ background: "none", border: "1px solid #ddd" }}
              >
                Abbrechen
              </button>
            </div>
          </div>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* Add / edit actor form                                             */}
        {/* ---------------------------------------------------------------- */}
        {(showAddActor || selectedActorId) && (
          <div>
            <h2 style={{ marginTop: 0 }}>
              {selectedActorId ? "Akteur bearbeiten" : "Neuer Akteur"}
            </h2>

            <label style={{ display: "block", fontSize: "13px", marginBottom: "0.25rem" }}>
              Name
            </label>
            <input
              value={actorLabel}
              onChange={(e) => setActorLabel(e.target.value)}
              placeholder="Name des Akteurs"
              style={{
                width: "100%",
                padding: "0.4rem",
                marginBottom: "16px",
                boxSizing: "border-box",
              }}
            />

            <label style={{ display: "block", fontSize: "13px", marginBottom: "0.25rem" }}>
              Typ
            </label>
            <select
              value={actorType}
              onChange={(e) => setActorType(e.target.value)}
              style={{ padding: "0.4rem", marginBottom: "16px", fontSize: "13px" }}
            >
              {ACTOR_TYPES.map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>

            <label style={{ display: "block", fontSize: "13px", marginBottom: "0.25rem" }}>
              Beschreibung{" "}
              <span style={{ color: "var(--color-text-tertiary)", fontWeight: "normal" }}>(optional)</span>
            </label>
            <textarea
              value={actorNotes}
              onChange={(e) => setActorNotes(e.target.value)}
              placeholder="Kurze Beschreibung des Akteurs…"
              rows={4}
              style={{
                width: "100%",
                padding: "0.4rem",
                marginBottom: "16px",
                boxSizing: "border-box",
                resize: "vertical",
                lineHeight: 1.6,
              }}
            />

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                onClick={selectedActorId ? updateActor : addActor}
                disabled={loading || !actorLabel.trim()}
              >
                Speichern
              </button>
              <button
                onClick={cancelActorForm}
                style={{ background: "none", border: "1px solid #ddd" }}
              >
                Abbrechen
              </button>
            </div>
          </div>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* Selected scene                                                    */}
        {/* ---------------------------------------------------------------- */}
        {selectedScene && (
          <>
            <h2 style={{ fontSize: "18px", fontWeight: "600", marginTop: "0", color: "var(--color-text-primary)" }}>
              <span
                style={{ color: "var(--color-text-tertiary)", fontWeight: "normal", marginRight: "8px" }}
              >
                {selectedScene.position}.
              </span>
              {selectedScene.title}
            </h2>

            <p
              style={{
                whiteSpace: "pre-wrap",
                lineHeight: "1.7",
                color: "var(--color-text-secondary)",
                fontSize: "14px",
                marginBottom: "24px",
              }}
            >
              {selectedScene.text}
            </p>

            {/* Claims ---------------------------------------------------- */}
            <div
              style={{
                borderTop: "1px solid var(--color-border-subtle)",
                paddingTop: "20px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "16px",
                  marginBottom: "0.75rem",
                }}
              >
                <h3 style={{ margin: "0", fontSize: "12px", color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: "600" }}>
                  Claims{" "}
                  {selectedClaims !== null ? `(${selectedClaims.length})` : ""}
                </h3>
                <button
                  onClick={extractClaims}
                  disabled={extracting}
                  style={{ fontSize: "12px", padding: "5px 12px", border: "1px solid var(--color-border)", borderRadius: "6px", background: "var(--color-bg)", cursor: "pointer" }}
                >
                  {extracting ? "Extrahiere…" : "Claims extrahieren"}
                </button>
              </div>

              {selectedClaims !== null && selectedClaims.length === 0 && !extracting && (
                <p style={{ color: "var(--color-text-tertiary)", fontSize: "13px", margin: 0 }}>
                  Noch keine Claims extrahiert.
                </p>
              )}

              {selectedClaims !== null && selectedClaims.length > 0 && (
                <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
                  {selectedClaims.map((c, i) => (
                    <li
                      key={i}
                      style={{
                        display: "flex",
                        gap: "0.5rem",
                        alignItems: "flex-start",
                        marginBottom: "0.4rem",
                      }}
                    >
                      <span
                        style={{
                          background: "var(--color-bg-subtle)",
                          color: "var(--color-text-secondary)",
                          borderRadius: "10px",
                          padding: "2px 8px",
                          fontSize: "11px",
                          marginTop: "0.1rem",
                          flexShrink: 0,
                        }}
                      >
                        {CLAIM_TYPE_LABELS[c.typ] ?? c.typ}
                      </span>
                      <span style={{ color: "var(--color-text-secondary)", fontSize: "13px" }}>{c.text}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Consistency check ----------------------------------------- */}
            <div style={{ borderTop: "1px solid var(--color-border-subtle)", paddingTop: "1.25rem" }}>
              <h3 style={{ margin: "0 0 0.75rem", fontSize: "12px", color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: "600" }}>
                Konsistenzprüfung
              </h3>

              {causalModels.length === 0 ? (
                <p style={{ color: "var(--color-text-tertiary)", fontSize: "13px" }}>
                  Kein Wirkmodell vorhanden. Im Wirkmodell-Editor anlegen.
                </p>
              ) : (
                <>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      marginBottom: "0.75rem",
                    }}
                  >
                    <select
                      value={selectedModelId}
                      onChange={(e) => {
                        setSelectedModelId(e.target.value);
                        setConsistencyResult(null);
                      }}
                      style={{ padding: "6px 10px", fontSize: "13px", border: "1px solid var(--color-border)", borderRadius: "6px" }}
                    >
                      {causalModels.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.title}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={checkConsistency}
                      disabled={checking || !selectedModelId}
                      style={{ fontSize: "12px", padding: "5px 12px", border: "1px solid var(--color-border)", borderRadius: "6px", background: "var(--color-bg)", cursor: "pointer" }}
                    >
                      {checking ? "Prüfe…" : "Konsistenz prüfen"}
                    </button>
                  </div>

                  {consistencyResult && (
                    <div>
                      <div
                        style={{
                          background: consistencyResult.consistent
                            ? "var(--color-green-bg)"
                            : "var(--color-red-bg)",
                          color: consistencyResult.consistent
                            ? "var(--color-green-text)"
                            : "var(--color-red-text)",
                          borderRadius: "6px",
                          padding: "8px 12px",
                          fontWeight: "500",
                          fontSize: "13px",
                          marginBottom: "0.75rem",
                        }}
                      >
                        {consistencyResult.consistent
                          ? "✓ Konsistent"
                          : `✗ ${consistencyResult.conflicts.length} Konflikt${
                              consistencyResult.conflicts.length !== 1 ? "e" : ""
                            }`}
                      </div>

                      {consistencyResult.conflicts.map((c, i) => (
                        <div
                          key={i}
                          style={{
                            marginBottom: "0.75rem",
                            border: "1px solid var(--color-border)",
                            borderRadius: "6px",
                            padding: "12px",
                            background: "var(--color-bg-subtle)",
                            fontSize: "13px",
                          }}
                        >
                          <strong style={{ color: "var(--color-text-tertiary)", fontSize: "0.8rem" }}>
                            Axiom
                          </strong>
                          <p style={{ margin: "0.15rem 0 0.4rem", fontStyle: "italic" }}>
                            {c.axiom_label}
                          </p>
                          <strong style={{ color: "var(--color-text-tertiary)", fontSize: "0.8rem" }}>
                            Problem
                          </strong>
                          <p style={{ margin: "0.15rem 0 0.4rem" }}>{c.description}</p>
                          {c.suggestion && (
                            <>
                              <strong style={{ color: "var(--color-text-tertiary)", fontSize: "0.8rem" }}>
                                Vorschlag
                              </strong>
                              <p style={{ margin: "0.15rem 0 0" }}>{c.suggestion}</p>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* Analyse button                                                     */}
        {/* ---------------------------------------------------------------- */}
        {selected && !showAddScene && !showAddActor && !selectedActorId && (
          <div
            style={{
              borderTop: "1px solid var(--color-border)",
              paddingTop: "24px",
              marginTop: "32px",
            }}
          >
            <button
              onClick={analyseNarrative}
              disabled={analysing}
              style={{
                background: analysing ? "var(--color-bg-subtle)" : "var(--color-text-primary)",
                color: analysing ? "var(--color-text-tertiary)" : "var(--color-text-inverse)",
                border: "none",
                borderRadius: "6px",
                padding: "10px 16px",
                fontSize: "14px",
                fontWeight: "500",
                cursor: analysing ? "not-allowed" : "pointer",
                width: "100%",
              }}
            >
              {analysing ? "⏳ Analyse läuft…" : "Analysieren →"}
            </button>
            {analyseError && (
              <p style={{ color: "var(--color-red-text)", fontSize: "13px", marginTop: "8px" }}>
                {analyseError}
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
