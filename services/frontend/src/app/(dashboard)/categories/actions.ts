"use server";

import { revalidatePath } from "next/cache";
import { apiErrors, apiFetch } from "@/lib/session";

export type SaveState = { ok?: true; errors?: string[] } | undefined;

export async function saveCategory(id: number | null, _: SaveState, formData: FormData): Promise<SaveState> {
  // An empty file input still submits a 0-byte file; don't send it.
  const image = formData.get("image");
  if (image instanceof File && image.size === 0) formData.delete("image");

  const res = await apiFetch(id ? `/api/v1/admin/categories/${id}/` : "/api/v1/admin/categories/", {
    method: id ? "PATCH" : "POST",
    body: formData,
  });
  if (!res?.ok) return { errors: await apiErrors(res, "Unable to save the category.") };

  revalidatePath("/categories");
  return { ok: true };
}

export async function deleteCategory(id: number) {
  const res = await apiFetch(`/api/v1/admin/categories/${id}/`, { method: "DELETE" });
  if (res?.ok) revalidatePath("/categories");
  return res?.ok ?? false;
}
