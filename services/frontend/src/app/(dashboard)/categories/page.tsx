import Image from "next/image";
import { Shapes } from "lucide-react";
import Pagination from "@/components/pagination";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import CategoryDialog from "./category-dialog";
import DeleteButton from "./delete-button";

export type Category = {
  id: number;
  name: string;
  type: "classic" | "premium" | "exotic" | "seasonal" | "niche";
  description: string;
  image_url: string;
  products_count: number;
};

const PAGE_SIZE = 5; // matches CategoryPagination on the API

export default async function CategoriesPage({ searchParams }: PageProps<"/categories">) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const [dict, lang, data] = await Promise.all([
    getDictionary(),
    getLang(),
    apiGet<{ count: number; results: Category[] }>(`/api/v1/admin/categories/?page=${page}`),
  ]);
  const t = dict.categories;
  const num = new Intl.NumberFormat(lang);
  const from = (page - 1) * PAGE_SIZE + 1;

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-center justify-between gap-6">
        <div>
          <h1 className="text-5xl font-bold tracking-tight text-gray-900">{t.title}</h1>
          <p className="mt-3 text-lg text-gray-600">{t.subtitle}</p>
        </div>
        <CategoryDialog t={t} />
      </div>

      <div className="mt-10 flex items-end justify-between rounded-2xl bg-white px-6 py-7 shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-700">{t.total}</p>
          <p className="mt-2 text-5xl font-semibold text-brand">{data ? num.format(data.count) : "—"}</p>
        </div>
        <span className="flex size-11 items-center justify-center rounded-xl bg-[#e3e8f7] text-brand"><Shapes className="size-5" /></span>
      </div>

      {!data ? (
        <p role="alert" className="mt-8 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{t.loadError}</p>
      ) : (
        <div className="mx-auto mt-10 max-w-3xl overflow-hidden rounded-2xl border border-gray-200 bg-white">
          <p className="border-b border-gray-200 bg-gray-50/60 px-8 py-6 text-sm font-semibold uppercase tracking-[0.12em] text-gray-600">{t.management}</p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="text-xs font-semibold uppercase tracking-wider text-gray-600">
                <tr className="border-b border-gray-200">
                  {[t.image, t.name, t.type, t.products, t.actions].map((h) => <th key={h} className="px-8 py-5 text-start font-semibold">{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {data.results.map((c) => (
                  <tr key={c.id} className="border-b border-gray-200 last:border-0">
                    <td className="px-8 py-4">
                      <Image src={c.image_url} alt={c.name} width={64} height={48} className="h-12 w-16 rounded-lg object-cover" />
                    </td>
                    <td className="px-8 py-4">
                      <p className="text-lg font-semibold text-gray-900">{c.name}</p>
                      <p className="text-sm text-gray-600">{c.description}</p>
                    </td>
                    <td className="px-8 py-4">
                      <span className={`rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider ${c.type === "premium" ? "bg-brand-light text-white" : "border border-blue-200 bg-[#e3e8f7] text-brand"}`}>
                        {t.types[c.type]}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-8 py-4 text-lg font-semibold text-gray-900">{num.format(c.products_count)} {t.items}</td>
                    <td className="px-8 py-4">
                      <div className="flex items-center gap-5">
                        <CategoryDialog t={t} category={c} />
                        <DeleteButton id={c.id} label={t.delete} confirmText={t.confirmDelete} errorText={t.deleteError} />
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
            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-gray-200 bg-gray-50/60 px-8 py-5">
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
