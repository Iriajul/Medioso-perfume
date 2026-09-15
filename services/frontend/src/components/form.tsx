// Shared auth form styles and icons.
export const inputClass =
  "w-full rounded-2xl border border-gray-100 bg-[#f8f9fd] py-4 pl-12 pr-4 text-base text-gray-900 placeholder:text-gray-300 outline-none focus:border-brand-light";

export const submitClass =
  "w-full rounded-2xl bg-gradient-to-r from-brand-light to-brand py-4 text-base tracking-[0.1em] text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70";

const iconProps = { width: 20, height: 20, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.6, "aria-hidden": true };
const leading = "absolute left-4 top-1/2 -translate-y-1/2 text-gray-400";

export function MailIcon() {
  return (
    <svg {...iconProps} className={leading}>
      <rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" />
    </svg>
  );
}

export function LockIcon() {
  return (
    <svg {...iconProps} className={leading}>
      <rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /><circle cx="12" cy="16" r="1" />
    </svg>
  );
}

export function EyeIcon() {
  return (
    <svg {...iconProps}>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" />
    </svg>
  );
}
