"use server";

import { redirect } from "next/navigation";
import { postJson } from "@/lib/api";

type State = { errors: string[] } | undefined;

export async function resetPassword(_: State, formData: FormData): Promise<State> {
  const password = formData.get("password");
  if (password !== formData.get("confirm")) return { errors: ["Passwords do not match."] };

  const res = await postJson("/api/v1/auth/password-reset/confirm/", {
    uid: formData.get("uid"),
    token: formData.get("token"),
    password,
  });

  if (!res) return { errors: ["Unable to reach the server. Please try again."] };
  if (res.status === 429) return { errors: ["Too many attempts. Please try again in a minute."] };
  if (!res.ok) {
    // DRF validation errors: { field: [messages] }
    const body = await res.json().catch(() => ({}));
    const errors = Object.values(body).flat().map(String);
    return { errors: errors.length ? errors : ["Unable to reset password."] };
  }

  redirect("/login?reset=1");
}
