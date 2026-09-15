"use client";

import { useActionState } from "react";
import { inputClass, LockIcon, submitClass } from "@/components/form";
import { resetPassword } from "./actions";

export default function ResetForm({ uid, token }: { uid: string; token: string }) {
  const [state, action, pending] = useActionState(resetPassword, undefined);

  return (
    <form action={action} className="mt-10 space-y-6">
      <input type="hidden" name="uid" value={uid} />
      <input type="hidden" name="token" value={token} />
      {(["password", "confirm"] as const).map((name) => (
        <div key={name}>
          <label htmlFor={name} className="ml-1 text-base text-gray-600">{name === "password" ? "New Password" : "Confirm Password"}</label>
          <div className="relative mt-2">
            <LockIcon />
            <input id={name} name={name} type="password" required autoComplete="new-password" placeholder="••••••••••••" className={inputClass} />
          </div>
        </div>
      ))}
      {state?.errors.map((e) => <p key={e} role="alert" className="text-sm text-red-600">{e}</p>)}
      <button type="submit" disabled={pending} className={submitClass}>
        {pending ? "UPDATING…" : "UPDATE PASSWORD"}
      </button>
    </form>
  );
}
