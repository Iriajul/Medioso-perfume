import Image from "next/image";
import DeleteButton from "@/components/delete-button";
import Pagination from "@/components/pagination";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import { deleteBanner, deleteProduct } from "./actions";
import BannerDialog from "./banner-dialog";
import ProductDialog from "./product-dialog";

export type Option = { id: number; name: string };
export type Product = {
  id: number; sku: string; name: string; category: number; category_name: string; price: string; stock: number;
  description: string; is_featured: boolean; branches: number[]; image_urls: (string | null)[];
};
export type Banner = {
  id: number; title: string; image_url: string; starts_on: string; ends_on: string; is_active: boolean;
  status: "active" | "scheduled" | "ended" | "hidden";
};

const PAGE_SIZE = 4; // matches the API's product pagination
const STATUS_STYLES = { active: "bg-brand text-white", scheduled: "bg-gray-100 text-gray-700", ended: "bg-gray-700 text-white", hidden: "bg-gray-300 text-gray-800" };

export default async function ProductsPage({ searchParams }: PageProps<"/products">) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const [dict, lang, data, banners, categories, branches] = await Promise.all([
    getDictionary(),
    getLang(),
    apiGet<{ count: number; in_stock: number; revenue: string; results: Product[] }>(`/api/v1/admin/products/?page=${page}`),
    apiGet<Banner[]>("/api/v1/admin/banners/"),
    apiGet<Option[]>("/api/v1/admin/categories/options/"),
    apiGet<(Option & { address: string })[]>("/api/v1/admin/branches/options/"),
  ]);
  const t = dict.products;
  const num = new Intl.NumberFormat(lang);
  const money = new Intl.NumberFormat(lang, { style: "currency", currency: "USD" });
  const compactMoney = new Intl.NumberFormat(lang, { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 1 });
  const shortDate = new Intl.DateTimeFormat(lang, { month: "short", day: "numeric" });
  const from = (page - 1) * PAGE_SIZE + 1;
  const dialogProps = { t, categories: categories ?? [], branches: branches ?? [] };

  const bannerNote = (b: Banner) => {
    const today = new Date(new Date().toDateString());
    const date = (d: string) => shortDate.format(new Date(`${d}T00:00:00`));
    if (b.status === "active") {
      const days = Math.round((new Date(`${b.ends_on}T00:00:00`).getTime() - today.getTime()) / 86_400_000);
      return days <= 0 ? t.endsToday : t.endsIn.replace("{n}", num.format(days));
    }
    if (b.status === "scheduled") return t.startsOn.replace("{date}", date(b.starts_on));
    return b.status === "ended" ? t.endedOn.replace("{date}", date(b.ends_on)) : t.hiddenNote;
  };

  return (
    <div className="mx-auto max-w-5xl">
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-gray-700">{t.breadcrumbAdmin} / <span className="text-brand-light">{t.breadcrumbInventory}</span></p>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-6">
        <h1 className="text-5xl font-bold tracking-tight text-brand">{t.title}</h1>
        <ProductDialog {...dialogProps} />
      </div>

      <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2">
        {[[t.inStock, data && num.format(data.in_stock)], [t.revenue, data && compactMoney.format(Number(data.revenue))]].map(([label, value]) => (
          <div key={label} className="rounded-2xl bg-white px-6 py-7 shadow-[0_8px_30px_rgba(0,50,125,0.08)]">
            <p className="text-[11px] font-medium uppercase tracking-[0.15em] text-gray-700">{label}</p>
            <p className="mt-2 text-lg text-gray-900">{value ?? "—"}</p>
          </div>
        ))}
      </div>

      {!data ? (
        <p role="alert" className="mt-8 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{t.loadError}</p>
      ) : (
        <div className="mt-12 overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.08)]">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-b from-[#eef0fb] to-[#e6e9f8] text-xs font-semibold uppercase tracking-[0.15em] text-gray-700">
                <tr>
                  {[t.image, t.name, t.category, t.price].map((h) => <th key={h} className="px-8 py-6 text-start font-semibold">{h}</th>)}
                  <th className="px-8 py-6 text-end font-semibold">{t.actions}</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((p) => (
                  <tr key={p.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-8 py-6">
                      <span className="relative block size-16 overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
                        {p.image_urls.find(Boolean) && <Image src={p.image_urls.find(Boolean)!} alt={p.name} fill className="object-cover p-2" sizes="64px" />}
                      </span>
                    </td>
                    <td className="px-8 py-6">
                      <p className="text-lg text-gray-900">{p.name}</p>
                      <p className="mt-1 text-[11px] font-medium uppercase tracking-[0.1em] text-gray-700">{t.sku}: {p.sku}</p>
                    </td>
                    <td className="px-8 py-6">
                      <span className="rounded-full bg-[#e3e8f7] px-4 py-1 text-[11px] font-bold uppercase tracking-wider text-brand">{p.category_name}</span>
                    </td>
                    <td className="px-8 py-6 text-lg font-semibold text-brand">{money.format(Number(p.price))}</td>
                    <td className="px-8 py-6">
                      <div className="flex items-center justify-end gap-6">
                        <ProductDialog {...dialogProps} product={p} />
                        <DeleteButton action={deleteProduct.bind(null, p.id)} label={t.delete} cancelText={dict.common.cancel} confirmText={t.confirmDelete} errorText={t.deleteError} />
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
            <div className="flex flex-wrap items-center justify-between gap-4 px-8 py-6">
              <p className="text-base text-gray-700">
                {t.showing.replace("{from}", num.format(from)).replace("{to}", num.format(Math.min(from + PAGE_SIZE - 1, data.count))).replace("{total}", num.format(data.count))}
              </p>
              <Pagination page={page} pageCount={Math.ceil(data.count / PAGE_SIZE)} />
            </div>
          )}
        </div>
      )}

      <div className="mt-14 flex flex-wrap items-center justify-between gap-6">
        <h2 className="text-4xl font-bold tracking-tight text-brand">{t.banners}</h2>
        <BannerDialog t={t} />
      </div>
      <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
        {banners?.length === 0 && <p className="text-gray-500">{t.noBanners}</p>}
        {banners?.map((b) => (
          <div key={b.id} className="rounded-2xl bg-white p-5 shadow-[0_8px_30px_rgba(0,50,125,0.08)]">
            <div className="relative aspect-[432/158] overflow-hidden rounded-xl">
              <Image src={b.image_url} alt={b.title} fill className="object-cover" sizes="(min-width: 640px) 440px, 100vw" />
              <span className={`absolute end-2 top-2 rounded-full px-3 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${STATUS_STYLES[b.status]}`}>{t.bannerStatus[b.status]}</span>
            </div>
            <div className="mt-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-lg text-gray-900">{b.title}</p>
                <p className="text-[11px] font-medium uppercase tracking-[0.1em] text-gray-700">{bannerNote(b)}</p>
              </div>
              <div className="flex items-center gap-6">
                <BannerDialog t={t} banner={b} />
                <DeleteButton action={deleteBanner.bind(null, b.id)} label={t.delete} cancelText={dict.common.cancel} confirmText={t.confirmDeleteBanner} errorText={t.deleteBannerError} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
