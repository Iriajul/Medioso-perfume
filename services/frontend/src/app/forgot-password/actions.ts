"use server";

import { postJson } from "@/lib/api";

type State = { sent?: true; error?: string } | undefined;

export async function requestReset(_: State, formData: FormData): Promise<State> {
  const res = await postJson("/api/v1/auth/password-reset/", { email: formData.get("email") });
  if (res?.ok) return { sent: true };
  return { error: res?.status === 429 ? "Too many attempts. Please try again in a minute." : "Unable to send the reset link. Please try again." };
}
