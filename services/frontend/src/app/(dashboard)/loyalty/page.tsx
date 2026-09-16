import Image from "next/image";
import { Medal, TrendingUp } from "lucide-react";
import DeleteButton from "@/components/delete-button";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import { deleteReward } from "./actions";
import Redemptions, { type Redemption } from "./redemptions";
import RewardDialog from "./reward-dialog";

export type Reward = {
  id: number; name: string; points_required: number; discount_amount: string; category: "physical_product" | "experience" | "service";
  eligibility: "all" | "gold" | "platinum" | "diamond"; description: string; image_url: string; is_active: boolean;
};

export default async function LoyaltyPage({ searchParams }: PageProps<"/loyalty">) {
  const filters = await searchParams;
  const query = typeof filters.q === "string" ? filters.q : "";
  const status = typeof filters.status === "string" ? filters.status : "all";
  const page = Math.max(1, Number(filters.page) || 1);
  const redemptionQuery = new URLSearchParams({
    page: String(page), ...(query && { search: query }), ...(status !== "all" && { status }),
  });
  const [dict, lang, data, redemptions] = await Promise.all([
    getDictionary(), getLang(),
    apiGet<{ total_redemptions: number; redemptions_trend: number | null; results: Reward[] }>("/api/v1/admin/rewards/"),
    apiGet<{ count: number; pending_count: number; results: Redemption[] }>(`/api/v1/admin/redemptions/?${redemptionQuery}`),
  ]);
  const t = dict.loyalty;
  const num = new Intl.NumberFormat(lang);

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div className="max-w-xl">
          <h1 className="text-5xl font-bold tracking-tight text-brand-light">{t.title}</h1>
          <p className="mt-4 text-lg leading-8 text-gray-700">{t.subtitle}</p>
        </div>
        <RewardDialog t={t} />
      </div>

      <div className="mt-10 rounded-3xl bg-white px-8 py-8 shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
        <div className="flex items-start justify-between">
          <span className="flex size-9 items-center justify-center rounded-xl bg-[#e3e8f7] text-brand"><Medal className="size-4" /></span>
          {data?.redemptions_trend != null && (
            <span className="flex items-center gap-1 rounded-full bg-green-50 px-2 py-0.5 text-sm font-semibold text-green-600" dir="ltr">
              <TrendingUp className="size-4" />{data.redemptions_trend > 0 ? "+" : ""}{data.redemptions_trend}%
            </span>
          )}
        </div>
        <p className="mt-6 text-xs font-semibold uppercase tracking-[0.15em] text-gray-700">{t.totalRedemptions}</p>
        <p className="mt-2 text-2xl font-semibold text-gray-900">{data ? num.format(data.total_redemptions) : "—"}</p>
      </div>

      <h2 className="mt-12 flex items-center gap-4 text-2xl font-semibold text-gray-900"><span className="h-8 w-1.5 rounded-full bg-brand-light" />{t.availableTiers}</h2>
      {!data && <p role="alert" className="mt-6 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{dict.common.loadError}</p>}
      {data?.results.length === 0 && <p className="mt-6 text-gray-500">{t.empty}</p>}

      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
        {data?.results.map((r) => (
          <article key={r.id} className="flex min-h-72 overflow-hidden rounded-3xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
            <div className="relative w-2/5 shrink-0">
              <Image src={r.image_url} alt={r.name} fill className="object-cover" sizes="(min-width: 1024px) 200px, 40vw" />
            </div>
            <div className="flex flex-1 flex-col p-6">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-lg font-semibold text-gray-900">{r.name}</h3>
                <span className="shrink-0 rounded-2xl bg-[#e3e8f7] px-3 py-1 text-center font-semibold leading-5 text-brand-light">{num.format(r.points_required)}<br />{dict.common.pts}</span>
              </div>
              <p className="mt-2 line-clamp-2 text-base text-gray-700">{r.description}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {[t.categories[r.category], t.eligibility[r.eligibility]].map((tag) => (
                  <span key={tag} className="rounded-full bg-[#e3e8f7] px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-gray-700">{tag}</span>
                ))}
              </div>
              <div className="mt-auto flex justify-end gap-3 pt-6">
                <RewardDialog t={t} reward={r} />
                <span className="flex size-9 items-center justify-center rounded-full bg-white shadow">
                  <DeleteButton action={deleteReward.bind(null, r.id)} label={t.delete} cancelText={dict.common.cancel} confirmText={t.confirmDelete} errorText={t.deleteError} />
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>

      <Redemptions t={t} common={dict.common} lang={lang} data={redemptions} query={query} status={status} page={page} />
    </div>
  );
}
