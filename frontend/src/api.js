// Small API client for the FlavorGraph backend.
//
// All calls go through "/api", which is proxied to the backend by Vite in dev
// and by nginx in Docker. Set VITE_API_BASE to override if needed.

const BASE = import.meta.env.VITE_API_BASE || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch (_) {
      // ignore non-JSON error bodies
    }
    throw new Error(detail);
  }
  return response.json();
}

// POST /recommend — match recipes to the user's preferences.
export function getRecommendations(preferences) {
  return request("/recommend/", {
    method: "POST",
    body: JSON.stringify(preferences),
  });
}

// GET /recommend/popular — fallback list shown on first load.
export function getPopular(limit = 8) {
  return request(`/recommend/popular?limit=${limit}`);
}

// GET /recommend/similar/{id} — "more like this".
export function getSimilar(recipeId, limit = 6) {
  return request(`/recommend/similar/${recipeId}?limit=${limit}`);
}

// GET /health — used to show backend status.
export function getHealth() {
  return request("/health");
}
