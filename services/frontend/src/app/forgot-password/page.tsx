"use client";

import Link from "next/link";
import { useActionState } from "react";
import AuthShell from "@/components/auth-shell";
import { inputClass, MailIcon, submitClass } from "@/components/form";
import { requestReset } from "./actions";

export default function ForgotPasswordPage() {
  const [state, action, pending] = useActionState(requestReset, undefined);

  return (
    <AuthShell title="Forgot Password" subtitle="Enter your admin email and we'll send you a link to reset your password.">
      {state?.sent ? (
        <p role="status" className="mt-8 rounded-xl bg-green-50 px-4 py-3 text-sm text-green-700">
          If an admin account exists for that email, a reset link is on its way. The link expires in 1 hour.
        </p>
      ) : (
        <form action={action} className="mt-10 space-y-6">
          <div>
            <label htmlFor="email" className="ml-1 text-base text-gray-600">Email Address</label>
            <div className="relative mt-2">
              <MailIcon />
              <input id="email" name="email" type="email" required autoComplete="email" placeholder="admin@madperfume.com" className={inputClass} />
            </div>
          </div>
          {state?.error && <p role="alert" className="text-sm text-red-600">{state.error}</p>}
          <button type="submit" disabled={pending} className={submitClass}>
            {pending ? "SENDING…" : "SEND RESET LINK"}
          </button>
        </form>
      )}
      <Link href="/login" className="mt-6 block text-center text-base text-brand hover:underline">Back to login</Link>
    </AuthShell>
  );
}
