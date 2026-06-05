import { useEffect, useState } from "react";
import { api, Claim, Narrative, NarrativeSummary } from "../lib/api";

// ---------------------------------------------------------------------------
// Claim type labels (German — user-facing)
// ---------------------------------------------------------------------------

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
// ReadingView — continuous reading experience for the reader
//
// Shows all scenes with their full text in sequence. Already-extracted claims
// are displayed below each scene. No analysis actions — those belong to the
// author's NarrativeEditor.
// ---------------------------------------------------------------------------

export default function ReadingView() {
  const [summaries, setSummaries] = useState<NarrativeSummary[]>([]);
  const [narrative, setNarrative] = useState<Narrative | null>(null);
  const [claimsByScene, setClaimsByScene] = useState<Record<string, Claim[]>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.narratives
      .list()
      .then((narrs) => {
        setSummaries(narrs);
        if (narrs.length > 0) return loadNarrative(narrs[0].id);
      })
      .catch(() => setError("API nicht erreichbar"));
  }, []);

  // Loads a narrative and fetches all its scene claims in parallel.
  async function loadNarrative(id: string) {
    const narr = await api.narratives.get(id);
    setNarrative(narr);
    setClaimsByScene({});

    const entries = await Promise.all(
      narr.scenes.map(async (scene) => {
        const claims = await api.narratives
          .getSceneClaims(narr.id, scene.id)
          .catch(() => [] as Claim[]);
        return [scene.id, claims] as [string, Claim[]];
      })
    );
    setClaimsByScene(Object.fromEntries(entries));
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "0 1rem" }}>
      {error && <p style={{ color: "var(--color-red-text)" }}>{error}</p>}

      {/* Narrative selector — only shown when more than one narrative exists */}
      {summaries.length > 1 && (
        <select
          onChange={(e) => loadNarrative(e.target.value)}
          style={{ marginBottom: "32px", padding: "0.4rem" }}
        >
          {summaries.map((n) => (
            <option key={n.id} value={n.id}>
              {n.title}
            </option>
          ))}
        </select>
      )}

      {narrative && (
        <>
          <h1 style={{ marginTop: 0, marginBottom: "2.5rem", fontSize: "1.8rem" }}>
            {narrative.title}
          </h1>

          {narrative.scenes.length === 0 && (
            <p style={{ color: "var(--color-text-tertiary)" }}>Dieses Narrativ enthält noch keine Szenen.</p>
          )}

          {narrative.scenes.map((scene) => {
            const claims = claimsByScene[scene.id];
            return (
              <div key={scene.id} style={{ marginBottom: "3rem" }}>
                <h2 style={{ fontSize: "16px", marginBottom: "0.75rem", color: "var(--color-text-primary)" }}>
                  <span style={{ color: "var(--color-text-tertiary)", fontWeight: "normal", marginRight: "0.4rem" }}>
                    {scene.position}.
                  </span>
                  {scene.title}
                </h2>

                <p
                  style={{
                    whiteSpace: "pre-wrap",
                    lineHeight: 1.8,
                    color: "var(--color-text-primary)",
                    margin: "0 0 16px",
                    fontSize: "16px",
                  }}
                >
                  {scene.text}
                </p>

                {/* Claims — shown only when already extracted by the author */}
                {claims && claims.length > 0 && (
                  <div
                    style={{
                      borderTop: "1px solid var(--color-border-subtle)",
                      paddingTop: "0.75rem",
                      marginTop: "0.5rem",
                    }}
                  >
                    <p
                      style={{
                        margin: "0 0 0.5rem",
                        fontSize: "0.75rem",
                        color: "var(--color-text-tertiary)",
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                      }}
                    >
                      Claims ({claims.length})
                    </p>
                    <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
                      {claims.map((c, i) => (
                        <li
                          key={i}
                          style={{
                            display: "flex",
                            gap: "0.5rem",
                            alignItems: "flex-start",
                            marginBottom: "0.4rem",
                            fontSize: "13px",
                          }}
                        >
                          <span
                            style={{
                              flexShrink: 0,
                              // TODO(token): needs color.semantic.blue variant — current tokens have --color-blue-bg (#E6F1FB) and --color-blue-text (#0C447C) but different shades
                              background: "var(--color-blue-bg)",
                              color: "var(--color-blue-text)",
                              borderRadius: 3,
                              padding: "0.1rem 0.4rem",
                              fontSize: "0.75rem",
                              marginTop: "0.15rem",
                            }}
                          >
                            {CLAIM_TYPE_LABELS[c.typ] ?? c.typ}
                          </span>
                          <span style={{ color: "var(--color-text-secondary)" }}>{c.text}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
