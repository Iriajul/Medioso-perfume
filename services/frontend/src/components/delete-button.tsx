"use client";

import { useTransition } from "react";
import { Trash2 } from "lucide-react";

// `action` is a bound server action that returns whether the delete succeeded.
export default function DeleteButton({ action, label, confirmText, errorText }: { action: () => Promise<boolean>; label: string; confirmText: string; errorText: string }) {
  const [pending, startTransition] = useTransition();

  return (
    <button
      type="button" aria-label={label} disabled={pending} className="text-gray-600 hover:text-red-600 disabled:opacity-40"
      onClick={() => confirm(confirmText) && startTransition(async () => { if (!(await action())) alert(errorText); })}
    >
      <Trash2 className="size-4" />
    </button>
  );
}
