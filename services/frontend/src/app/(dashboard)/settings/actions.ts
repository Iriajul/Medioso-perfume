"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { apiErrors, apiJson } from "@/lib/session";

export type ChangeState = { errors?: string[] } | undefined;

export async function changePassword(_: ChangeState, formData: FormData): Promise<ChangeState> {
  const password = formData.get("password");
  if (password !== formData.get("confirm")) return { errors: ["Passwords do not match."] };

  const res = await apiJson("/api/v1/auth/change-password/", { current_password: formData.get("current_password"), password });
  if (!res?.ok) return { errors: await apiErrors(res, "Unable to update the password.") };

  // The API signs the account out everywhere; clear this session and log in again.
  const cookieStore = await cookies();
  ["access", "refresh", "remember"].forEach((c) => cookieStore.delete(c));
  redirect("/login?reset=1");
}
