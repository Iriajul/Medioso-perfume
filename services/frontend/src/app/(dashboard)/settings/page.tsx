import { getDictionary, getLang } from "@/i18n/server";
import { timeAgo } from "@/lib/format";
import { apiGet } from "@/lib/session";
import PasswordForm from "./password-form";

export default async function SettingsPage() {
  const [dict, lang, me] = await Promise.all([getDictionary(), getLang(), apiGet<{ password_changed_at: string | null }>("/api/v1/auth/me/")]);
  const t = dict.settings;
  const changed = me?.password_changed_at;

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-4xl font-bold tracking-tight text-gray-900">{t.title}</h1>
      <p className="mt-3 max-w-2xl text-base text-gray-600">{t.subtitle}</p>
      <PasswordForm t={t} />
      <p className="mt-10 text-center text-sm text-gray-600">
        {t.lastChange}{" "}
        <span className="rounded-md bg-gray-100 px-2 py-1 font-semibold text-gray-900">
          {changed ? `${new Intl.DateTimeFormat(lang, { dateStyle: "medium" }).format(new Date(changed))} (${timeAgo(lang, changed)})` : t.never}
        </span>
      </p>
    </div>
  );
}
