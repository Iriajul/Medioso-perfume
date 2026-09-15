"use client";

import { useTransition } from "react";
import { Globe } from "lucide-react";
import { LANGS, type Lang } from "@/i18n/dictionaries";
import { setLanguage } from "./actions";

export default function LanguageSwitcher({ lang }: { lang: Lang }) {
  const [pending, startTransition] = useTransition();

  return (
    <label className="flex items-center gap-2 rounded-full bg-gray-100/80 px-3 py-1.5 text-sm font-semibold text-brand">
      <Globe className="size-4" />
      <select
        aria-label="Language"
        value={lang}
        disabled={pending}
        onChange={(e) => startTransition(() => setLanguage(e.target.value as Lang))}
        className="cursor-pointer bg-transparent uppercase outline-none"
      >
        {LANGS.map((l) => <option key={l} value={l}>{l.toUpperCase()}</option>)}
      </select>
    </label>
  );
}
