import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Banknote, Check, ChevronRight, CreditCard, FileText, ShoppingBasket, Truck } from "lucide-react";
import Avatar from "@/components/avatar";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import StatusMenu from "./status-menu";

type Detail = {
  id: number; number: string; status: string; channel: "app" | "branch"; branch_name: string | null; created_at: string;
  customer: { id: number; full_name: string; email: string; phone: string };
  items: { product_name: string; sku: string; image_url: string; unit_price: string; quantity: number; line_total: string }[];
  events: { status: string; created_at: string }[];
  subtotal: string; shipping_method: string; shipping_fee: string; tax: string; total: string;
  payment_method: "card" | "debit" | "cod" | "in_store"; payment_reference: string; card_last4: string;
  shipping_address: string; billing_address: string; notes: string;
};

const APP_FLOW = ["pending_payment", "paid", "processing", "shipped", "delivered"];
const card = "rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]";

export default async function OrderDetailPage({ params }: PageProps<"/orders/[id]">) {
  const { id } = await params;
  const [dict, lang, o] = await Promise.all([getDictionary(), getLang(), apiGet<Detail>(`/api/v1/admin/orders/${Number(id)}/`)]);
  if (!o) notFound();
  const t = dict.orders;
  const status = dict.common.status;
  const money = (v: string) => new Intl.NumberFormat(lang, { style: "currency", currency: "USD" }).format(Number(v));
  const dateTime = new Intl.DateTimeFormat(lang, { dateStyle: "medium", timeStyle: "short" });
  const time = new Intl.DateTimeFormat(lang, { timeStyle: "short" });

  // Timeline: reached steps from the event log; for app orders, the remaining normal steps as pending.
  const reached = new Map(o.events.map((e) => [e.status, e.created_at]));
  const steps = o.channel === "app" && o.status !== "cancelled"
    ? APP_FLOW.map((s) => ({ status: s, at: reached.get(s) ?? (s === "pending_payment" ? o.created_at : null) }))
    : o.events.map((e) => ({ status: e.status, at: e.created_at }));
  const lastEvent = o.events.at(-1);
  // A step not reached but followed by a reached one was skipped, not pending.
  const lastReached = steps.findLastIndex((s) => s.at);

  return (
    <div className="mx-auto max-w-5xl">
      <nav className="flex items-center gap-2 text-base text-gray-600">
        <Link href="/orders" className="hover:text-brand">{t.title}</Link><ChevronRight className="size-4 rtl:-scale-x-100" />
        <span className="text-gray-900">#{o.number}</span>
      </nav>
      <div className="mt-1 flex flex-wrap items-start justify-between gap-6">
        <div>
          <h1 className="text-5xl font-bold tracking-tight text-brand">#{o.number}</h1>
          <p className="mt-2 text-base text-gray-600">{t.placedOn.replace("{date}", dateTime.format(new Date(o.created_at)))}</p>
        </div>
        {o.channel === "app" && (
          <StatusMenu id={o.id} current={o.status} label={t.updateStatus} errorText={t.updateError}
            options={[...APP_FLOW, "cancelled"].map((s) => [s, status[s as keyof typeof status]])} />
        )}
      </div>

      <div className="mt-10 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_290px]">
        <div className="space-y-8">
          <section className={`${card} px-8 py-8`}>
            <h2 className="flex items-center gap-2 text-2xl font-semibold text-brand"><ShoppingBasket className="size-6" />{t.orderedProducts}</h2>
            {o.items.length === 0 ? (
              <p className="mt-6 text-gray-600">{t.noItems}{o.branch_name ? ` · ${t.branch}: ${o.branch_name}` : ""}</p>
            ) : (
              <div className="mt-6 overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-[#eef2fb] text-sm font-semibold uppercase tracking-[0.1em] text-gray-600">
                    <tr><th className="rounded-s-xl px-4 py-4 text-start">{t.product}</th><th className="px-4 py-4 text-start">{t.sku}</th><th className="px-4 py-4 text-end">{t.price}</th><th className="px-4 py-4 text-end">{t.qty}</th><th className="rounded-e-xl px-4 py-4 text-end">{t.lineTotal}</th></tr>
                  </thead>
                  <tbody>
                    {o.items.map((i, n) => (
                      <tr key={n} className="border-b border-gray-200 last:border-0">
                        <td className="px-4 py-6">
                          <span className="flex items-center gap-4">
                            {i.image_url ? <Image src={i.image_url} alt="" width={64} height={64} className="size-16 rounded-xl object-cover shadow" /> : <span className="size-16 rounded-xl bg-gray-100" />}
                            <span className="font-semibold text-gray-900">{i.product_name}</span>
                          </span>
                        </td>
                        <td className="px-4 py-6 text-gray-600">{i.sku}</td>
                        <td className="px-4 py-6 text-end text-gray-900">{money(i.unit_price)}</td>
                        <td className="px-4 py-6 text-end text-gray-900">{i.quantity}</td>
                        <td className="px-4 py-6 text-end font-semibold text-brand">{money(i.line_total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
            <section className={`${card} px-8 py-8`}>
              <h2 className="text-2xl font-semibold text-brand">{t.orderSummary}</h2>
              <dl className="mt-6 space-y-4 text-gray-700">
                {([[t.subtotal, o.subtotal], [`${t.shipping}${o.shipping_method ? ` (${o.shipping_method})` : ""}`, o.shipping_fee], [t.tax, o.tax]] as const).map(([label, value]) => (
                  <div key={label} className="flex justify-between gap-4"><dt>{label}</dt><dd className="text-gray-900">{money(value)}</dd></div>
                ))}
              </dl>
              <div className="mt-6 flex items-center justify-between gap-4 border-t border-gray-200 pt-6">
                <span className="max-w-20 text-brand">{t.totalAmount}</span><span className="text-3xl font-bold text-brand">{money(o.total)}</span>
              </div>
            </section>

            <section className="flex flex-col items-center rounded-3xl bg-[#f3f5fb] px-6 py-8 text-center">
              <span className="flex size-20 items-center justify-center rounded-2xl bg-[#c7d5f1] text-brand shadow-lg"><Banknote className="size-9" /></span>
              <h2 className="mt-8 text-base uppercase tracking-[0.15em] text-gray-700">{t.paymentInfo}</h2>
              {o.payment_reference && <p className="mt-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-1.5 text-xs text-gray-700">{t.transactionId}: {o.payment_reference}</p>}
              <p className="mt-5 flex items-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-2 text-start">
                <CreditCard className="size-4 text-brand" />
                <span><span className="block text-[10px] uppercase tracking-wide text-gray-600">{t.paymentMethod}</span>
                  <span className="block text-gray-900">
                    {o.card_last4 ? t.cardEnding.replace("{method}", t.paymentMethods[o.payment_method]).replace("{last4}", o.card_last4) : t.paymentMethods[o.payment_method]}
                  </span>
                </span>
              </p>
            </section>
          </div>
        </div>

        <div className="space-y-8">
          <section className={`${card} px-8 py-8`}>
            <h2 className="text-2xl font-semibold text-brand">{t.customerProfile}</h2>
            <Link href={`/customers/${o.customer.id}`} className="mt-6 flex items-center gap-3">
              <Avatar name={o.customer.full_name} className="size-12 rounded-xl text-lg" />
              <span className="min-w-0"><span className="block font-semibold text-gray-900">{o.customer.full_name}</span><span className="block truncate text-gray-600">{o.customer.email}</span></span>
            </Link>
            {o.channel === "app" && (
              <>
                <h3 className="mt-8 flex items-center gap-2 text-sm uppercase tracking-[0.15em] text-gray-600"><Truck className="size-4" />{t.shippingAddress}</h3>
                <p className="mt-3 whitespace-pre-line text-gray-900">{o.shipping_address}</p>
                {o.customer.phone && <p className="mt-1 text-brand" dir="ltr">{o.customer.phone}</p>}
                <h3 className="mt-8 flex items-center gap-2 text-sm uppercase tracking-[0.15em] text-gray-600"><FileText className="size-4" />{t.billingAddress}</h3>
                <p className="mt-3 whitespace-pre-line italic text-gray-700">{o.billing_address || t.sameAsShipping}</p>
              </>
            )}
            {o.branch_name && <p className="mt-6 text-gray-700">{t.branch}: <span className="text-gray-900">{o.branch_name}</span></p>}
          </section>

          <section className={`${card} px-8 py-8`}>
            <h2 className="text-2xl font-semibold text-brand">{t.orderStatus}</h2>
            <div className="mt-6 flex items-center gap-3">
              <span className="rounded-md border border-gray-300 bg-[#e9edf9] px-3 py-1 text-xs font-semibold uppercase text-brand">{status[o.status as keyof typeof status]}</span>
              {lastEvent && <span className="text-xs text-gray-600">{t.since.replace("{time}", time.format(new Date(lastEvent.created_at)))}</span>}
            </div>
            <ol className="mt-8 space-y-7 border-s-2 border-gray-100 ps-6">
              {steps.map((s, i) => {
                const current = s.at && s.status === o.status;
                const skipped = !s.at && i < lastReached;
                return (
                  <li key={`${s.status}-${i}`} className="relative">
                    <span className={`absolute -start-[35px] top-0.5 flex size-5 items-center justify-center rounded-full ${s.at ? (current ? "border-4 border-brand bg-white" : "bg-brand text-white") : "bg-gray-100"}`}>
                      {s.at && !current && <Check className="size-3" />}
                    </span>
                    <p className={`font-semibold ${s.at ? (current ? "text-brand" : "text-gray-900") : "text-gray-300"}`}>
                      {s.status === "pending_payment" && s.at ? t.orderReceived : status[s.status as keyof typeof status]}
                    </p>
                    <p className={`text-sm ${s.at ? "text-gray-600" : "text-gray-300"}`}>{s.at ? dateTime.format(new Date(s.at)) : skipped ? "—" : t.pending}</p>
                  </li>
                );
              })}
            </ol>
          </section>
        </div>
      </div>
    </div>
  );
}
