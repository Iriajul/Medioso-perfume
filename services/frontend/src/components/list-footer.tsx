import Pagination from "./pagination";

// "Showing N of TOTAL noun" + page links, for paginated admin tables.
export default function ListFooter({ text, page, pageCount, className = "" }: { text: string; page: number; pageCount: number; className?: string }) {
  return (
    <div className={`flex flex-wrap items-center justify-between gap-4 px-8 py-5 ${className}`}>
      <p className="text-sm text-gray-600">{text}</p>
      <Pagination page={page} pageCount={pageCount} />
    </div>
  );
}
