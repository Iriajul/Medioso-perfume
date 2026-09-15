"use client";

import Image from "next/image";
import { startTransition, useActionState, useRef, useState } from "react";
import { ArrowRight, FileUp, Plus, Shapes, SquarePen, X } from "lucide-react";
import type { Dictionary } from "@/i18n/dictionaries";
import type { SaveState } from "@/lib/session";
import { saveCategory } from "./actions";
import type { Category } from "./page";

const field = "w-full rounded-xl border border-gray-300 px-4 py-3 text-base text-gray-900 placeholder:text-gray-300 outline-none focus:border-brand-light";

export default function CategoryDialog({ t, category }: { t: Dictionary["categories"]; category?: Category }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const form = useRef<HTMLFormElement>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const close = () => {
    dialog.current?.close();
    form.current?.reset();
    setPreview(null);
  };

  // Close after a successful save; the page re-renders with fresh data.
  const [state, action, pending] = useActionState(async (prev: SaveState, formData: FormData) => {
    const result = await saveCategory(category?.id ?? null, prev, formData);
    if (result?.ok) close();
    return result;
  }, undefined);

  return (
    <>
      {category ? (
        <button type="button" onClick={() => dialog.current?.showModal()} aria-label={t.edit} className="text-gray-600 hover:text-brand">
          <SquarePen className="size-4" />
        </button>
      ) : (
        <button
          type="button"
          onClick={() => dialog.current?.showModal()}
          className="flex items-center gap-2 rounded-xl bg-brand px-7 py-4 text-base uppercase tracking-[0.08em] text-white shadow-[0_8px_20px_rgba(0,50,125,0.3)]"
        >
          <Plus className="size-5" /> {t.add}
        </button>
      )}

      <dialog
        ref={dialog}
        onClose={close}
        className="m-auto w-full max-w-[640px] rounded-[36px] bg-white p-0 text-start shadow-2xl backdrop:bg-gray-900/30 backdrop:backdrop-blur-sm"
      >
        <div className="flex items-center gap-4 border-b border-gray-200 bg-gray-50/60 px-8 py-6">
          <span className="flex size-10 items-center justify-center rounded-full bg-[#e3e8f7] text-brand"><Shapes className="size-5" /></span>
          <div className="flex-1">
            <h2 className="text-2xl font-semibold text-gray-900">{category ? t.editTitle : t.newTitle}</h2>
            <p className="text-sm text-gray-600">{t.modalSubtitle}</p>
          </div>
          <button type="button" onClick={close} aria-label="Close" className="text-gray-600"><X className="size-6" /></button>
        </div>

        <form
          ref={form}
          // onSubmit (not action=) so a failed save keeps what the admin typed.
          onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); startTransition(() => action(data)); }}
          className="space-y-6 px-8 py-8">
          <div>
            <p className="text-base text-gray-700">{t.imageLabel}</p>
            <label className="relative mt-3 flex h-44 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-gray-300 text-center">
              {(preview ?? category?.image_url) && (
                <Image src={preview ?? category!.image_url} alt="" fill unoptimized={!!preview} className="object-cover opacity-40" sizes="580px" />
              )}
              <FileUp className="relative size-7 text-brand" />
              <span className="relative mt-3 text-base font-medium text-gray-900">{t.upload}</span>
              <span className="relative text-xs text-gray-600">{t.uploadHint}</span>
              <input
                type="file" name="image" accept="image/png,image/jpeg,image/webp" required={!category} className="sr-only"
                onChange={(e) => { const f = e.target.files?.[0]; setPreview(f ? URL.createObjectURL(f) : null); }}
              />
            </label>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <label className="block">
              <span className="text-base text-gray-700">{t.name}</span>
              <input name="name" required maxLength={100} defaultValue={category?.name} placeholder={t.namePlaceholder} className={`${field} mt-3`} />
            </label>
            <label className="block">
              <span className="text-base text-gray-700">{t.typeLabel}</span>
              <select name="type" required defaultValue={category?.type ?? ""} className={`${field} mt-3 bg-white`}>
                <option value="" disabled>{t.selectType}</option>
                {Object.entries(t.types).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
          </div>

          <label className="block">
            <span className="text-base text-gray-700">{t.description}</span>
            <textarea name="description" rows={3} defaultValue={category?.description} placeholder={t.descriptionPlaceholder} className={`${field} mt-3 resize-none`} />
          </label>

          {state?.errors?.map((e) => <p key={e} role="alert" className="text-sm text-red-600">{e}</p>)}

          <div className="flex items-center justify-end gap-10 border-t border-gray-200 pt-6">
            <button type="button" onClick={close} className="text-base text-gray-600">{t.discard}</button>
            <button type="submit" disabled={pending} className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-light to-brand px-8 py-3 text-base text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70">
              {pending ? t.saving : t.save} <ArrowRight className="size-4 rtl:-scale-x-100" />
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
