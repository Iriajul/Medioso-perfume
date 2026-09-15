"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { LANGS, type Lang } from "@/i18n/dictionaries";
import { postJson } from "@/lib/api";

export async function logout() {
  const cookieStore = await cookies();
  const refresh = cookieStore.get("refresh")?.value;
  if (refresh) await postJson("/api/v1/auth/logout/", { refresh }); // blacklist server-side
  ["access", "refresh", "remember"].forEach((c) => cookieStore.delete(c));
  redirect("/login");
}

export async function setLanguage(lang: Lang) {
  if (!LANGS.includes(lang)) return;
  (await cookies()).set("lang", lang, { path: "/", maxAge: 60 * 60 * 24 * 365, sameSite: "lax" });
}
