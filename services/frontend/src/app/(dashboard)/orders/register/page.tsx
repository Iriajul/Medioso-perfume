import Link from "next/link";
import { ChevronRight, User } from "lucide-react";
import { getDictionary, getLang } from "@/i18n/server";
import { timeAgo } from "@/lib/format";
import { apiGet } from "@/lib/session";
import RegisterForm from "./register-form";

type Recent = { points_per_dollar: number; results: { id: number; number: string; customer_name: string; total: string; points: number; created_at: string }[] };

export default async function RegisterPurchasePage() {
  const [dict, lang, branches, recent] = await Promise.all([
    getDictionary(), getLang(),
    apiGet<{ id: number; name: string }[]>("/api/v1/admin/branches/options/"),
    apiGet<Recent>("/api/v1/admin/orders/in-store/recent/"),
  ]);
  const t = dict.register;
  const num = new Intl.NumberFormat(lang);
  const money = new Intl.NumberFormat(lang, { style: "currency", currency: "USD" });

  return (
    <div className="mx-auto max-w-5xl">
      <nav className="flex items-center gap-2 text-base text-gray-600">
        <Link href="/orders" className="hover:text-brand">{dict.orders.title}</Link><ChevronRight className="size-4 rtl:-scale-x-100" />
        <span className="text-gray-900">{t.breadcrumb}</span>
      </nav>
      <h1 className="mt-6 text-5xl font-bold tracking-tight text-gray-900">{t.title}</h1>
      <p className="mt-3 text-lg text-gray-600">{t.subtitle}</p>

      <RegisterForm t={t} tiers={dict.common.tiers} pointsLabel={dict.common.points} branches={branches ?? []} rate={recent?.points_per_dollar ?? 1} />

      <section className="mt-6 overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
        <h2 className="border-b border-gray-100 px-8 py-8 text-base text-gray-900">{t.recentActivity}</h2>
        <div className="overflow-x-auto px-4">
          <table className="w-full">
            <thead className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-700">
              <tr>{[t.transactionIdCol, t.customerCol, t.amountCol, t.pointsCol, t.timeCol, t.statusCol].map((h) => <th key={h} className="px-4 py-6 text-start font-semibold">{h}</th>)}</tr>
            </thead>
            <tbody>
              {recent?.results.map((r) => (
                <tr key={r.id} className="border-t border-gray-100">
                  <td className="px-4 py-5 font-mono text-xs font-bold text-brand-light"><Link href={`/orders/${r.id}`}>#{r.number}</Link></td>
                  <td className="px-4 py-5"><span className="flex items-center gap-3 text-gray-900"><span className="flex size-10 items-center justify-center rounded-xl bg-[#e3e8f7] text-brand"><User className="size-4" /></span>{r.customer_name}</span></td>
                  <td className="px-4 py-5 font-semibold text-gray-900">{money.format(Number(r.total))}</td>
                  <td className="px-4 py-5"><span className="rounded-lg bg-[#e3e8f7] px-3 py-1 font-semibold text-brand" dir="ltr">+{num.format(r.points)}</span></td>
                  <td className="px-4 py-5 text-gray-600">{timeAgo(lang, r.created_at)}</td>
                  <td className="px-4 py-5"><span className="rounded-full border border-green-200 bg-green-50 px-3 py-0.5 text-[10px] font-semibold uppercase text-green-700">{t.completed}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
          {recent?.results.length === 0 && <p className="px-4 pb-8 text-gray-500">{t.noActivity}</p>}
        </div>
      </section>
    </div>
  );
}
