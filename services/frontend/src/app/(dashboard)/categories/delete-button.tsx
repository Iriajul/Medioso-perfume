"use client";

import { useTransition } from "react";
import { Trash2 } from "lucide-react";
import { deleteCategory } from "./actions";

export default function DeleteButton({ id, label, confirmText, errorText }: { id: number; label: string; confirmText: string; errorText: string }) {
  const [pending, startTransition] = useTransition();

  return (
    <button
      type="button" aria-label={label} disabled={pending} className="text-gray-600 hover:text-red-600 disabled:opacity-40"
      onClick={() => confirm(confirmText) && startTransition(async () => { if (!(await deleteCategory(id))) alert(errorText); })}
    >
      <Trash2 className="size-4" />
    </button>
  );
}
