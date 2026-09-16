import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";

// Page links for DRF page-number pagination (?page=N).
export default function Pagination({ page, pageCount, params }: { page: number; pageCount: number; params?: Record<string, string> }) {
  if (pageCount <= 1) return null;
  const href = (n: number) => `?${new URLSearchParams({ ...params, page: String(n) })}`;
  const box = "flex size-10 items-center justify-center rounded-xl border text-sm";
  const arrow = (target: number, Icon: typeof ChevronLeft) =>
    target < 1 || target > pageCount ? (
      <span className={`${box} border-gray-100 text-gray-300`}><Icon className="size-4 rtl:-scale-x-100" /></span>
    ) : (
      <Link href={href(target)} className={`${box} border-gray-200 text-gray-700`}><Icon className="size-4 rtl:-scale-x-100" /></Link>
    );

  return (
    <nav className="flex items-center gap-2">
      {arrow(page - 1, ChevronLeft)}
      {Array.from({ length: pageCount }, (_, i) => i + 1).map((n) => (
        <Link
          key={n}
          href={href(n)}
          aria-current={n === page ? "page" : undefined}
          className={`${box} ${n === page ? "border-brand bg-brand text-white" : "border-gray-200 text-gray-700"}`}
        >
          {n}
        </Link>
      ))}
      {arrow(page + 1, ChevronRight)}
    </nav>
  );
}
