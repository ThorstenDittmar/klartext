const BASE = "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
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

export interface Scene {
  id: string;
  title: string;
  text: string;
  position: number;
}

export interface Narrative {
  id: string;
  title: string;
  scenes: Scene[];
}

export interface NarrativeSummary {
  id: string;
  title: string;
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
  },
};
