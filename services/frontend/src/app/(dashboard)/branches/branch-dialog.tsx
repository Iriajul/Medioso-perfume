"use client";

import Image from "next/image";
import { startTransition, useActionState, useRef, useState } from "react";
import { ArrowRight, CloudUpload, Pencil, Phone, Plus, X } from "lucide-react";
import type { Dictionary } from "@/i18n/dictionaries";
import type { SaveState } from "@/lib/session";
import { saveBranch } from "./actions";
import type { Branch } from "./page";

const field = "w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-400 outline-none focus:border-brand-light";
const label = "text-xs font-medium uppercase tracking-wide text-gray-700";

export default function BranchDialog({ t, branch }: { t: Dictionary["branches"]; branch?: Branch }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const form = useRef<HTMLFormElement>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const close = () => {
    dialog.current?.close();
    form.current?.reset();
    setPreview(null);
  };

  const [state, action, pending] = useActionState(async (prev: SaveState, formData: FormData) => {
    const result = await saveBranch(branch?.id ?? null, prev, formData);
    if (result?.ok) close();
    return result;
  }, undefined);

  const time = (name: keyof Branch, fallback: string) => (
    <input type="time" name={name} required defaultValue={(branch?.[name] as string | undefined)?.slice(0, 5) ?? fallback} className={field} />
  );

  return (
    <>
      {branch ? (
        <button type="button" onClick={() => dialog.current?.showModal()} aria-label={t.edit} className="text-gray-600 hover:text-brand">
          <Pencil className="size-4" />
        </button>
      ) : (
        <button
          type="button"
          onClick={() => dialog.current?.showModal()}
          className="flex items-center gap-8 rounded-2xl bg-brand-light px-8 py-4 text-base font-semibold uppercase tracking-[0.1em] text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)]"
        >
          <Plus className="size-5" /> <span className="max-w-32 text-center leading-6">{t.add}</span>
        </button>
      )}

      <dialog
        ref={dialog}
        onClose={close}
        className="m-auto max-h-[92vh] w-full max-w-[672px] rounded-3xl bg-[#f1f1f1] p-0 text-start shadow-2xl backdrop:bg-gray-900/30 backdrop:backdrop-blur-sm"
      >
        <div className="flex items-start gap-4 border-b border-gray-200 bg-[#f5f5f5] px-8 py-7">
          <div className="flex-1">
            <h2 className="text-2xl font-semibold text-gray-900">{branch ? t.editTitle : t.newTitle}</h2>
            <p className="mt-1 text-base text-gray-600">{t.modalSubtitle}</p>
          </div>
          <button type="button" onClick={close} aria-label="Close" className="text-gray-700"><X className="size-6" /></button>
        </div>

        <form
          ref={form}
          // onSubmit (not action=) so a failed save keeps what the admin typed.
          onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); startTransition(() => action(data)); }}
          className="space-y-7 px-8 py-8">
          <div>
            <p className={label}>{t.imageLabel}</p>
            <label className="relative mt-3 flex h-64 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed border-[#d9c7b0] text-center">
              {(preview ?? branch?.image_url) && (
                <Image src={preview ?? branch!.image_url} alt="" fill unoptimized={!!preview} className="object-cover opacity-40" sizes="610px" />
              )}
              <span className="relative flex size-16 items-center justify-center rounded-full bg-[#dfe6f3] text-brand-light"><CloudUpload className="size-7" /></span>
              <span className="relative mt-5 text-base font-medium text-gray-900">{t.upload}</span>
              <span className="relative mt-1 text-sm text-gray-600">{t.uploadHint}</span>
              <span className="relative mt-5 rounded-xl border border-gray-500 bg-white px-6 py-2 text-sm text-gray-900">{t.selectFiles}</span>
              <input
                type="file" name="image" accept="image/png,image/jpeg,image/webp" className="sr-only"
                onChange={(e) => { const f = e.target.files?.[0]; setPreview(f ? URL.createObjectURL(f) : null); }}
              />
            </label>
          </div>

          <label className="block">
            <span className={label}>{t.name}</span>
            <input name="name" required maxLength={100} defaultValue={branch?.name} placeholder={t.namePlaceholder} className={`${field} mt-3`} />
          </label>

          <label className="block">
            <span className={label}>{t.fullAddress}</span>
            <textarea name="address" required rows={3} defaultValue={branch?.address} placeholder={t.addressPlaceholder} className={`${field} mt-3 resize-none`} />
          </label>

          <div>
            <p className={label}>{t.hours}</p>
            <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-2 text-xs text-gray-700">{t.weekdays}</p>
                <div className="grid grid-cols-2 gap-2">{time("weekday_opens", "10:00")}{time("weekday_closes", "21:00")}</div>
              </div>
              <div>
                <p className="mb-2 text-xs text-gray-700">{t.sunday}</p>
                <div className="grid grid-cols-2 gap-2">{time("sunday_opens", "11:00")}{time("sunday_closes", "19:00")}</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block">
              <span className={label}>{t.phone}</span>
              <span className="relative mt-3 block">
                <input name="phone" type="tel" required maxLength={30} defaultValue={branch?.phone} placeholder="+33 1 23 45 67 89" className={`${field} pe-10`} dir="ltr" />
                <Phone className="absolute end-3 top-1/2 size-4 -translate-y-1/2 text-gray-500" />
              </span>
            </label>
            <div>
              <span className={label}>{t.location}</span>
              <div className="mt-3 grid grid-cols-2 gap-2">
                <input name="latitude" type="number" step="0.000001" min={-90} max={90} defaultValue={branch?.latitude ?? ""} placeholder={t.latitude} className={field} dir="ltr" />
                <input name="longitude" type="number" step="0.000001" min={-180} max={180} defaultValue={branch?.longitude ?? ""} placeholder={t.longitude} className={field} dir="ltr" />
              </div>
            </div>
          </div>

          {state?.errors?.map((e) => <p key={e} role="alert" className="text-sm text-red-600">{e}</p>)}

          <div className="flex justify-end">
            <button type="submit" disabled={pending} className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-light to-brand px-8 py-3 text-base text-white shadow-[0_8px_20px_rgba(0,68,165,0.3)] disabled:opacity-70">
              {pending ? t.saving : branch ? t.update : t.save} <ArrowRight className="size-4 rtl:-scale-x-100" />
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
