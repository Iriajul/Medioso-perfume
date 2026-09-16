"use client";

import Image from "next/image";
import { useState } from "react";
import { ArrowRight, CloudUpload, Pencil, Plus, Star, X } from "lucide-react";
import { useFormDialog } from "@/components/use-form-dialog";
import type { Dictionary } from "@/i18n/dictionaries";
import type { SaveState } from "@/lib/session";
import { saveReward } from "./actions";
import type { Reward } from "./page";

const field = "w-full rounded-lg border border-[#e6d9c8] bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-400 outline-none focus:border-brand-light";
const label = "text-xs font-medium uppercase tracking-wide text-gray-700";

export default function RewardDialog({ t, reward }: { t: Dictionary["loyalty"]; reward?: Reward }) {
  const [preview, setPreview] = useState<string | null>(null);
  const { dialogRef, formRef, open, close, state, pending, onSubmit } = useFormDialog(
    (prev: SaveState, formData: FormData) => saveReward(reward?.id ?? null, prev, formData),
    () => setPreview(null),
  );
  const src = preview ?? reward?.image_url;

  return (
    <>
      {reward ? (
        <button type="button" onClick={open} aria-label={t.edit} className="flex size-9 items-center justify-center rounded-full bg-white text-gray-700 shadow hover:text-brand"><Pencil className="size-4" /></button>
      ) : (
        <button type="button" onClick={open} className="flex items-center gap-2 rounded-full bg-brand-light px-8 py-4 text-base font-semibold text-white shadow-[0_10px_30px_rgba(0,68,165,0.35)]">
          <Plus className="size-5" /> {t.add}
        </button>
      )}

      <dialog ref={dialogRef} onClose={close} className="m-auto max-h-[94vh] w-full max-w-[672px] rounded-2xl bg-[#f7f7f7] p-0 text-start shadow-2xl backdrop:bg-gray-900/30 backdrop:backdrop-blur-sm">
        <div className="flex items-start border-b border-gray-200 bg-[#f3f3f3] px-8 py-7">
          <div className="flex-1">
            <h2 className="text-2xl text-gray-900">{reward ? t.editTitle : t.newTitle}</h2>
            <p className="mt-1 text-sm text-gray-700">{t.modalSubtitle}</p>
          </div>
          <button type="button" onClick={close} aria-label="Close" className="text-gray-700"><X className="size-6" /></button>
        </div>

        <form ref={formRef} onSubmit={onSubmit}>
          <div className="space-y-7 px-8 py-8">
            <div>
              <p className={label}>{t.imageLabel}</p>
              <label className="relative mt-3 flex h-56 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-lg border-2 border-dashed border-[#d9c7b0] text-center">
                {src && <Image src={src} alt="" fill unoptimized={!!preview} className="object-cover opacity-40" sizes="610px" />}
                <span className="relative flex size-16 items-center justify-center rounded-full bg-[#dfe6f3] text-brand-light"><CloudUpload className="size-7" /></span>
                <span className="relative mt-5 text-base font-medium text-gray-900">{t.upload}</span>
                <span className="relative mt-1 text-sm text-gray-700">{t.uploadHint}</span>
                <input type="file" name="image" accept="image/png,image/jpeg,image/webp" required={!reward} className="sr-only"
                  onChange={(e) => { const f = e.target.files?.[0]; setPreview(f ? URL.createObjectURL(f) : null); }} />
              </label>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <label className="block"><span className={label}>{t.name}</span>
                <input name="name" required maxLength={150} defaultValue={reward?.name} placeholder={t.namePlaceholder} className={`${field} mt-3`} />
              </label>
              <label className="block"><span className={label}>{t.requiredPoints}</span>
                <span className="relative mt-3 block">
                  <input name="points_required" type="number" required min="1" step="1" defaultValue={reward?.points_required} placeholder="1200" className={`${field} pe-10`} dir="ltr" />
                  <Star className="absolute end-3 top-1/2 size-5 -translate-y-1/2 text-brand-light" />
                </span>
              </label>
              <label className="block"><span className={label}>{t.discountAmount}</span>
                <span className="relative mt-3 block">
                  <input name="discount_amount" type="number" min="0" step="0.01" defaultValue={reward?.discount_amount ?? "0.00"} placeholder="20.00" className={`${field} pe-10`} dir="ltr" />
                  <span className="absolute end-3 top-1/2 -translate-y-1/2 text-brand-light">$</span>
                </span>
                <span className="mt-2 block text-sm font-normal normal-case tracking-normal text-gray-600">{t.discountHint}</span>
              </label>
              <label className="block"><span className={label}>{t.category}</span>
                <select name="category" required defaultValue={reward?.category ?? ""} className={`${field} mt-3`}>
                  <option value="" disabled>{t.selectCategory}</option>
                  {Object.entries(t.categories).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </label>
              <label className="block"><span className={label}>{t.eligibilityLabel}</span>
                <select name="eligibility" required defaultValue={reward?.eligibility ?? "all"} className={`${field} mt-3`}>
                  {Object.entries(t.eligibility).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </label>
            </div>

            <label className="block"><span className={label}>{t.description}</span>
              <textarea name="description" rows={4} defaultValue={reward?.description} placeholder={t.descriptionPlaceholder} className={`${field} mt-3 resize-none`} />
            </label>

            {state?.errors?.map((e) => <p key={e} role="alert" className="text-sm text-red-600">{e}</p>)}
          </div>

          <div className="flex items-center justify-end gap-6 border-t border-gray-200 bg-[#f3f3f3] px-8 py-6">
            <button type="button" onClick={close} className="text-sm uppercase tracking-[0.1em] text-gray-700">{t.discard}</button>
            <button type="submit" disabled={pending} className="flex items-center gap-2 rounded-lg bg-gradient-to-b from-brand-light to-brand px-8 py-3 text-base text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70">
              {pending ? t.saving : reward ? t.update : t.save} <ArrowRight className="size-4 rtl:-scale-x-100" />
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
