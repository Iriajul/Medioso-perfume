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

export async function apiGet<T>(path: string): Promise<T | null> {
  const access = (await cookies()).get("access")?.value;
  const res = await fetch(`${API_URL}${path}`, { headers: { Authorization: `Bearer ${access}` }, cache: "no-store" }).catch(() => null);
  return res?.ok ? res.json() : null;
}
