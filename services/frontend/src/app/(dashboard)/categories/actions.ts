"use server";

import { revalidatePath } from "next/cache";
import { apiFetch, saveForm, type SaveState } from "@/lib/session";

const API = "/api/v1/admin/categories/";

export async function saveCategory(id: number | null, _: SaveState, formData: FormData) {
  const result = await saveForm(API, id, formData);
  if (result?.ok) revalidatePath("/categories");
  return result;
}

export async function deleteCategory(id: number) {
  const res = await apiFetch(`${API}${id}/`, { method: "DELETE" });
  if (res?.ok) revalidatePath("/categories");
  return res?.ok ?? false;
}
