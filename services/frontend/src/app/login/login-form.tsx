"use client";

import { useActionState, useState } from "react";
import { login } from "./actions";

const inputClass =
  "w-full rounded-2xl border border-gray-100 bg-[#f8f9fd] py-4 pl-12 pr-4 text-base text-gray-900 placeholder:text-gray-300 outline-none focus:border-brand-light";

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
          <a href="#" className="text-base text-brand hover:underline">Forgot Password?</a>
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

      <button
        type="submit" disabled={pending}
        className="w-full rounded-2xl bg-gradient-to-r from-brand-light to-brand py-4 text-base tracking-[0.1em] text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70"
      >
        {pending ? "SIGNING IN…" : "LOGIN TO DASHBOARD"}
      </button>
    </form>
  );
}

const iconProps = { width: 20, height: 20, fill: "none", stroke: "currentColor", strokeWidth: 1.6, "aria-hidden": true };

function MailIcon() {
  return (
    <svg {...iconProps} viewBox="0 0 24 24" className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
      <rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg {...iconProps} viewBox="0 0 24 24" className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
      <rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /><circle cx="12" cy="16" r="1" />
    </svg>
  );
}

function EyeIcon() {
  return (
    <svg {...iconProps} viewBox="0 0 24 24">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" />
    </svg>
  );
}
