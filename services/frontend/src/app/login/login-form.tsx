"use client";

import Link from "next/link";
import { useActionState, useState } from "react";
import { EyeIcon, inputClass, LockIcon, MailIcon, submitClass } from "@/components/form";
import { login } from "./actions";

export default function LoginForm() {
  const [state, action, pending] = useActionState(login, undefined);
  const [showPassword, setShowPassword] = useState(false);

  return (
    <form action={action} className="mt-10 space-y-6">
      <div>
        <label htmlFor="email" className="ml-1 text-base text-gray-600">Email Address</label>
        <div className="relative mt-2">
          <MailIcon />
          <input
            id="email" name="email" type="email" required autoComplete="email"
            placeholder="admin@madperfume.com" defaultValue={state?.email} className={inputClass}
          />
        </div>
      </div>

      <div>
        <div className="ml-1 flex items-center justify-between">
          <label htmlFor="password" className="text-base text-gray-600">Password</label>
          <Link href="/forgot-password" className="text-base text-brand hover:underline">Forgot Password?</Link>
        </div>
        <div className="relative mt-2">
          <LockIcon />
          <input
            id="password" name="password" type={showPassword ? "text" : "password"} required
            autoComplete="current-password" placeholder="••••••••••••" className={`${inputClass} pr-12`}
          />
          <button
            type="button" onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? "Hide password" : "Show password"}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400"
          >
            <EyeIcon />
          </button>
        </div>
      </div>

      <label className="ml-1 flex items-center gap-3 text-base text-gray-600">
        <input name="remember" type="checkbox" className="size-5 rounded border-gray-300 accent-brand" />
        Remember this device for 30 days
      </label>

      {state?.error && <p role="alert" className="text-sm text-red-600">{state.error}</p>}

      <button type="submit" disabled={pending} className={submitClass}>
        {pending ? "SIGNING IN…" : "LOGIN TO DASHBOARD"}
      </button>
    </form>
  );
}
