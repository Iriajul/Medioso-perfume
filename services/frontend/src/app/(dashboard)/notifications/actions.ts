"use server";

import { apiErrors, apiJson } from "@/lib/session";

export type SendState = { count?: number; errors?: string[] } | undefined;

export async function sendNotification(_: SendState, formData: FormData): Promise<SendState> {
  const res = await apiJson("/api/v1/admin/notifications/", Object.fromEntries(formData));
  if (!res?.ok) return { errors: await apiErrors(res, "Unable to send the notification.") };
  return { count: (await res.json()).recipients_count };
}
