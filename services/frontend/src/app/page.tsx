export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center">
      <h1 className="text-3xl font-semibold tracking-tight">Mad Perfume Admin</h1>
      <p className="text-sm text-zinc-500">
        Dashboard scaffold. API: {process.env.NEXT_PUBLIC_API_URL ?? "not configured"}
      </p>
    </main>
  );
}
