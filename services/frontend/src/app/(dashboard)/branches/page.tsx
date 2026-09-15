import { Store } from "lucide-react";
import Avatar from "@/components/avatar";
import DeleteButton from "@/components/delete-button";
import Pagination from "@/components/pagination";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import { deleteBranch } from "./actions";
import BranchDialog from "./branch-dialog";

export type Branch = {
  id: number;
  name: string;
  address: string;
  phone: string;
  weekday_opens: string;
  weekday_closes: string;
  sunday_opens: string;
  sunday_closes: string;
  latitude: string | null;
  longitude: string | null;
  image_url: string;
};

const PAGE_SIZE = 5; // matches BranchPagination on the API

export default async function BranchesPage({ searchParams }: PageProps<"/branches">) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const [dict, lang, data] = await Promise.all([
    getDictionary(),
    getLang(),
    apiGet<{ count: number; added_this_quarter: number; results: Branch[] }>(`/api/v1/admin/branches/?page=${page}`),
  ]);
  const t = dict.branches;
  const num = new Intl.NumberFormat(lang);
  const from = (page - 1) * PAGE_SIZE + 1;

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-center justify-between gap-6">
        <div className="max-w-2xl">
          <h1 className="text-5xl font-bold tracking-tight text-brand-light">{t.title}</h1>
          <p className="mt-4 text-lg leading-7 text-gray-600">{t.subtitle}</p>
        </div>
        <BranchDialog t={t} />
      </div>

      <div className="mt-12 flex items-start justify-between rounded-3xl bg-white px-6 py-7 shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
        <div>
          <span className="flex size-9 items-center justify-center rounded-lg bg-[#e3e8f7] text-brand-light"><Store className="size-4" /></span>
          <p className="mt-5 text-2xl font-bold text-gray-900">{data ? num.format(data.count) : "—"}</p>
          {!!data?.added_this_quarter && (
            <p className="mt-1 text-sm font-semibold text-brand-light">{t.thisQuarter.replace("{n}", num.format(data.added_this_quarter))}</p>
          )}
        </div>
        <p className="max-w-24 text-xs font-semibold uppercase tracking-wider text-gray-600">{t.total}</p>
      </div>

      {!data ? (
        <p role="alert" className="mt-8 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{t.loadError}</p>
      ) : (
        <div className="mt-12 overflow-hidden rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
          <h2 className="px-8 py-8 text-xl font-semibold text-gray-900">{t.directory}</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#eef2fb] text-sm font-semibold uppercase tracking-[0.1em] text-gray-600">
                <tr>{[t.name, t.address, t.phone, t.actions].map((h) => <th key={h} className="px-8 py-5 text-start font-semibold">{h}</th>)}</tr>
              </thead>
              <tbody>
                {data.results.map((b, i) => (
                  <tr key={b.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-8 py-4">
                      <span className="flex items-center gap-3 font-semibold text-gray-900">
                        <Avatar name={b.name} className={`size-10 text-sm ${i % 2 ? "!bg-gray-200 !text-gray-600" : ""}`} />
                        {b.name}
                      </span>
                    </td>
                    <td className="max-w-64 px-8 py-4 text-gray-600">{b.address}</td>
                    <td className="max-w-36 px-8 py-4 text-gray-900" dir="ltr">{b.phone}</td>
                    <td className="px-8 py-4">
                      <div className="flex items-center gap-6">
                        <BranchDialog t={t} branch={b} />
                        <DeleteButton action={deleteBranch.bind(null, b.id)} label={t.delete} cancelText={dict.common.cancel} confirmText={t.confirmDelete} errorText={t.deleteError} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.count === 0 ? (
            <p className="px-8 py-10 text-center text-gray-500">{t.empty}</p>
          ) : (
            <div className="flex flex-wrap items-center justify-between gap-4 bg-[#eef2fb] px-8 py-5">
              <p className="text-sm text-gray-600">
                {t.showing
                  .replace("{from}", num.format(from))
                  .replace("{to}", num.format(Math.min(from + PAGE_SIZE - 1, data.count)))
                  .replace("{total}", num.format(data.count))}
              </p>
              <Pagination page={page} pageCount={Math.ceil(data.count / PAGE_SIZE)} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
