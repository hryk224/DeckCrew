const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post(path: string, body?: unknown): Promise<void> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
}

export async function startSession(): Promise<void> {
  await post("/session");
}

export async function submitRequest(text: string): Promise<void> {
  await post("/session/request", { text });
}

export async function runTurn(): Promise<void> {
  await post("/session/turn");
}

export async function updateGenreGroup(genreGroup: string): Promise<void> {
  const res = await fetch(`${API_URL}/session/params`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ genre_group: genreGroup }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
}

// --- Memory API ---

export interface MemoryIntervention {
  session_id: string;
  turn: number;
  text: string;
  adopted_agent: string;
  timestamp: string;
}

export interface MemoryProfile {
  preferred_mood: string | null;
  min_energy: number;
  max_energy: number;
  preferred_focus: string | null;
  intervention_count: number;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchInterventions(): Promise<MemoryIntervention[]> {
  return get<MemoryIntervention[]>("/memory/interventions");
}

export async function fetchProfile(): Promise<MemoryProfile> {
  return get<MemoryProfile>("/memory/profile");
}

export async function clearMemory(): Promise<void> {
  const res = await fetch(`${API_URL}/memory`, { method: "DELETE" });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
}
