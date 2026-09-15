import { getDictionary } from "@/i18n/server";
import NotificationForm from "./notification-form";

export default async function NotificationsPage() {
  const t = (await getDictionary()).notifications;
  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-5xl font-bold tracking-tight text-brand-light">{t.title}</h1>
      <p className="mt-3 max-w-md text-base leading-6 text-gray-700">{t.subtitle}</p>
      <NotificationForm t={t} />
    </div>
  );
}
