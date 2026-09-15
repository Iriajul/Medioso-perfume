"use server";

import { revalidatePath } from "next/cache";
import { apiErrors, apiFetch, apiJson } from "@/lib/session";

export async function updateOrderStatus(id: number, status: string) {
  const res = await apiJson(`/api/v1/admin/orders/${id}/status/`, { status });
  if (res?.ok) revalidatePath(`/orders/${id}`);
  return res?.ok ?? false;
}

export type Lookup = { id: number; full_name: string; email: string; avatar_url: string; points_balance: number; tier: string; is_active: boolean };

export async function lookupCustomer(email: string): Promise<Lookup | null> {
  const res = await apiFetch(`/api/v1/admin/customers/lookup/?email=${encodeURIComponent(email)}`);
  return res?.ok ? res.json() : null;
}

export type RegisterState = { ok?: { order: string; points: number; balance: number }; errors?: string[] } | undefined;

export async function registerPurchase(_: RegisterState, formData: FormData): Promise<RegisterState> {
  const res = await apiJson("/api/v1/admin/orders/in-store/", Object.fromEntries(formData));
  if (!res?.ok) return { errors: await apiErrors(res, "Unable to register the purchase.") };
  revalidatePath("/orders/register");
  return { ok: await res.json() };
}
