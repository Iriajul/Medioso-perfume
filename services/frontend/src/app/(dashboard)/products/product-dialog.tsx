"use client";

import Image from "next/image";
import { useState } from "react";
import { ArrowRight, ImagePlus, Pencil, Plus, X } from "lucide-react";
import { useFormDialog } from "@/components/use-form-dialog";
import type { Dictionary } from "@/i18n/dictionaries";
import type { SaveState } from "@/lib/session";
import { saveProduct } from "./actions";
import type { Option, Product } from "./page";

const field = "w-full rounded-xl border border-gray-400 bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-400 outline-none focus:border-brand-light";
const label = "text-xs font-medium uppercase tracking-wide text-gray-700";
const SLOTS = [0, 1, 2];

type Props = { t: Dictionary["products"]; categories: Option[]; branches: (Option & { address: string })[]; product?: Product };

export default function ProductDialog({ t, categories, branches, product }: Props) {
  const [previews, setPreviews] = useState<(string | null)[]>([null, null, null]);
  const { dialogRef, formRef, open, close, state, pending, onSubmit } = useFormDialog(
    (prev: SaveState, formData: FormData) => saveProduct(product?.id ?? null, prev, formData),
    () => setPreviews([null, null, null]),
  );

  const selectAll = () => formRef.current?.querySelectorAll<HTMLInputElement>("input[name=branches]").forEach((c) => (c.checked = true));

  return (
    <>
      {product ? (
        <button type="button" onClick={open} aria-label={t.edit} className="text-brand hover:text-brand-light"><Pencil className="size-5" /></button>
      ) : (
        <button type="button" onClick={open} className="flex items-center gap-3 rounded-2xl bg-brand px-10 py-5 text-base font-semibold uppercase tracking-[0.1em] text-white shadow-[0_10px_30px_rgba(0,50,125,0.35)]">
          <Plus className="size-5" /> {t.add}
        </button>
      )}

      <dialog ref={dialogRef} onClose={close} className="m-auto max-h-[94vh] w-full max-w-[640px] rounded-2xl bg-white p-0 text-start shadow-2xl backdrop:bg-gray-900/30 backdrop:backdrop-blur-sm">
        <div className="flex items-start border-b border-gray-200 px-8 py-6">
          <div className="flex-1">
            <h2 className="text-base text-gray-900">{product ? t.editTitle : t.newTitle}</h2>
            <p className="mt-1 text-base text-gray-900">{t.modalSubtitle}</p>
          </div>
          <button type="button" onClick={close} aria-label="Close" className="text-gray-900"><X className="size-6" /></button>
        </div>

        <form ref={formRef} onSubmit={onSubmit}>
          <div className="space-y-6 px-8 py-7">
            <div>
              <p className={label}>{t.imagery}</p>
              <div className="mt-3 grid grid-cols-3 gap-4">
                {SLOTS.map((i) => {
                  const src = previews[i] ?? product?.image_urls[i];
                  return (
                    <label key={i} className="relative flex aspect-[9/8] cursor-pointer flex-col items-center justify-center overflow-hidden rounded-lg border-2 border-dashed border-gray-300 text-sm text-gray-900">
                      {src && <Image src={src} alt="" fill unoptimized={!!previews[i]} className="object-cover" sizes="180px" />}
                      {!src && <><span className="flex size-9 items-center justify-center rounded-full bg-gray-50"><ImagePlus className="size-4" /></span><span className="mt-3">{t.uploadImage}</span></>}
                      <input
                        type="file" name={`image_${i + 1}`} accept="image/png,image/jpeg,image/webp" className="sr-only"
                        required={i === 0 && !product}
                        onChange={(e) => { const f = e.target.files?.[0]; setPreviews((p) => p.map((v, j) => (j === i ? (f ? URL.createObjectURL(f) : null) : v))); }}
                      />
                    </label>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <label className="block"><span className={label}>{t.name}</span>
                <input name="name" required maxLength={150} defaultValue={product?.name} placeholder={t.namePlaceholder} className={`${field} mt-3`} />
              </label>
              <label className="block"><span className={label}>{t.fragranceCategory}</span>
                <select name="category" required defaultValue={product?.category ?? ""} className={`${field} mt-3`}>
                  <option value="" disabled>{t.selectCategory}</option>
                  {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </label>
              <label className="block"><span className={label}>{t.retailPrice}</span>
                <span className="relative mt-3 block">
                  <span className="absolute start-4 top-1/2 -translate-y-1/2 text-gray-900">$</span>
                  <input name="price" type="number" required min="0" step="0.01" defaultValue={product?.price} placeholder="0.00" className={`${field} ps-9`} dir="ltr" />
                </span>
              </label>
              <label className="block"><span className={label}>{t.stockUnits}</span>
                <input name="stock" type="number" required min="0" step="1" defaultValue={product?.stock ?? 0} className={`${field} mt-3`} dir="ltr" />
              </label>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <p className="text-[11px] font-medium uppercase tracking-wide text-gray-700">{t.branchAvailability}</p>
                {branches.length > 0 && <button type="button" onClick={selectAll} className="text-[11px] text-gray-900 hover:underline">{t.selectAllBranches}</button>}
              </div>
              <div className="mt-3 grid grid-cols-1 gap-x-6 gap-y-4 rounded-lg border border-gray-200 p-5 sm:grid-cols-2">
                {branches.length === 0 && <p className="text-sm text-gray-500">{t.noBranches}</p>}
                {branches.map((b) => (
                  <label key={b.id} className="flex items-start gap-3">
                    <input type="checkbox" name="branches" value={b.id} defaultChecked={product?.branches.includes(b.id) ?? true} className="mt-0.5 size-5 accent-blue-600" />
                    <span><span className="block text-sm text-gray-900">{b.name}</span><span className="block text-[11px] text-gray-600">{b.address}</span></span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-gray-700">{t.visibility}</p>
              <label className="mt-3 flex items-start gap-4 rounded-lg border border-gray-200 px-4 py-3">
                <input type="checkbox" name="is_featured" value="true" defaultChecked={product?.is_featured} className="mt-1 size-5 accent-blue-600" />
                <span><span className="block text-base text-gray-900">{t.featured}</span><span className="block text-sm text-gray-700">{t.featuredHint}</span></span>
              </label>
            </div>

            <label className="block"><span className={label}>{t.description}</span>
              <textarea name="description" rows={4} defaultValue={product?.description} placeholder={t.descriptionPlaceholder} className={`${field} mt-3 resize-none`} />
            </label>

            {state?.errors?.map((e) => <p key={e} role="alert" className="text-sm text-red-600">{e}</p>)}
          </div>

          <div className="flex items-center justify-end gap-6 border-t border-gray-200 px-8 py-6">
            <button type="button" onClick={close} className="text-sm uppercase tracking-[0.1em] text-gray-900">{t.discard}</button>
            <button type="submit" disabled={pending} className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-light to-brand px-8 py-3 text-base text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70">
              {pending ? t.saving : product ? t.update : t.save} <ArrowRight className="size-4 rtl:-scale-x-100" />
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
