"use client";

import { startTransition, useActionState, useState } from "react";
import { Check, Eye, Lock } from "lucide-react";
import type { Dictionary } from "@/i18n/dictionaries";
import { changePassword } from "./actions";

const field = "w-full rounded-full border border-gray-200 bg-white/70 px-5 py-3.5 pe-12 text-base text-gray-900 placeholder:text-gray-500 outline-none focus:border-brand-light";

export default function PasswordForm({ t }: { t: Dictionary["settings"] }) {
  const [password, setPassword] = useState("");
  const [show, setShow] = useState({ current: false, next: false });
  const [state, action, pending] = useActionState(changePassword, undefined);
  const rules = [
    [t.ruleLength, password.length >= 8],
    [t.ruleSymbol, /[^A-Za-z0-9]/.test(password)],
    [t.ruleNumber, /\d/.test(password)],
  ] as const;

  const eye = (key: keyof typeof show) => (
    <button type="button" onClick={() => setShow((s) => ({ ...s, [key]: !s[key] }))} aria-label="Toggle visibility" className="absolute end-4 top-1/2 -translate-y-1/2 text-gray-400">
      <Eye className="size-5" />
    </button>
  );

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); startTransition(() => action(data)); }}
      onReset={() => setPassword("")}
      className="mx-auto mt-10 max-w-xl rounded-3xl bg-white/70 px-10 py-10 shadow-[0_8px_30px_rgba(0,50,125,0.08)]"
    >
      <div className="flex items-center gap-5">
        <span className="flex size-14 items-center justify-center rounded-2xl bg-brand-light text-white shadow-lg"><Lock className="size-6" /></span>
        <div><h2 className="text-xl font-semibold text-gray-900">{t.updatePassword}</h2><p className="text-sm text-gray-600">{t.updateHint}</p></div>
      </div>

      <label className="mt-8 block text-sm font-medium text-gray-900">{t.current}
        <span className="relative mt-2 block">
          <input name="current_password" type={show.current ? "text" : "password"} required autoComplete="current-password" placeholder="••••••••••••" className={field} />
          {eye("current")}
        </span>
      </label>

      <label className="mt-6 block text-sm font-medium text-gray-900">{t.newPassword}
        <span className="relative mt-2 block">
          <input name="password" type={show.next ? "text" : "password"} required autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={t.newPlaceholder} className={field} />
          {eye("next")}
        </span>
      </label>

      <div className="mt-3 rounded-2xl border border-gray-100 bg-white/60 px-5 py-4">
        <p className="text-xs font-semibold tracking-wide text-gray-600">{t.requirements}</p>
        <ul className="mt-3 space-y-2">
          {rules.map(([text, met]) => (
            <li key={text} className="flex items-center gap-3 text-sm text-gray-700">
              <span className={`flex size-4 items-center justify-center rounded-full ${met ? "bg-brand-light text-white" : "border border-gray-300"}`}>{met && <Check className="size-3" />}</span>
              {text}
            </li>
          ))}
        </ul>
      </div>

      <label className="mt-6 block text-sm font-medium text-gray-900">{t.confirm}
        <input name="confirm" type="password" required autoComplete="new-password" placeholder={t.confirmPlaceholder} className={`${field} mt-2`} />
      </label>

      {state?.errors?.map((e) => <p key={e} role="alert" className="mt-4 text-sm text-red-600">{e}</p>)}

      <div className="mt-8 flex items-center justify-between border-t border-gray-200 pt-8">
        <button type="reset" className="px-8 text-base text-gray-600">{t.cancel}</button>
        <button type="submit" disabled={pending || !rules.every(([, met]) => met)} className="rounded-full bg-brand-light px-10 py-4 text-lg font-semibold text-white shadow-[0_10px_30px_rgba(0,68,165,0.35)] disabled:opacity-60">
          {pending ? t.submitting : t.submit}
        </button>
      </div>
    </form>
  );
}
