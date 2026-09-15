"use client";

import { useRef, useState, useTransition } from "react";
import { Trash2 } from "lucide-react";

type Props = { action: () => Promise<boolean>; label: string; confirmText: string; cancelText: string; errorText: string };

// Trash button + in-app confirmation (not window.confirm, which browsers let users silence).
// `action` is a bound server action that returns whether the delete succeeded.
export default function DeleteButton({ action, label, confirmText, cancelText, errorText }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [error, setError] = useState(false);
  const [pending, startTransition] = useTransition();

  const close = () => {
    dialog.current?.close();
    setError(false);
  };

  const confirm = () =>
    startTransition(async () => {
      if (await action()) close();
      else setError(true);
    });

  return (
    <>
      <button type="button" aria-label={label} onClick={() => dialog.current?.showModal()} className="text-gray-600 hover:text-red-600">
        <Trash2 className="size-4" />
      </button>

      <dialog ref={dialog} onClose={() => setError(false)} className="m-auto w-full max-w-sm rounded-3xl bg-white p-0 text-start shadow-2xl backdrop:bg-gray-900/30 backdrop:backdrop-blur-sm">
        <div className="px-7 pb-6 pt-7">
          <span className="flex size-11 items-center justify-center rounded-full bg-red-50 text-red-600"><Trash2 className="size-5" /></span>
          <p className="mt-4 text-lg font-semibold text-gray-900">{confirmText}</p>
          {error && <p role="alert" className="mt-2 text-sm text-red-600">{errorText}</p>}
        </div>
        <div className="flex justify-end gap-3 border-t border-gray-100 bg-gray-50/60 px-7 py-4">
          <button type="button" onClick={close} disabled={pending} className="rounded-xl px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-100">
            {cancelText}
          </button>
          <button type="button" onClick={confirm} disabled={pending} className="rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-red-700 disabled:opacity-60">
            {pending ? "…" : label}
          </button>
        </div>
      </dialog>
    </>
  );
}
