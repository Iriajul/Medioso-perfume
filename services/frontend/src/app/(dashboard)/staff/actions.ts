"use server";

import { revalidatePath } from "next/cache";
import { apiFetch, saveForm, type SaveState } from "@/lib/session";

const API = "/api/v1/admin/staff/";

export async function saveStaff(id: number | null, _: SaveState, formData: FormData) {
  // Unchecked checkboxes are not submitted at all; send an explicit value.
  formData.set("is_active", formData.get("is_active") ? "true" : "false");
  const result = await saveForm(API, id, formData);
  if (result?.ok) revalidatePath("/staff");
  return result;
}

export async function deleteStaff(id: number) {
  const res = await apiFetch(`${API}${id}/`, { method: "DELETE" });
  if (res?.ok) revalidatePath("/staff");
  return res?.ok ?? false;
}
