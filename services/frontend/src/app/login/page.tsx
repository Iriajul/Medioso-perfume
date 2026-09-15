import AuthShell from "@/components/auth-shell";
import LoginForm from "./login-form";

export const metadata = { title: "Admin Login · Mad Perfume" };

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const { reset } = await searchParams;
  return (
    <AuthShell title="Admin Login" subtitle="Please enter your credentials to access the management dashboard.">
      {reset && (
        <p role="status" className="mt-6 rounded-xl bg-green-50 px-4 py-3 text-sm text-green-700">
          Your password has been updated. Please log in.
        </p>
      )}
      <LoginForm />
    </AuthShell>
  );
}
