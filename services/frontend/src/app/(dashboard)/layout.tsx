import { Bell } from "lucide-react";
import { getDictionary, getLang } from "@/i18n/server";
import { getUser } from "@/lib/session";
import Avatar from "@/components/avatar";
import LanguageSwitcher from "./language-switcher";
import Sidebar from "./sidebar";

export default async function DashboardLayout({ children }: LayoutProps<"/">) {
  const [t, lang, user] = await Promise.all([getDictionary(), getLang(), getUser()]);

  return (
    <div className="flex min-h-screen">
      <Sidebar t={t} />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-20 items-center justify-end gap-6 bg-white/60 px-8 shadow-[0_1px_0_rgba(0,50,125,0.04)]">
          <LanguageSwitcher lang={lang} />
          <span className="relative text-gray-700" aria-label={t.nav.notifications}>
            <Bell className="size-5" />
            <span className="absolute -end-0.5 -top-0.5 size-2 rounded-full bg-red-500" />
          </span>
          <div className="flex items-center gap-3">
            <div className="text-end leading-tight">
              <p className="text-sm font-semibold text-gray-900">{user.name}</p>
              <p className="text-xs text-gray-500">{t.role.admin}</p>
            </div>
            <Avatar name={user.name} className="size-9 text-sm" />
          </div>
        </header>
        <main className="flex-1 px-8 py-10">{children}</main>
      </div>
    </div>
  );
}
