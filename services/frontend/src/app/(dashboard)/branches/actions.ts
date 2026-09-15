"use server";

import { revalidatePath } from "next/cache";
import { apiFetch, saveForm, type SaveState } from "@/lib/session";

const API = "/api/v1/admin/branches/";

export async function saveBranch(id: number | null, _: SaveState, formData: FormData) {
  const result = await saveForm(API, id, formData);
  if (result?.ok) revalidatePath("/branches");
  return result;
}

export async function deleteBranch(id: number) {
  const res = await apiFetch(`${API}${id}/`, { method: "DELETE" });
  if (res?.ok) revalidatePath("/branches");
  return res?.ok ?? false;
}
