// Server-side calls use API_URL (e.g. http://backend:8000 inside local compose);
// otherwise the public API URL.
export const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;

export function postJson(path: string, body: unknown) {
  return fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  }).catch(() => null);
}
