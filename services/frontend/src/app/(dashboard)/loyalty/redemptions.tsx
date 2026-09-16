import Image from "next/image";
import Link from "next/link";
import { BadgeCheck, Search, Ticket } from "lucide-react";
import ListFooter from "@/components/list-footer";
import type { Dictionary } from "@/i18n/dictionaries";
import CollectButton from "./collect-button";

export type Redemption = {
  id: number; voucher_code: string; customer_name: string; customer_email: string;
  reward_name: string | null; reward_image: string | null; points: number; branch_name: string | null;
  discount_amount: string | null; used_on_order: string | null;
  status: "processing" | "used" | "collected"; created_at: string; fulfilled_at: string | null; collected_by: string | null;
};

export const REDEMPTION_PAGE_SIZE = 20;
const isVoucher = (r: Redemption) => Number(r.discount_amount ?? 0) > 0;
const FILTERS = ["all", "processing", "used", "collected"] as const;

export default function Redemptions({ t, common, lang, data, query, status, page }: {
  t: Dictionary["loyalty"]; common: Dictionary["common"]; lang: string;
  data: { count: number; pending_count: number; results: Redemption[] } | null;
  query: string; status: string; page: number;
}) {
  const num = new Intl.NumberFormat(lang);
  const date = (value: string) => new Intl.DateTimeFormat(lang, { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
  const params = { ...(query && { q: query }), ...(status !== "all" && { status }) };
  const from = (page - 1) * REDEMPTION_PAGE_SIZE + 1;

  return (
    <section className="mt-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="flex items-center gap-4 text-2xl font-semibold text-gray-900">
            <span className="h-8 w-1.5 rounded-full bg-brand-light" />{t.redemptionsTitle}
            {!!data?.pending_count && (
              <span className="rounded-full bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-700">
                {t.pendingCount.replace("{count}", num.format(data.pending_count))}
              </span>
            )}
          </h2>
          <p className="mt-3 max-w-2xl text-gray-700">{t.redemptionsSubtitle}</p>
        </div>

        <form className="relative" role="search">
          {Object.entries(params).filter(([k]) => k !== "q").map(([k, v]) => <input key={k} type="hidden" name={k} value={v} />)}
          <Search className="pointer-events-none absolute start-4 top-1/2 size-4 -translate-y-1/2 text-gray-500" />
          <input
            name="q" defaultValue={query} placeholder={t.searchPlaceholder} aria-label={t.searchPlaceholder}
            className="w-72 max-w-full rounded-full border border-gray-200 bg-white py-3 pe-4 ps-11 text-base text-gray-900 shadow-sm outline-none focus:border-brand-light"
          />
        </form>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {FILTERS.map((key) => (
          <Link
            key={key}
            href={`?${new URLSearchParams({ ...(query && { q: query }), ...(key !== "all" && { status: key }) })}#redemptions`}
            aria-current={status === key ? "true" : undefined}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
              status === key ? "bg-brand text-white shadow-sm" : "bg-white text-gray-700 shadow-sm hover:text-brand"}`}
          >
            {t.filters[key]}
          </Link>
        ))}
      </div>

      {!data && <p role="alert" className="mt-6 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{common.loadError}</p>}

      {data && (
        <div id="redemptions" className="mt-6 overflow-hidden rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
          {data.count === 0 ? (
            <p className="px-8 py-14 text-center text-gray-500">{query ? t.noMatches : t.noRedemptions}</p>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[56rem]">
                  <thead className="bg-gray-100/80 text-[11px] font-bold uppercase tracking-[0.12em] text-brand">
                    <tr>
                      {[t.voucher, t.reward, t.customer, t.points, t.status].map((h) => (
                        <th key={h} className="whitespace-nowrap px-6 py-5 text-start font-bold">{h}</th>
                      ))}
                      <th />
                    </tr>
                  </thead>
                  <tbody className="text-base text-gray-800">
                    {data.results.map((r) => (
                      <tr key={r.id} className="border-b border-gray-100 last:border-0 hover:bg-gray-50/60">
                        <td className="whitespace-nowrap px-6 py-5 align-top">
                          <span className="block font-semibold tracking-wide text-gray-900" dir="ltr">{r.voucher_code}</span>
                          <span className="mt-1 block text-sm text-gray-500">{date(r.created_at)}</span>
                        </td>
                        <td className="px-6 py-5 align-top">
                          <span className="flex items-start gap-3">
                            {r.reward_image
                              ? <Image src={r.reward_image} alt="" width={44} height={44} className="size-11 shrink-0 rounded-xl object-cover" />
                              : <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-[#e3e8f7] text-brand"><Ticket className="size-4" /></span>}
                            <span>
                              <span className="block font-medium text-gray-900">{r.reward_name ?? "—"}</span>
                              <span className="mt-0.5 block text-sm text-gray-500" dir="ltr">
                                {isVoucher(r) ? `$${r.discount_amount} ${t.off}` : t.inBoutique}
                              </span>
                            </span>
                          </span>
                        </td>
                        <td className="px-6 py-5 align-top">
                          <span className="block font-medium text-gray-900">{r.customer_name}</span>
                          <span className="block text-sm text-gray-500">{r.customer_email}</span>
                        </td>
                        <td className="whitespace-nowrap px-6 py-5 align-top font-semibold">{num.format(r.points)} {common.pts}</td>
                        <td className="px-6 py-5 align-top">
                          {r.status === "processing" ? (
                            <span className="inline-flex whitespace-nowrap rounded-full bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-700">
                              {isVoucher(r) ? t.unused : t.processing}
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-700">
                              <BadgeCheck className="size-4" />{r.status === "used" ? t.used : t.collected}
                            </span>
                          )}
                          {r.status === "used" && r.used_on_order && (
                            <span className="mt-1.5 block text-sm text-gray-500" dir="ltr">{t.usedOn.replace("{order}", r.used_on_order)}</span>
                          )}
                          {r.status === "collected" && r.collected_by && (
                            <span className="mt-1.5 block text-sm text-gray-500">
                              {t.collectedBy.replace("{name}", r.collected_by).replace("{branch}", r.branch_name ?? "—")}
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-5 text-end align-top">
                          {r.status === "processing" && !isVoucher(r) &&
                            <CollectButton id={r.id} label={t.markCollected} saving={t.marking} errorText={t.collectError} />}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <ListFooter
                className="border-t border-gray-100"
                text={t.showing.replace("{from}", num.format(from))
                  .replace("{to}", num.format(Math.min(from + REDEMPTION_PAGE_SIZE - 1, data.count)))
                  .replace("{total}", num.format(data.count))}
                page={page} pageCount={Math.ceil(data.count / REDEMPTION_PAGE_SIZE)} params={params}
              />
            </>
          )}
        </div>
      )}
    </section>
  );
}
