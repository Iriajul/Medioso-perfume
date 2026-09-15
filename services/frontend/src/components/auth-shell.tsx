import Image from "next/image";

// Shared frame for the login / forgot / reset password pages.
export default function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <main className="flex flex-1 flex-col items-center px-4 pt-12 pb-8">
      <Image src="/logo.png" alt="Mad Perfume" width={96} height={96} priority className="rounded-3xl shadow-[0_8px_24px_rgba(0,50,125,0.06)]" />
      <h1 className="mt-6 text-4xl font-medium tracking-tight text-brand">MAD PERFUME</h1>
      <p className="mt-4 text-base tracking-[0.25em] text-gray-500">LUXURY FRAGRANCE ADMIN</p>

      <section className="mt-12 w-full max-w-[400px] rounded-[28px] bg-white px-10 py-10 shadow-[0_24px_60px_rgba(0,50,125,0.08)]">
        <h2 className="text-base text-gray-900">{title}</h2>
        <p className="mt-2 text-base leading-6 text-gray-600">{subtitle}</p>
        {children}
      </section>

      <footer className="mt-14 text-[10px] tracking-[0.12em] text-gray-400">
        © {new Date().getFullYear()} MAD PERFUME INTERNATIONAL. ALL RIGHTS RESERVED.
      </footer>
    </main>
  );
}
