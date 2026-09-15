import Link from "next/link";
import AuthShell from "@/components/auth-shell";
import ResetForm from "./reset-form";

export const metadata = { title: "Reset Password · Mad Perfume" };

export default async function ResetPasswordPage({ searchParams }: PageProps<"/reset-password">) {
  const { uid, token } = await searchParams;

  return (
    <AuthShell title="Reset Password" subtitle="Choose a new password for your admin account.">
      {typeof uid === "string" && typeof token === "string" ? (
        <ResetForm uid={uid} token={token} />
      ) : (
        <p role="alert" className="mt-8 text-sm text-red-600">This reset link is invalid. Please request a new one.</p>
      )}
      <Link href="/login" className="mt-6 block text-center text-base text-brand hover:underline">Back to login</Link>
    </AuthShell>
  );
}
