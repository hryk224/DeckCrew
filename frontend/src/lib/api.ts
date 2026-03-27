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
