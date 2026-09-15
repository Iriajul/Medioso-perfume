import Image from "next/image";
import { MapPin } from "lucide-react";
import Avatar from "@/components/avatar";
import DeleteButton from "@/components/delete-button";
import ListFooter from "@/components/list-footer";
import { getDictionary, getLang } from "@/i18n/server";
import { apiGet } from "@/lib/session";
import { deleteStaff } from "./actions";
import StaffDialog from "./staff-dialog";

export type StaffMember = {
  id: number; full_name: string; email: string; branch: number | null; branch_name: string | null;
  job_title: string; is_active: boolean; avatar_url: string;
};

const PAGE_SIZE = 4;

export default async function StaffPage({ searchParams }: PageProps<"/staff">) {
  const page = Math.max(1, Number((await searchParams).page) || 1);
  const [dict, lang, data, branches] = await Promise.all([
    getDictionary(), getLang(),
    apiGet<{ count: number; total_staff: number; active_staff: number; results: StaffMember[] }>(`/api/v1/admin/staff/?page=${page}`),
    apiGet<{ id: number; name: string }[]>("/api/v1/admin/branches/options/"),
  ]);
  const t = dict.staff;
  const num = new Intl.NumberFormat(lang);
  const from = (page - 1) * PAGE_SIZE + 1;

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">{t.title}</h1>
          <p className="mt-3 text-base text-gray-600">{t.subtitle}</p>
        </div>
        <StaffDialog t={t} branches={branches ?? []} />
      </div>

      <div className="mt-8 grid grid-cols-1 items-start gap-6 lg:grid-cols-[220px_1fr]">
        <aside className="rounded-3xl bg-white/80 px-6 py-7 shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
          <p className="text-[11px] font-semibold uppercase tracking-[0.15em] text-gray-600">{t.overview}</p>
          <dl className="mt-5 space-y-5">
            <div className="flex items-center justify-between"><dt className="text-sm text-gray-700">{t.total}</dt><dd className="text-xl font-semibold text-gray-900">{data ? num.format(data.total_staff) : "—"}</dd></div>
            <div className="flex items-center justify-between"><dt className="text-sm text-gray-700">{t.active}</dt><dd className="text-xl font-semibold text-brand-light">{data ? num.format(data.active_staff) : "—"}</dd></div>
          </dl>
        </aside>

        {!data ? (
          <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{dict.common.loadError}</p>
        ) : (
          <div className="overflow-hidden rounded-2xl bg-white shadow-[0_8px_30px_rgba(0,50,125,0.06)]">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#eef1fb] text-[10px] font-semibold uppercase tracking-[0.12em] text-gray-600">
                  <tr>{[t.name, t.branch, t.role, t.actions].map((h) => <th key={h} className="max-w-20 px-6 py-5 text-start font-semibold">{h}</th>)}</tr>
                </thead>
                <tbody>
                  {data.results.map((s) => (
                    <tr key={s.id} className="border-b border-gray-100 last:border-0">
                      <td className="px-6 py-5">
                        <span className="flex items-center gap-3">
                          {s.avatar_url
                            ? <Image src={s.avatar_url} alt="" width={44} height={44} className="size-11 rounded-xl object-cover" />
                            : <Avatar name={s.full_name} className="size-11 rounded-xl text-sm" />}
                          <span>
                            <span className="block font-semibold text-gray-900">{s.full_name}{!s.is_active && <span className="ms-2 rounded bg-gray-100 px-1.5 text-[10px] font-semibold uppercase text-gray-500">{t.inactive}</span>}</span>
                            <span className="block text-xs text-gray-500">{s.email}</span>
                          </span>
                        </span>
                      </td>
                      <td className="max-w-28 px-6 py-5"><span className="flex items-start gap-2 text-sm text-gray-700"><MapPin className="mt-0.5 size-4 shrink-0 text-blue-300" />{s.branch_name ?? "—"}</span></td>
                      <td className="max-w-28 px-6 py-5 text-sm text-gray-700">{s.job_title}</td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-5">
                          <StaffDialog t={t} branches={branches ?? []} member={s} />
                          <DeleteButton action={deleteStaff.bind(null, s.id)} label={t.delete} confirmText={t.confirmDelete} errorText={t.deleteError} />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {data.count === 0 ? (
              <p className="px-6 py-10 text-center text-gray-500">{t.empty}</p>
            ) : (
              <ListFooter
                text={t.showing.replace("{from}", num.format(from)).replace("{to}", num.format(Math.min(from + PAGE_SIZE - 1, data.count))).replace("{total}", num.format(data.count))}
                page={page} pageCount={Math.ceil(data.count / PAGE_SIZE)}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
