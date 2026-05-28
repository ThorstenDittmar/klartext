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

export interface CausalModel {
  id: string;
  title: string;
  status: string;
  axioms: Axiom[];
}

export interface Actor {
  id: string;
  name: string;
  typ: string;
  description: string | null;
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
}

export interface Claim {
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
  },
  narratives: {
    list: () => request<NarrativeSummary[]>("/narratives"),
    get: (id: string) => request<Narrative>(`/narratives/${id}`),
    create: (title: string) =>
      request<Narrative>("/narratives", {
        method: "POST",
        body: JSON.stringify({ title }),
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
    addActor: (narrativeId: string, name: string, typ: string, description: string | null) =>
      request<Actor>(`/narratives/${narrativeId}/actors`, {
        method: "POST",
        body: JSON.stringify({ name, typ, description }),
      }),
    updateActor: (narrativeId: string, actorId: string, name: string, typ: string, description: string | null) =>
      request<Actor>(`/narratives/${narrativeId}/actors/${actorId}`, {
        method: "PUT",
        body: JSON.stringify({ name, typ, description }),
      }),
    removeActor: (narrativeId: string, actorId: string) =>
      requestVoid(`/narratives/${narrativeId}/actors/${actorId}`, { method: "DELETE" }),
  },
};
