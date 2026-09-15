import Link from "next/link";
import { MoreVertical, Star, TrendingUp } from "lucide-react";
import Avatar from "@/components/avatar";
import ListFooter from "@/components/list-footer";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";

export type Customer = {
  id: number; full_name: string; email: string; phone: string; avatar_url: string;
  points_balance: number; tier: "silver" | "gold" | "platinum" | "diamond"; is_active: boolean;
};

const PAGE_SIZE = 5;

export default async function CustomersPage({ searchParams }: PageProps<"/customers">) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const [dict, lang, data] = await Promise.all([
    getDictionary(), getLang(),
    apiGet<{ count: number; active_clients: number; results: Customer[] }>(`/api/v1/admin/customers/?page=${page}`),
  ]);
  const t = dict.customers;
  const num = new Intl.NumberFormat(lang);

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-4xl font-bold tracking-tight text-gray-900">{t.title}</h1>
      <p className="mt-3 text-base text-gray-600">{t.subtitle}</p>

      <div className="mx-auto mt-8 w-fit min-w-72 rounded-2xl bg-white px-9 py-8 shadow-[0_8px_30px_rgba(0,50,125,0.08)]">
        <p className="text-sm uppercase tracking-[0.15em] text-gray-700">{t.activeClients}</p>
        <p className="mt-1 text-5xl font-bold text-gray-900">{data ? num.format(data.active_clients) : "—"}</p>
        <p className="mt-3 flex items-center gap-1 text-xs font-medium text-brand"><TrendingUp className="size-3.5" />{t.premiumFocus}</p>
      </div>

      {!data ? (
        <p role="alert" className="mt-8 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{dict.common.loadError}</p>
      ) : (
        <div className="mt-8 overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
          <div className="h-11 border-b border-gray-200" />
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50/60 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-600">
                <tr>
                  {[t.name, t.phone, t.email, t.points].map((h) => <th key={h} className="max-w-32 px-8 py-5 text-start font-semibold">{h}</th>)}
                  <th className="px-8 py-5 text-end font-semibold">{t.actions}</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((c) => (
                  <tr key={c.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-8 py-5">
                      <Link href={`/customers/${c.id}`} className="flex items-center gap-4">
                        <Avatar name={c.full_name} className="size-11 text-sm shadow-md" />
                        <span>
                          <span className="block max-w-32 font-semibold text-gray-900">{c.full_name}</span>
                          <span className="mt-1 inline-block rounded bg-[#e3e8f7] px-1.5 text-[9px] font-bold uppercase text-brand">{dict.common.tiers[c.tier]}</span>
                        </span>
                      </Link>
                    </td>
                    <td className="max-w-36 px-8 py-5 text-gray-700" dir="ltr">{c.phone || "—"}</td>
                    <td className="px-8 py-5 text-gray-700">{c.email}</td>
                    <td className="px-8 py-5">
                      <span className="flex items-center gap-2 text-brand" dir="ltr"><Star className="size-4 fill-brand text-white" />{num.format(c.points_balance)} {dict.common.pts}</span>
                    </td>
                    <td className="px-8 py-5 text-end">
                      <Link href={`/customers/${c.id}`} aria-label={dict.common.viewDetails} className="inline-flex text-gray-600 hover:text-brand"><MoreVertical className="size-5" /></Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.count === 0 ? (
            <p className="px-8 py-10 text-center text-gray-500">{t.empty}</p>
          ) : (
            <ListFooter
              className="bg-[#eef1fb]"
              text={dict.common.showingOf.replace("{count}", num.format(data.results.length)).replace("{total}", num.format(data.count)).replace("{noun}", t.noun)}
              page={page} pageCount={Math.ceil(data.count / PAGE_SIZE)}
            />
          )}
        </div>
      )}
    </div>
  );
}
