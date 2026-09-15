"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Contact, LayoutGrid, LogOut, Package, Settings, Shapes, ShoppingCart, Star, Store, Users } from "lucide-react";
import type { Dictionary } from "@/i18n/dictionaries";
import { logout } from "./actions";

const NAV = [
  ["/", "dashboard", LayoutGrid],
  ["/products", "products", Package],
  ["/categories", "categories", Shapes],
  ["/orders", "orders", ShoppingCart],
  ["/customers", "customers", Users],
  ["/loyalty", "loyalty", Star],
  ["/branches", "branches", Store],
  ["/staff", "staff", Contact],
  ["/notifications", "notifications", Bell],
  ["/settings", "settings", Settings],
] as const;

export default function Sidebar({ t }: { t: Dictionary }) {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col bg-white px-6 py-8">
      <div className="px-2">
        <p className="text-3xl font-bold leading-tight text-brand">MAD<br />PERFUME</p>
        <p className="mt-1 text-sm text-gray-600">{t.brandSubtitle}</p>
      </div>

      <nav className="mt-10 space-y-2">
        {NAV.map(([href, key, Icon]) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-xl px-4 py-3 text-base ${active ? "bg-brand text-white shadow-[0_8px_20px_rgba(0,50,125,0.25)]" : "text-gray-700 hover:bg-gray-50"}`}
            >
              <Icon className="size-5" strokeWidth={1.8} />
              {t.nav[key]}
            </Link>
          );
        })}
      </nav>

      <form action={logout} className="mt-auto border-t border-gray-200 pt-6">
        <button type="submit" className="flex w-full items-center gap-3 px-4 py-2 text-base text-gray-700 hover:text-brand">
          <LogOut className="size-5 rtl:-scale-x-100" strokeWidth={1.8} />
          {t.nav.logout}
        </button>
      </form>
    </aside>
  );
}
