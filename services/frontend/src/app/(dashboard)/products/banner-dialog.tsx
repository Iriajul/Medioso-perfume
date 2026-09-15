"use client";

import Image from "next/image";
import { useState } from "react";
import { CloudUpload, Eye, GalleryHorizontal, ImagePlus, Pencil, X } from "lucide-react";
import { useFormDialog } from "@/components/use-form-dialog";
import type { Dictionary } from "@/i18n/dictionaries";
import type { SaveState } from "@/lib/session";
import { saveBanner } from "./actions";
import type { Banner } from "./page";

const field = "w-full rounded-xl border border-gray-100 bg-white px-5 py-3 text-base text-gray-900 placeholder:text-gray-400 shadow-[0_2px_6px_rgba(0,0,0,0.04)] outline-none focus:border-brand-light";

export default function BannerDialog({ t, banner }: { t: Dictionary["products"]; banner?: Banner }) {
  const [preview, setPreview] = useState<string | null>(null);
  const { dialogRef, formRef, open, close, state, pending, onSubmit } = useFormDialog(
    (prev: SaveState, formData: FormData) => saveBanner(banner?.id ?? null, prev, formData),
    () => setPreview(null),
  );
  const src = preview ?? banner?.image_url;

  return (
    <>
      {banner ? (
        <button type="button" onClick={open} aria-label={t.edit} className="text-brand hover:text-brand-light"><Pencil className="size-5" /></button>
      ) : (
        <button type="button" onClick={open} className="flex items-center gap-3 rounded-2xl bg-brand px-8 py-4 text-sm font-semibold uppercase tracking-[0.1em] text-white shadow-[0_10px_30px_rgba(0,50,125,0.35)]">
          <ImagePlus className="size-4" /> {t.addBanner}
        </button>
      )}

      <dialog ref={dialogRef} onClose={close} className="m-auto w-full max-w-[672px] rounded-[36px] bg-white p-0 text-start shadow-2xl backdrop:bg-gray-900/30 backdrop:backdrop-blur-sm">
        <form ref={formRef} onSubmit={onSubmit} className="px-8 py-9">
          <div className="flex items-start">
            <div className="flex-1">
              <h2 className="flex items-center gap-3 text-base text-gray-900"><GalleryHorizontal className="size-5" />{banner ? t.editBanner : t.newBanner}</h2>
              <p className="mt-1 text-sm text-gray-700">{t.bannerSubtitle}</p>
            </div>
            <button type="button" onClick={close} aria-label="Close" className="text-gray-800"><X className="size-5" /></button>
          </div>

          <p className="mt-8 text-base text-gray-900">{t.bannerAsset}</p>
          <label className="relative mt-3 flex h-48 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-gray-400 text-center">
            {src && <Image src={src} alt="" fill unoptimized={!!preview} className="object-cover opacity-40" sizes="610px" />}
            <span className="relative flex size-12 items-center justify-center rounded-xl bg-gray-100/90"><CloudUpload className="size-6" /></span>
            <span className="relative mt-3 text-base text-gray-900">{t.bannerUpload}</span>
            <span className="relative text-xs text-gray-700">{t.bannerHint}</span>
            <input type="file" name="image" accept="image/png,image/jpeg,image/webp" required={!banner} className="sr-only"
              onChange={(e) => { const f = e.target.files?.[0]; setPreview(f ? URL.createObjectURL(f) : null); }} />
          </label>

          <label className="mt-8 block text-base text-gray-900">{t.campaignTitle}
            <input name="title" required maxLength={150} defaultValue={banner?.title} placeholder={t.campaignPlaceholder} className={`${field} mt-3`} />
          </label>

          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <label className="block text-base text-gray-900">{t.startDate}
              <input name="starts_on" type="date" required defaultValue={banner?.starts_on} className={`${field} mt-3`} />
            </label>
            <label className="block text-base text-gray-900">{t.endDate}
              <input name="ends_on" type="date" required defaultValue={banner?.ends_on} className={`${field} mt-3`} />
            </label>
          </div>

          <label className="mt-8 flex cursor-pointer items-center gap-4 px-4">
            <Eye className="size-5 text-gray-800" />
            <span className="flex-1"><span className="block text-base text-gray-900">{t.bannerLive}</span><span className="block text-xs text-gray-700">{t.bannerLiveHint}</span></span>
            <input type="checkbox" name="is_active" defaultChecked={banner?.is_active ?? true} className="peer sr-only" />
            <span className="relative h-8 w-14 rounded-full bg-gray-300 transition peer-checked:bg-brand-light after:absolute after:start-1 after:top-1 after:size-6 after:rounded-full after:bg-white after:transition peer-checked:after:translate-x-6 rtl:peer-checked:after:-translate-x-6" />
          </label>

          {state?.errors?.map((e) => <p key={e} role="alert" className="mt-4 text-sm text-red-600">{e}</p>)}

          <div className="mt-10 flex items-center justify-between gap-6">
            <button type="button" onClick={close} className="w-52 rounded-xl border border-gray-300 py-3 text-base text-gray-900">{t.cancel}</button>
            <button type="submit" disabled={pending} className="w-64 rounded-xl bg-gradient-to-b from-brand-light to-brand py-3 text-base text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70">
              {pending ? t.saving : banner ? t.update : t.createPromotion}
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
