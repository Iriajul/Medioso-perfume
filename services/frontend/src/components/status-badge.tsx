const STYLES: Record<string, string> = {
  pending_payment: "border border-red-200 bg-red-50 text-red-700",
  paid: "bg-blue-50 text-brand",
  processing: "bg-[#e9edf9] text-gray-600",
  shipped: "border border-gray-300 bg-gray-100 text-gray-800",
  delivered: "bg-green-50 text-green-700",
  cancelled: "bg-gray-200 text-gray-600",
  in_store: "bg-brand text-white",
};

export default function StatusBadge({ status, label, className = "" }: { status: string; label: string; className?: string }) {
  return (
    <span className={`inline-block rounded-md px-3 py-1 text-xs font-semibold ${STYLES[status] ?? "bg-gray-100 text-gray-600"} ${className}`}>
      {label}
    </span>
  );
}
