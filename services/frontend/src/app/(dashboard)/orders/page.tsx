import Link from "next/link";
import { ArrowRight, MoreVertical, TrendingUp } from "lucide-react";
import Avatar from "@/components/avatar";
import ListFooter from "@/components/list-footer";
import StatusBadge from "@/components/status-badge";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";

type OrderRow = { id: number; number: string; customer_name: string; customer_email: string; total: string; status: string; created_at: string };

const PAGE_SIZE = 5;

export default async function OrdersPage({ searchParams }: PageProps<"/orders">) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const [dict, lang, data] = await Promise.all([
    getDictionary(), getLang(),
    apiGet<{ count: number; total_revenue: string; revenue_trend: number | null; active_orders: number; results: OrderRow[] }>(`/api/v1/admin/orders/?page=${page}`),
  ]);
  const t = dict.orders;
  const num = new Intl.NumberFormat(lang);
  const money = new Intl.NumberFormat(lang, { style: "currency", currency: "USD" });
  const date = new Intl.DateTimeFormat(lang, { dateStyle: "medium" });

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div>
          <h1 className="text-lg text-brand">{t.title}</h1>
          <p className="mt-1 text-base text-gray-600">{t.subtitle}</p>
        </div>
        <Link href="/orders/register" className="flex items-center gap-4 rounded-xl bg-brand px-6 py-3 text-base text-white shadow-[0_8px_20px_rgba(0,50,125,0.25)]">
          <span className="max-w-40 text-center leading-6">{t.registerPurchase}</span><ArrowRight className="size-5 rtl:-scale-x-100" />
        </Link>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="rounded-2xl border border-gray-200 bg-white px-6 py-7">
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-700">{t.totalRevenue}</p>
          <p className="mt-2 text-3xl font-bold text-brand">{data ? money.format(Number(data.total_revenue)) : "—"}</p>
          {data?.revenue_trend != null && (
            <p className="mt-2 flex items-center gap-1 text-xs font-semibold text-brand" dir="ltr">
              <TrendingUp className="size-3.5" />{t.fromLastMonth.replace("{value}", `${data.revenue_trend > 0 ? "+" : ""}${data.revenue_trend}`)}
            </p>
          )}
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white px-6 py-7">
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-700">{t.activeOrders}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{data ? num.format(data.active_orders) : "—"}</p>
          <p className="mt-2 text-xs text-gray-600">{t.processingNote}</p>
        </div>
      </div>

      {!data ? (
        <p role="alert" className="mt-8 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{dict.common.loadError}</p>
      ) : (
        <div className="mt-6 overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.08)]">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100/80 text-[11px] font-bold uppercase tracking-[0.12em] text-brand">
                <tr>{[t.number, t.customer, t.total, t.status, t.date].map((h) => <th key={h} className="max-w-28 px-8 py-6 text-start font-bold">{h}</th>)}<th /></tr>
              </thead>
              <tbody>
                {data.results.map((o) => (
                  <tr key={o.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-8 py-5 text-gray-900"><Link href={`/orders/${o.id}`} className="hover:text-brand">#{o.number}</Link></td>
                    <td className="px-8 py-5">
                      <span className="flex items-center gap-3">
                        <Avatar name={o.customer_name} className="size-9 text-xs" />
                        <span><span className="block font-semibold text-gray-900">{o.customer_name}</span><span className="block text-xs text-gray-600">{o.customer_email}</span></span>
                      </span>
                    </td>
                    <td className="px-8 py-5 font-semibold text-brand">{money.format(Number(o.total))}</td>
                    <td className="px-8 py-5"><StatusBadge status={o.status} label={dict.common.status[o.status as keyof typeof dict.common.status]} /></td>
                    <td className="px-8 py-5 text-gray-700">{date.format(new Date(o.created_at))}</td>
                    <td className="px-4 py-5"><Link href={`/orders/${o.id}`} aria-label={dict.common.viewDetails} className="inline-flex text-gray-600 hover:text-brand"><MoreVertical className="size-5" /></Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.count === 0 ? (
            <p className="px-8 py-10 text-center text-gray-500">{t.empty}</p>
          ) : (
            <ListFooter
              text={dict.common.showingOf.replace("{count}", num.format(data.results.length)).replace("{total}", num.format(data.count)).replace("{noun}", t.noun)}
              page={page} pageCount={Math.ceil(data.count / PAGE_SIZE)}
            />
          )}
        </div>
      )}
    </div>
  );
}
