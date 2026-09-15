import { cookies } from "next/headers";
import { API_URL } from "./api";

type Claims = { exp: number; full_name?: string; email?: string };

// Reads (does not verify) JWT claims for display. The API verifies every request.
export function decodeJwt(token: string | undefined): Claims | null {
  try {
    return JSON.parse(Buffer.from(token!.split(".")[1], "base64url").toString());
  } catch {
    return null;
  }
}

export async function getUser() {
  const claims = decodeJwt((await cookies()).get("access")?.value);
  return { name: claims?.full_name || claims?.email || "", email: claims?.email ?? "" };
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const access = (await cookies()).get("access")?.value;
  return fetch(`${API_URL}${path}`, { ...init, headers: { Authorization: `Bearer ${access}` }, cache: "no-store" }).catch(() => null);
}

export async function apiGet<T>(path: string): Promise<T | null> {
  const res = await apiFetch(path);
  return res?.ok ? res.json() : null;
}

/** Flattens a DRF error response ({field: [messages]}) into a list of messages. */
export async function apiErrors(res: Response | null, fallback: string) {
  if (!res) return [fallback];
  const body = await res.json().catch(() => ({}));
  const errors = Object.values(body).flat().map(String);
  return errors.length ? errors : [fallback];
}
