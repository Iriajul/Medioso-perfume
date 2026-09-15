export function initials(name: string) {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]!.toUpperCase()).join("");
}

export default function Avatar({ name, className = "" }: { name: string; className?: string }) {
  return (
    <span className={`inline-flex shrink-0 items-center justify-center rounded-full bg-[#e3e8f7] font-semibold text-brand ${className}`}>
      {initials(name)}
    </span>
  );
}
