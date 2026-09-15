import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ChevronRight, Gift, Smartphone, Star, Store } from "lucide-react";
import Avatar from "@/components/avatar";
import StatusBadge from "@/components/status-badge";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import type { Customer } from "../page";

type Profile = Customer & {
  shipping_address: string; next_tier: Customer["tier"] | null; tier_progress: number; lifetime_spend: string; avg_order_value: string;
  orders: { id: number; number: string; created_at: string; status: string; total: string; images: string[] }[];
  loyalty_history: {
    id: number; kind: "earned" | "redeemed"; channel: "app" | "branch"; branch_name: string | null; reward_name: string | null;
    created_at: string; reference: string; purchase_amount: string; points: number; balance_after: number;
  }[];
};

const card = "rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]";

export default async function CustomerProfilePage({ params }: PageProps<"/customers/[id]">) {
  const { id } = await params;
  const [dict, lang, c] = await Promise.all([getDictionary(), getLang(), apiGet<Profile>(`/api/v1/admin/customers/${Number(id)}/`)]);
  if (!c) notFound();
  const t = dict.customers;
  const num = new Intl.NumberFormat(lang);
  const money = new Intl.NumberFormat(lang, { style: "currency", currency: "USD" });
  const date = new Intl.DateTimeFormat(lang, { dateStyle: "medium" });
  const time = new Intl.DateTimeFormat(lang, { timeStyle: "short" });

  return (
    <div className="mx-auto max-w-5xl">
      <nav className="flex items-center gap-2 text-sm text-gray-600">
        <Link href="/customers" className="hover:text-brand">{t.title}</Link>
        <ChevronRight className="size-4 rtl:-scale-x-100" />
        <span className="font-semibold text-gray-900">{c.full_name}</span>
      </nav>

      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[290px_1fr]">
        <aside className={`${card} px-8 py-8 lg:row-span-2`}>
          <div className="flex flex-col items-center text-center">
            {c.avatar_url
              ? <Image src={c.avatar_url} alt={c.full_name} width={128} height={128} className="size-32 rounded-full border-4 border-white object-cover shadow-lg" />
              : <Avatar name={c.full_name} className="size-32 text-4xl shadow-lg" />}
            <h1 className="mt-5 text-2xl font-semibold text-gray-900">{c.full_name}</h1>
            <span className="mt-2 rounded-full bg-[#dde5f8] px-4 py-1 text-xs font-bold uppercase tracking-wider text-brand">
              {t.member.replace("{tier}", dict.common.tiers[c.tier])}
            </span>
          </div>
          <dl className="mt-12 space-y-6">
            {[[t.emailAddress, c.email], [t.phoneNumber, c.phone], [t.shippingAddress, c.shipping_address]].map(([label, value]) => (
              <div key={label}>
                <dt className="text-[10px] font-semibold uppercase tracking-[0.12em] text-gray-700">{label}</dt>
                <dd className="mt-1 whitespace-pre-line break-words text-base text-gray-900">{value || t.notProvided}</dd>
              </div>
            ))}
          </dl>
        </aside>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
          <div className="relative overflow-hidden rounded-3xl bg-brand-light px-8 py-8 text-white">
            <Star className="absolute -bottom-6 -end-6 size-32 fill-white/10 text-white/10" />
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-white/80">{t.currentBalance}</p>
            <p className="mt-1"><span className="text-5xl font-bold">{num.format(c.points_balance)}</span> <span className="text-sm">{dict.common.points}</span></p>
            <div className="mt-6 flex items-center gap-4">
              <span className="h-1.5 w-24 rounded-full bg-white/30"><span className="block h-full rounded-full bg-white" style={{ width: `${c.tier_progress}%` }} /></span>
              <span className="text-sm font-semibold">
                {c.next_tier ? t.toNextTier.replace("{percent}", num.format(c.tier_progress)).replace("{tier}", dict.common.tiers[c.next_tier]) : t.topTier}
              </span>
            </div>
          </div>
          <div className={`${card} px-8 py-8`}>
            <h2 className="text-xl font-semibold text-gray-900">{t.accountSummary}</h2>
            <dl className="mt-6 space-y-5">
              {[[t.lifetimeSpend, c.lifetime_spend], [t.avgOrder, c.avg_order_value]].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-4">
                  <dt className="text-gray-700">{label}</dt><dd className="font-semibold text-gray-900">{money.format(Number(value))}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>

        <section className={`${card} overflow-hidden`}>
          <h2 className="px-8 py-7 text-xl font-semibold text-gray-900">{t.orderHistory}</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#eef2fb] text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-600">
                <tr>{[t.orderId, t.date, t.products, t.status].map((h) => <th key={h} className="px-5 py-4 text-start font-semibold">{h}</th>)}<th className="px-5 py-4 text-end font-semibold">{t.amount}</th></tr>
              </thead>
              <tbody>
                {c.orders.map((o) => (
                  <tr key={o.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-5 py-5 font-semibold text-gray-900"><Link href={`/orders/${o.id}`} className="hover:text-brand">#{o.number}</Link></td>
                    <td className="px-5 py-5 text-gray-700">{date.format(new Date(o.created_at))}</td>
                    <td className="px-5 py-5">
                      <span className="flex items-center">
                        {o.images.filter(Boolean).slice(0, 1).map((src) => (
                          <Image key={src} src={src} alt="" width={28} height={28} className="size-7 rounded-full border-2 border-white object-cover shadow" />
                        ))}
                        {o.images.length > 1 && <span className="-ms-1 flex size-7 items-center justify-center rounded-full bg-[#e3e8f7] text-[10px] font-semibold text-brand">+{o.images.length - 1}</span>}
                      </span>
                    </td>
                    <td className="px-5 py-5"><StatusBadge status={o.status} label={dict.common.status[o.status as keyof typeof dict.common.status]} className="uppercase" /></td>
                    <td className="px-5 py-5 text-end font-semibold text-gray-900">{money.format(Number(o.total))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {c.orders.length === 0 && <p className="px-8 pb-8 text-gray-500">{t.noOrders}</p>}
        </section>
      </div>

      <section className={`${card} mx-auto mt-10 max-w-3xl overflow-hidden`}>
        <h2 className="px-8 py-7 text-xl font-semibold text-gray-900">{t.loyaltyHistory}</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#eef2fb] text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-600">
              <tr>{[t.channelBranch, t.dateTime, t.orderNo, t.amount].map((h) => <th key={h} className="px-8 py-5 text-start font-semibold">{h}</th>)}<th className="px-8 py-5 text-end font-semibold">{dict.common.points}</th><th className="px-8 py-5 text-end font-semibold">{t.balanceAfter}</th></tr>
            </thead>
            <tbody>
              {c.loyalty_history.map((e) => {
                const redeemed = e.kind === "redeemed";
                const [Icon, title, sub] = redeemed
                  ? [Gift, t.rewardRedemption, e.reward_name ?? t.loyaltyProgram]
                  : e.channel === "app" ? [Smartphone, dict.common.channels.app, t.digitalStore] : [Store, e.branch_name ?? dict.common.channels.branch, t.physicalBranch];
                return (
                  <tr key={e.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-8 py-6">
                      <span className="flex items-center gap-3">
                        <span className={`flex size-8 shrink-0 items-center justify-center rounded-full ${redeemed ? "bg-red-50 text-red-600" : "bg-[#e3e8f7] text-brand"}`}><Icon className="size-4" /></span>
                        <span><span className="block font-semibold text-gray-900">{title}</span><span className="block text-[10px] uppercase tracking-wide text-gray-600">{sub}</span></span>
                      </span>
                    </td>
                    <td className="px-8 py-6 text-gray-700">{date.format(new Date(e.created_at))} • {time.format(new Date(e.created_at))}</td>
                    <td className="px-8 py-6 text-gray-900">#{e.reference}</td>
                    <td className="px-8 py-6 text-gray-900">{money.format(Number(e.purchase_amount))}</td>
                    <td className={`px-8 py-6 text-end font-semibold ${redeemed ? "text-red-600" : "text-brand"}`} dir="ltr">{e.points > 0 ? "+" : ""}{num.format(e.points)} {dict.common.pts}</td>
                    <td className="px-8 py-6 text-end text-gray-700">{num.format(e.balance_after)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {c.loyalty_history.length === 0 && <p className="px-8 pb-8 text-gray-500">{t.noLoyalty}</p>}
      </section>
    </div>
  );
}
