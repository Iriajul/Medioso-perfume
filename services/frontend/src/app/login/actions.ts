"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

// Server-side calls use API_URL (e.g. http://backend:8000 inside local compose);
// otherwise the public API URL.
const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;

type LoginState = { error: string; email: string } | undefined;

export async function login(_: LoginState, formData: FormData): Promise<LoginState> {
  const email = String(formData.get("email") ?? "");
  const remember = formData.get("remember") === "on";

  const res = await fetch(`${API_URL}/api/v1/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password: formData.get("password") }),
    cache: "no-store",
  }).catch(() => null);

  if (!res?.ok) {
    const error =
      res?.status === 401 || res?.status === 400 ? "Invalid email or password."
      : res?.status === 429 ? "Too many attempts. Please try again in a minute."
      : "Unable to reach the server. Please try again.";
    return { error, email };
  }

  const { access, refresh } = await res.json();
  const cookieStore = await cookies();
  const base = { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/" } as const;
  cookieStore.set("access", access, { ...base, maxAge: 60 * 60 });
  // Without "remember", the refresh cookie ends with the browser session.
  cookieStore.set("refresh", refresh, remember ? { ...base, maxAge: 60 * 60 * 24 * 30 } : base);

  redirect("/");
}
