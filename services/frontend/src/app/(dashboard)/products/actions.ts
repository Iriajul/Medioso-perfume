"use server";

import { revalidatePath } from "next/cache";
import { apiFetch, saveForm, type SaveState } from "@/lib/session";

async function remove(path: string) {
  const res = await apiFetch(path, { method: "DELETE" });
  if (res?.ok) revalidatePath("/products");
  return res?.ok ?? false;
}

// PUT so unticked branches and the featured checkbox are cleared on edit.
export async function saveProduct(id: number | null, _: SaveState, formData: FormData) {
  const result = await saveForm("/api/v1/admin/products/", id, formData, "PUT");
  if (result?.ok) revalidatePath("/products");
  return result;
}

export async function saveBanner(id: number | null, _: SaveState, formData: FormData) {
  // Unchecked toggles are not submitted at all; send an explicit value.
  formData.set("is_active", formData.get("is_active") ? "true" : "false");
  const result = await saveForm("/api/v1/admin/banners/", id, formData);
  if (result?.ok) revalidatePath("/products");
  return result;
}

export async function deleteProduct(id: number) {
  return remove(`/api/v1/admin/products/${id}/`);
}

export async function deleteBanner(id: number) {
  return remove(`/api/v1/admin/banners/${id}/`);
}
