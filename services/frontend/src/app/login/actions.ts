"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { postJson } from "@/lib/api";

type LoginState = { error: string; email: string } | undefined;

export async function login(_: LoginState, formData: FormData): Promise<LoginState> {
  const email = String(formData.get("email") ?? "");
  const remember = formData.get("remember") === "on";

  const res = await postJson("/api/v1/auth/login/", { email, password: formData.get("password") });

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
  // Lets the proxy keep the 30-day lifetime when it rotates the refresh token.
  if (remember) cookieStore.set("remember", "1", { ...base, maxAge: 60 * 60 * 24 * 30 });
  else cookieStore.delete("remember");

  redirect("/");
}
