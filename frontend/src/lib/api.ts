const BASE = "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

async function requestVoid(path: string, options?: RequestInit): Promise<void> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
}

export interface Axiom {
  id: string;
  label: string;
  description: string;
}

export interface Actor {
  id: string;
  label: string;
  actor_type: string;
  notes: string | null;
  entity_ref: string | null;
}

export interface Scene {
  id: string;
  title: string;
  text: string;
  position: number;
}

export interface Narrative {
  id: string;
  title: string;
  causal_model_id: string | null;
  scenes: Scene[];
  actors: Actor[];
}

export interface NarrativeSummary {
  id: string;
  title: string;
  causal_model_id: string | null;
  user_id?: string | null;
  scene_count: number;
  actor_count: number;
  claim_count: number;
}

export interface Claim {
  id: string;
  text: string;
  typ: string;
  confidence: number;
}

export interface ConsistencyConflict {
  axiom_label: string;
  description: string;
  suggestion: string | null;
}

export interface ConsistencyResult {
  consistent: boolean;
  conflicts: ConsistencyConflict[];
}

// ---------------------------------------------------------------------------
// Wirkgefüge suggestion in a ClaimSuggestion (from /analyse)
// ---------------------------------------------------------------------------

export interface WirkgefuegeSuggestionInClaim {
  suggestion_type: string;
  slot: string | null;
  slot_state: string | null;
  source_slot: string | null;
  source_condition: string | null;
  target_slot: string | null;
  target_effect: string | null;
  mechanism: string | null;
}

export interface ActorSuggestion {
  label: string;
  actor_type: string;
  occurrences: string[];
  entity_suggestion: string | null;
}

export interface ClaimSuggestion {
  label: string;
  text: string;
  claim_type: string;
  confidence: number;
  wirkgefuege_suggestion: WirkgefuegeSuggestionInClaim | null;
}

export interface AnalyseNarrativeResponse {
  actors: ActorSuggestion[];
  claims: ClaimSuggestion[];
}

// ---------------------------------------------------------------------------
// Wirkgefüge suggestion (from /suggest-wirkgefuege)
// ---------------------------------------------------------------------------

export interface SuggestedSlot {
  identifier: string;
  slot_type: string;
}

export interface SuggestedRelation {
  source: string;
  target: string;
  source_condition: string | null;
  target_effect: string | null;
  mechanism: string | null;
  epistemic_status: string;
}

export interface SuggestWirkgefuegeResponse {
  suggested_slots: SuggestedSlot[];
  suggested_relations: SuggestedRelation[];
  from_claims: string[];
}

// ---------------------------------------------------------------------------
// Slot and Relation (from /causal-models/{id})
// ---------------------------------------------------------------------------

export interface Slot {
  id: string;
  identifier: string;
  slot_type: string;
  epistemic_status: string;
}

export interface Relation {
  id: string;
  identifier: string;
  source_slot_id: string;
  target_slot_id: string;
  mechanism: string | null;
  polarity: string | null;
  epistemic_status: string;
}

export interface CausalModel {
  id: string;
  title: string;
  status: string;
  axioms: Axiom[];
  slots: Slot[];
  relations: Relation[];
}

export const api = {
  causalModels: {
    list: () => request<CausalModel[]>("/causal-models"),
    get: (id: string) => request<CausalModel>(`/causal-models/${id}`),
    create: (title: string) =>
      request<CausalModel>("/causal-models", {
        method: "POST",
        body: JSON.stringify({ title }),
      }),
    addAxiom: (id: string, label: string, description: string) =>
      request<Axiom>(`/causal-models/${id}/axioms`, {
        method: "POST",
        body: JSON.stringify({ label, description }),
      }),
    checkConsistency: (id: string, scene_text: string) =>
      request<ConsistencyResult>(`/causal-models/${id}/check-consistency`, {
        method: "POST",
        body: JSON.stringify({ scene_text }),
      }),
    addSlot: (id: string, identifier: string, slot_type: string) =>
      request<Slot>(`/causal-models/${id}/slots`, {
        method: "POST",
        body: JSON.stringify({ identifier, slot_type, epistemic_status: "incomplete" }),
      }),
    addRelation: (
      id: string,
      identifier: string,
      source_slot_id: string,
      target_slot_id: string,
      mechanism: string | null,
    ) =>
      request<Relation>(`/causal-models/${id}/relations`, {
        method: "POST",
        body: JSON.stringify({ identifier, source_slot_id, target_slot_id, mechanism }),
      }),
    updateRelation: (
      causal_model_id: string,
      relation_id: string,
      mechanism: string | null,
      polarity: string | null,
      epistemic_status: string,
    ) =>
      request<Relation>(`/causal-models/${causal_model_id}/relations/${relation_id}`, {
        method: "PUT",
        body: JSON.stringify({ mechanism, polarity, epistemic_status }),
      }),
  },
  narratives: {
    list: () => request<NarrativeSummary[]>("/narratives"),
    get: (id: string) => request<Narrative>(`/narratives/${id}`),
    create: (title: string) =>
      request<Narrative>("/narratives", {
        method: "POST",
        body: JSON.stringify({ title }),
      }),
    importFromPath: (path: string) =>
      request<Narrative>("/narratives/import", {
        method: "POST",
        body: JSON.stringify({ path }),
      }),
    addScene: (narrativeId: string, title: string, text: string) =>
      request<Scene>(`/narratives/${narrativeId}/scenes`, {
        method: "POST",
        body: JSON.stringify({ title, text }),
      }),
    extractClaims: (narrativeId: string, sceneId: string) =>
      request<{ claims: Claim[] }>(
        `/narratives/${narrativeId}/scenes/${sceneId}/extract-claims`,
        { method: "POST" }
      ),
    getSceneClaims: (narrativeId: string, sceneId: string) =>
      request<Claim[]>(`/narratives/${narrativeId}/scenes/${sceneId}/claims`),
    addActor: (
      narrativeId: string,
      label: string,
      actor_type: string,
      notes: string | null,
      entity_ref?: string | null,
    ) =>
      request<Actor>(`/narratives/${narrativeId}/actors`, {
        method: "POST",
        body: JSON.stringify({ label, actor_type, notes, entity_ref: entity_ref ?? null }),
      }),
    updateActor: (
      narrativeId: string,
      actorId: string,
      label: string,
      actor_type: string,
      notes: string | null,
    ) =>
      request<Actor>(`/narratives/${narrativeId}/actors/${actorId}`, {
        method: "PUT",
        body: JSON.stringify({ label, actor_type, notes }),
      }),
    removeActor: (narrativeId: string, actorId: string) =>
      requestVoid(`/narratives/${narrativeId}/actors/${actorId}`, { method: "DELETE" }),
    analyse: (id: string) =>
      request<AnalyseNarrativeResponse>(`/narratives/${id}/analyse`, { method: "POST" }),
    suggestWirkgefuege: (id: string) =>
      request<SuggestWirkgefuegeResponse>(`/narratives/${id}/suggest-wirkgefuege`, {
        method: "POST",
      }),
    linkToCausalModel: (narrativeId: string, causalModelId: string) =>
      request<Narrative>(`/narratives/${narrativeId}/causal-model`, {
        method: "PUT",
        body: JSON.stringify({ causal_model_id: causalModelId }),
      }),
  },
  claims: {
    linkToWirkgefuege: (claimId: string, wirkgefuege_ref: string) =>
      requestVoid(`/claims/${claimId}/link-to-wirkgefuege`, {
        method: "POST",
        body: JSON.stringify({ wirkgefuege_ref }),
      }),
  },
};
