import Link from "next/link";
import { Gift, Package, ShoppingBag, ShoppingBasket, Star, Store, TrendingUp, Users } from "lucide-react";
import Avatar from "@/components/avatar";
import StatusBadge from "@/components/status-badge";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet, getUser } from "@/lib/session";
import Greeting from "./greeting";

type Dashboard = {
  total_customers: number;
  customers_trend: number | null;
  total_products: number;
  total_orders: number;
  orders_trend: number | null;
  points_issued: number;
  recent_orders: { id: number; number: string; customer_name: string; status: string; total: string }[];
  loyalty_activity: { id: number; customer_name: string; kind: "earned" | "redeemed"; channel: "app" | "branch"; reward_name: string | null; points: number }[];
};

export default async function DashboardPage() {
  const [t, lang, user, data] = await Promise.all([getDictionary(), getLang(), getUser(), apiGet<Dashboard>("/api/v1/admin/dashboard/")]);
  const d = t.dashboard;
  const num = new Intl.NumberFormat(lang);
  const compact = new Intl.NumberFormat(lang, { notation: "compact", maximumFractionDigits: 1 });
  const money = new Intl.NumberFormat(lang, { style: "currency", currency: "USD" });

  const cards = [
    { label: d.totalCustomers, value: data && num.format(data.total_customers), icon: Users, badge: trend(data?.customers_trend) },
    { label: d.totalProducts, value: data && num.format(data.total_products), icon: Package, badge: <Tag>{d.stable}</Tag> },
    { label: d.totalOrders, value: data && num.format(data.total_orders), icon: ShoppingBag, badge: trend(data?.orders_trend) },
    { label: d.pointsIssued, value: data && compact.format(data.points_issued), icon: Star, badge: <Tag>{d.lifetime}</Tag> },
  ];

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-5xl font-bold tracking-tight text-brand">
        <Greeting t={t.greeting} />, {user.name.split(" ")[0]}
      </h1>
      <p className="mt-3 text-base text-gray-600">{d.subtitle}</p>
      {!data && <p role="alert" className="mt-6 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{d.loadError}</p>}

      <section className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ label, value, icon: Icon, badge }) => (
          <div key={label} className="rounded-3xl bg-white p-6 shadow-[0_8px_30px_rgba(0,50,125,0.05)]">
            <div className="flex items-start justify-between">
              <span className="flex size-12 items-center justify-center rounded-xl bg-[#e3e8f7] text-brand"><Icon className="size-5" /></span>
              {badge}
            </div>
            <p className="mt-7 text-xs font-semibold uppercase tracking-[0.12em] text-gray-700">{label}</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">{value ?? "—"}</p>
          </div>
        ))}
      </section>

      <section className="mt-12 grid grid-cols-1 gap-8 xl:grid-cols-[1fr_300px]">
        <div className="min-h-[600px] overflow-hidden rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.05)]">
          <div className="flex items-center justify-between px-6 py-6">
            <h2 className="text-2xl text-gray-900">{d.recentOrders}</h2>
            <Link href="/orders" className="text-base font-semibold text-brand hover:underline">{d.viewAll}</Link>
          </div>
          <table className="w-full text-start">
            <thead className="bg-[#e3e8f7]/70 text-xs uppercase tracking-[0.12em] text-gray-600">
              <tr>
                {[d.orderId, d.customer, d.status].map((h) => <th key={h} className="px-6 py-4 text-start font-semibold">{h}</th>)}
                <th className="px-6 py-4 text-end font-semibold">{d.total}</th>
              </tr>
            </thead>
            <tbody>
              {data?.recent_orders.map((o) => (
                <tr key={o.id} className="border-b border-gray-100">
                  <td className="px-6 py-5 text-gray-900"><Link href={`/orders/${o.id}`} className="hover:text-brand">#{o.number}</Link></td>
                  <td className="px-6 py-5">
                    <span className="flex items-center gap-3 text-gray-900"><Avatar name={o.customer_name} className="size-8 text-xs" />{o.customer_name}</span>
                  </td>
                  <td className="px-6 py-5">
                    <StatusBadge status={o.status} label={t.common.status[o.status as keyof typeof t.common.status]} className="uppercase" />
                  </td>
                  <td className="px-6 py-5 text-end font-semibold text-gray-900">{money.format(Number(o.total))}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {data?.recent_orders.length === 0 && <p className="px-6 py-10 text-center text-gray-500">{d.noOrders}</p>}
        </div>

        <div className="rounded-3xl bg-white p-6 shadow-[0_8px_30px_rgba(0,50,125,0.05)]">
          <h2 className="text-2xl text-gray-900">{d.loyaltyActivity}</h2>
          <ul className="mt-8 space-y-6">
            {data?.loyalty_activity.map((a) => (
              <li key={a.id} className="flex items-center gap-3">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-700">
                  {a.kind === "redeemed" ? <Gift className="size-4" /> : a.channel === "app" ? <ShoppingBasket className="size-4" /> : <Store className="size-4" />}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-gray-900">{a.customer_name}</p>
                  <p className="text-xs text-gray-500">{a.kind === "redeemed" ? d.redeemed.replace("{reward}", a.reward_name ?? "") : a.channel === "app" ? d.purchaseReward : d.inStoreReward}</p>
                </div>
                <span className={`rounded-lg px-2 py-1 font-semibold ${a.points < 0 ? "bg-red-50 text-red-700" : "bg-gray-100 text-brand"}`} dir="ltr">
                  {a.points > 0 ? "+" : ""}{num.format(a.points)} {d.pts}
                </span>
              </li>
            ))}
          </ul>
          {data?.loyalty_activity.length === 0 && <p className="mt-8 text-center text-gray-500">{d.noActivity}</p>}
        </div>
      </section>
    </div>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">{children}</span>;
}

function trend(value: number | null | undefined) {
  if (value == null) return null;
  const up = value >= 0;
  return (
    <span className={`flex items-center gap-1 rounded-full px-2 py-1 text-sm font-semibold ${up ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"}`} dir="ltr">
      <TrendingUp className={`size-4 ${up ? "" : "-scale-y-100"}`} />{Math.abs(value)}%
    </span>
  );
}
