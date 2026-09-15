"use client";

import { useTransition } from "react";
import { ChevronDown } from "lucide-react";
import { updateOrderStatus } from "../actions";

export default function StatusMenu({ id, current, options, label, errorText }: {
  id: number; current: string; options: [string, string][]; label: string; errorText: string;
}) {
  const [pending, startTransition] = useTransition();

  return (
    <details className="group relative">
      <summary className="flex cursor-pointer list-none items-center gap-3 rounded-xl bg-brand px-8 py-3 text-base uppercase tracking-wide text-white shadow-[0_8px_20px_rgba(0,50,125,0.3)] aria-disabled:opacity-60" aria-disabled={pending}>
        {label} <ChevronDown className="size-5 transition group-open:rotate-180" />
      </summary>
      <ul className="absolute end-0 z-10 mt-2 w-56 overflow-hidden rounded-xl border border-gray-100 bg-white py-1 shadow-xl">
        {options.map(([value, text]) => (
          <li key={value}>
            <button
              type="button" disabled={pending || value === current}
              onClick={(e) => {
                e.currentTarget.closest("details")?.removeAttribute("open");
                startTransition(async () => { if (!(await updateOrderStatus(id, value))) alert(errorText); });
              }}
              className="w-full px-4 py-2.5 text-start text-sm text-gray-800 hover:bg-gray-50 disabled:font-semibold disabled:text-brand"
            >
              {text}
            </button>
          </li>
        ))}
      </ul>
    </details>
  );
}
