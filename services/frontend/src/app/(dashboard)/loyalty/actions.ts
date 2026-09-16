"use server";

import { revalidatePath } from "next/cache";
import { apiFetch, saveForm, type SaveState } from "@/lib/session";

const API = "/api/v1/admin/rewards/";

export async function saveReward(id: number | null, _: SaveState, formData: FormData) {
  const result = await saveForm(API, id, formData);
  if (result?.ok) revalidatePath("/loyalty");
  return result;
}

export async function deleteReward(id: number) {
  const res = await apiFetch(`${API}${id}/`, { method: "DELETE" });
  if (res?.ok) revalidatePath("/loyalty");
  return res?.ok ?? false;
}

export async function collectRedemption(id: number) {
  const res = await apiFetch(`/api/v1/admin/redemptions/${id}/collect/`, { method: "POST" });
  if (res?.ok) revalidatePath("/loyalty");
  return res?.ok ?? false;
}
