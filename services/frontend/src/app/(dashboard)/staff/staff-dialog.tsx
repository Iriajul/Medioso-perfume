"use client";

import Image from "next/image";
import { useState } from "react";
import { CircleCheck, ImagePlus, Pencil, Plus, X } from "lucide-react";
import { useFormDialog } from "@/components/use-form-dialog";
import type { Dictionary } from "@/i18n/dictionaries";
import type { SaveState } from "@/lib/session";
import { saveStaff } from "./actions";
import type { StaffMember } from "./page";

const field = "w-full rounded-full bg-[#f1f3fd] px-5 py-3.5 text-base text-gray-900 placeholder:text-gray-400 outline-none focus:ring-2 focus:ring-brand-light/30";
const label = "text-sm font-semibold uppercase tracking-[0.1em] text-gray-700";

export default function StaffDialog({ t, branches, member }: { t: Dictionary["staff"]; branches: { id: number; name: string }[]; member?: StaffMember }) {
  const [preview, setPreview] = useState<string | null>(null);
  const { dialogRef, formRef, open, close, state, pending, onSubmit } = useFormDialog(
    (prev: SaveState, formData: FormData) => saveStaff(member?.id ?? null, prev, formData),
    () => setPreview(null),
  );
  const src = preview ?? member?.avatar_url;

  return (
    <>
      {member ? (
        <button type="button" onClick={open} aria-label={t.edit} className="text-brand hover:text-brand-light"><Pencil className="size-5" /></button>
      ) : (
        <button type="button" onClick={open} className="flex items-center gap-2 rounded-full bg-brand-light px-7 py-3.5 text-base font-semibold uppercase text-white shadow-[0_10px_30px_rgba(0,68,165,0.35)]">
          <Plus className="size-5" /> {t.add}
        </button>
      )}

      <dialog ref={dialogRef} onClose={close} className="m-auto w-full max-w-[576px] rounded-[40px] bg-white p-0 text-start shadow-2xl backdrop:bg-gray-900/40 backdrop:backdrop-blur-sm">
        <div className="flex items-start border-b border-gray-100 px-8 py-8">
          <div className="flex-1">
            <h2 className="text-base font-semibold text-brand-light">{member ? t.editTitle : t.newTitle}</h2>
            <p className="mt-1 text-base text-gray-700">{member ? t.editSubtitle : t.modalSubtitle}</p>
          </div>
          <button type="button" onClick={close} aria-label="Close" className="text-gray-700"><X className="size-5" /></button>
        </div>

        <form ref={formRef} onSubmit={onSubmit}>
          <div className="space-y-6 px-10 py-8">
            <div className="flex items-center gap-8">
              <label className="relative flex size-24 shrink-0 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-3xl border-2 border-dashed border-blue-300 bg-[#f7f8fe] text-brand-light">
                {src ? <Image src={src} alt="" fill unoptimized={!!preview} className="object-cover" sizes="96px" /> : <><ImagePlus className="size-5" /><span className="mt-1 text-[10px] font-bold uppercase">{t.upload}</span></>}
                <input type="file" name="photo" accept="image/png,image/jpeg,image/webp" className="sr-only"
                  onChange={(e) => { const f = e.target.files?.[0]; setPreview(f ? URL.createObjectURL(f) : null); }} />
              </label>
              <div>
                <p className="text-base font-semibold uppercase tracking-[0.12em] text-gray-700">{t.photo}</p>
                <p className="mt-2 text-sm leading-6 text-gray-500">{t.photoHint}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <label className="block"><span className={label}>{t.fullName}</span>
                <input name="full_name" required maxLength={255} defaultValue={member?.full_name} placeholder={t.namePlaceholder} className={`${field} mt-3`} />
              </label>
              <label className="block"><span className={label}>{t.email}</span>
                <input name="email" type="email" required defaultValue={member?.email} placeholder={t.emailPlaceholder} className={`${field} mt-3`} />
              </label>
              <label className="block"><span className={label}>{t.branch}</span>
                <select name="branch" required defaultValue={member?.branch ?? ""} className={`${field} mt-3`}>
                  <option value="" disabled>{t.selectBranch}</option>
                  {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </label>
              <label className="block"><span className={label}>{t.role}</span>
                <select name="job_title" required defaultValue={member?.job_title ?? ""} className={`${field} mt-3`}>
                  <option value="" disabled>{t.selectRole}</option>
                  {Object.entries(t.roles).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </label>
            </div>

            <div>
              <p className={label}>{t.status}</p>
              <label className="mt-3 flex cursor-pointer items-center gap-3 rounded-full border border-blue-200 bg-[#f1f3fd] px-5 py-4 text-base font-semibold text-gray-900 has-[:checked]:border-brand-light">
                <CircleCheck className="size-5 text-brand-light" />
                <span className="flex-1">{t.activeStatus}</span>
                <input type="checkbox" name="is_active" defaultChecked={member?.is_active ?? true} className="size-5 accent-blue-700" />
              </label>
            </div>

            {!member && <p className="text-sm text-gray-500">{t.inviteNote}</p>}
            {state?.errors?.map((e) => <p key={e} role="alert" className="text-sm text-red-600">{e}</p>)}
          </div>

          <div className="flex items-center justify-end gap-6 rounded-b-[40px] bg-[#f3f5fa] px-8 py-8">
            <button type="button" onClick={close} className="text-base font-semibold uppercase tracking-[0.1em] text-gray-700">{t.cancel}</button>
            <button type="submit" disabled={pending} className="rounded-full bg-brand-light px-10 py-4 text-base font-semibold uppercase tracking-[0.1em] text-white shadow-[0_10px_30px_rgba(0,68,165,0.35)] disabled:opacity-70">
              {pending ? t.saving : member ? t.update : t.save}
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}
