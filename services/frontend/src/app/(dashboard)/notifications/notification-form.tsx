"use client";

import { startTransition, useActionState, useRef } from "react";
import { PlusCircle, SendHorizontal } from "lucide-react";
import type { Dictionary } from "@/i18n/dictionaries";
import { sendNotification, type SendState } from "./actions";

const field = "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-400 outline-none focus:border-brand-light";

export default function NotificationForm({ t }: { t: Dictionary["notifications"] }) {
  const form = useRef<HTMLFormElement>(null);
  const [state, action, pending] = useActionState(async (prev: SendState, formData: FormData) => {
    const result = await sendNotification(prev, formData);
    if (result?.count != null) form.current?.reset();
    return result;
  }, undefined);

  return (
    <form
      ref={form}
      onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); startTransition(() => action(data)); }}
      className="mx-auto mt-10 max-w-3xl rounded-3xl bg-white/80 px-8 py-8 shadow-[0_8px_30px_rgba(0,50,125,0.08)]"
    >
      <h2 className="flex items-center gap-2 text-2xl text-gray-900"><PlusCircle className="size-6 text-brand-light" />{t.create}</h2>
      <label className="mt-6 block text-sm font-medium text-gray-800">{t.titleLabel}
        <input name="title" required maxLength={150} placeholder={t.titlePlaceholder} className={`${field} mt-2`} />
      </label>
      <label className="mt-6 block text-sm font-medium text-gray-800">{t.body}
        <textarea name="body" required rows={4} placeholder={t.bodyPlaceholder} className={`${field} mt-2 resize-none`} />
      </label>
      <label className="mt-6 block text-sm font-medium text-gray-800">{t.recipients}
        <select name="audience" defaultValue="all" className={`${field} mt-2`}>
          {Object.entries(t.audiences).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </label>
      {state?.errors?.map((e) => <p key={e} role="alert" className="mt-4 text-sm text-red-600">{e}</p>)}
      {state?.count != null && <p role="status" className="mt-4 rounded-xl bg-green-50 px-4 py-3 text-sm text-green-700">{t.success.replace("{count}", state.count.toLocaleString())}</p>}
      <div className="mt-10 flex justify-end">
        <button type="submit" disabled={pending} className="flex items-center gap-3 rounded-xl bg-brand-light px-10 py-3 text-sm text-white shadow-md disabled:opacity-70">
          {pending ? t.sending : t.send} <SendHorizontal className="size-4 rtl:-scale-x-100" />
        </button>
      </div>
    </form>
  );
}
