const API_BASE = "http://127.0.0.1:8000/api";

async function handle(res, errMsg) {
  if (!res.ok) {
    let details = "";
    try {
      const t = await res.text();
      details = t ? ` (${t})` : "";
    } catch {
      details = "";
    }
    throw new Error(`${errMsg}${details}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function fetchSources() {
  const res = await fetch(`${API_BASE}/sources`);
  return handle(res, "Failed to fetch sources");
}

export async function createSource(payload) {
  const res = await fetch(`${API_BASE}/sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return handle(res, "Failed to create source");
}

export async function startCrawler(sourceId) {
  const res = await fetch(`${API_BASE}/sources/${sourceId}/start`, { method: "POST" });
  return handle(res, "Failed to start crawler");
}

export async function stopCrawler(sourceId) {
  const res = await fetch(`${API_BASE}/sources/${sourceId}/stop`, { method: "POST" });
  return handle(res, "Failed to stop crawler");
}

export async function fetchStats(sourceId) {
  const res = await fetch(`${API_BASE}/sources/${sourceId}/stats`);
  return handle(res, "Failed to fetch stats");
}
