import Image from "next/image";
import { BadgeCheck, Ticket } from "lucide-react";
import type { Dictionary } from "@/i18n/dictionaries";
import CollectButton from "./collect-button";

export type Redemption = {
  id: number; voucher_code: string; customer_name: string; customer_email: string;
  reward_name: string | null; reward_image: string | null; points: number; branch_name: string | null;
  discount_amount: string | null; used_on_order: string | null;
  status: "processing" | "used" | "collected"; created_at: string; fulfilled_at: string | null; collected_by: string | null;
};

const isVoucher = (r: Redemption) => Number(r.discount_amount ?? 0) > 0;

export default function Redemptions({ t, common, lang, data }: {
  t: Dictionary["loyalty"]; common: Dictionary["common"]; lang: string;
  data: { count: number; pending_count: number; results: Redemption[] } | null;
}) {
  const num = new Intl.NumberFormat(lang);
  const date = (value: string) => new Intl.DateTimeFormat(lang, { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));

  return (
    <section className="mt-12">
      <h2 className="flex items-center gap-4 text-2xl font-semibold text-gray-900">
        <span className="h-8 w-1.5 rounded-full bg-brand-light" />{t.redemptionsTitle}
        {!!data?.pending_count && (
          <span className="rounded-full bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-700">
            {t.pendingCount.replace("{count}", num.format(data.pending_count))}
          </span>
        )}
      </h2>
      <p className="mt-3 text-gray-700">{t.redemptionsSubtitle}</p>

      {!data && <p role="alert" className="mt-6 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{common.loadError}</p>}
      {data?.results.length === 0 && <p className="mt-6 text-gray-500">{t.noRedemptions}</p>}

      {!!data?.results.length && (
        <div className="mt-8 overflow-hidden rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100/80 text-[11px] font-bold uppercase tracking-[0.12em] text-brand">
                <tr>
                  {[t.voucher, t.reward, t.customer, t.points, t.date, t.status].map((h) => (
                    <th key={h} className="px-6 py-6 text-start font-bold">{h}</th>
                  ))}
                  <th />
                </tr>
              </thead>
              <tbody className="text-base text-gray-800">
                {data.results.map((r) => (
                  <tr key={r.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-6 py-5 font-semibold text-gray-900" dir="ltr">{r.voucher_code}</td>
                    <td className="px-6 py-5">
                      <span className="flex items-center gap-3">
                        {r.reward_image
                          ? <Image src={r.reward_image} alt="" width={40} height={40} className="size-10 shrink-0 rounded-xl object-cover" />
                          : <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[#e3e8f7] text-brand"><Ticket className="size-4" /></span>}
                        {r.reward_name ?? "—"}
                      </span>
                    </td>
                    <td className="px-6 py-5">
                      <span className="block font-medium text-gray-900">{r.customer_name}</span>
                      <span className="block text-sm text-gray-500">{r.customer_email}</span>
                    </td>
                    <td className="px-6 py-5 font-semibold">
                      {num.format(r.points)} {common.pts}
                      {isVoucher(r) && <span className="mt-1 block text-sm font-normal text-gray-500" dir="ltr">${r.discount_amount} {t.off}</span>}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">{date(r.created_at)}</td>
                    <td className="px-6 py-5">
                      {r.status === "processing" ? (
                        <span className="inline-flex rounded-full bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-700">
                          {isVoucher(r) ? t.unused : t.processing}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-700">
                          <BadgeCheck className="size-4" />{r.status === "used" ? t.used : t.collected}
                        </span>
                      )}
                      {r.status === "used" && r.used_on_order && (
                        <span className="mt-1 block text-sm text-gray-500" dir="ltr">{t.usedOn.replace("{order}", r.used_on_order)}</span>
                      )}
                      {r.status === "collected" && r.collected_by && (
                        <span className="mt-1 block text-sm text-gray-500">
                          {t.collectedBy.replace("{name}", r.collected_by).replace("{branch}", r.branch_name ?? "—")}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-5 text-end">
                      {r.status === "processing" && !isVoucher(r) &&
                        <CollectButton id={r.id} label={t.markCollected} saving={t.marking} errorText={t.collectError} />}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
