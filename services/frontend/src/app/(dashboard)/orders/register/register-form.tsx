"use client";

import Image from "next/image";
import { startTransition, useActionState, useRef, useState, useTransition } from "react";
import { Award, Mail, PlusCircle, Search, Star, Store, Tag, Ticket } from "lucide-react";
import Avatar from "@/components/avatar";
import type { Dictionary } from "@/i18n/dictionaries";
import { lookupCustomer, registerPurchase, type Lookup, type RegisterState } from "../actions";

type Props = { t: Dictionary["register"]; tiers: Dictionary["common"]["tiers"]; pointsLabel: string; branches: { id: number; name: string }[]; rate: number };

const step = "flex size-10 items-center justify-center rounded-xl bg-brand-light text-base font-semibold text-white shadow-md";
const cardClass = "rounded-2xl bg-white px-8 py-8 shadow-[0_8px_30px_rgba(0,50,125,0.06)]";

export default function RegisterForm({ t, tiers, pointsLabel, branches, rate }: Props) {
  const form = useRef<HTMLFormElement>(null);
  const [email, setEmail] = useState("");
  const [customer, setCustomer] = useState<Lookup | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [amount, setAmount] = useState("");
  const [voucher, setVoucher] = useState("");
  const [searching, startSearch] = useTransition();
  const [state, action, pending] = useActionState(async (prev: RegisterState, formData: FormData) => {
    const result = await registerPurchase(prev, formData);
    if (result?.ok) reset(false);
    return result;
  }, undefined);

  // The voucher's value is only known once the server applies it; points follow the amount actually paid.
  const points = Math.floor((Number(amount) || 0) * rate);
  const num = (n: number) => n.toLocaleString();

  function reset(clearEmail = true) {
    form.current?.reset();
    setAmount("");
    setVoucher("");
    setCustomer(null);
    if (clearEmail) setEmail("");
  }

  const search = () => startSearch(async () => {
    const found = email.trim() ? await lookupCustomer(email.trim()) : null;
    setCustomer(found);
    setNotFound(!found);
  });

  return (
    <div className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_380px]">
      <div className="space-y-6">
        <section className={cardClass}>
          <h2 className="flex items-center gap-4 text-base text-gray-900"><span className={step}>1</span>{t.findCustomer}</h2>
          <div className="mt-6 flex flex-wrap gap-4">
            <label className="relative min-w-60 flex-1">
              <Mail className="absolute start-4 top-1/2 size-5 -translate-y-1/2 text-gray-600" />
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} onKeyDown={(e) => e.key === "Enter" && search()}
                placeholder={t.emailPlaceholder} className="w-full border border-gray-400 py-4 pe-4 ps-12 text-base text-gray-900 placeholder:text-gray-500 outline-none focus:border-brand-light" />
            </label>
            <button type="button" onClick={search} disabled={searching} className="flex items-center gap-2 rounded-xl bg-brand-light px-8 py-4 text-base font-semibold text-white shadow-md disabled:opacity-70">
              <Search className="size-5" />{searching ? t.searching : t.search}
            </button>
          </div>
          {notFound && !searching && <p role="alert" className="mt-4 text-sm text-red-600">{t.notFound}</p>}
        </section>

        <section className={cardClass}>
          <div className="flex items-center justify-between gap-4">
            <h2 className="flex items-center gap-4 text-base text-gray-900"><span className={step}>2</span>{t.confirmIdentity}</h2>
            {customer && <span className="rounded-full bg-[#e3e8f7] px-4 py-1 text-xs font-semibold uppercase tracking-wider text-brand-light">{customer.is_active ? t.activeMember : t.inactiveMember}</span>}
          </div>
          {customer ? (
            <div className="mt-6 flex flex-wrap items-center gap-6 rounded-2xl border border-gray-100 px-6 py-6 shadow-sm">
              {customer.avatar_url
                ? <Image src={customer.avatar_url} alt="" width={72} height={88} className="h-22 w-18 rounded-lg object-cover shadow-lg" />
                : <Avatar name={customer.full_name} className="size-18 rounded-lg text-xl shadow-lg" />}
              <div className="min-w-0">
                <p className="text-base text-gray-900">{customer.full_name}</p>
                <p className="truncate text-base text-gray-600">{customer.email}</p>
                <div className="mt-3 flex flex-wrap gap-3">
                  <span className="flex items-center gap-2 rounded-lg px-4 py-2 font-semibold text-gray-900 shadow-sm"><Star className="size-4 fill-brand-light text-white" />{num(customer.points_balance)} <span className="text-sm font-normal text-gray-600">{pointsLabel}</span></span>
                  <span className="flex items-center gap-2 rounded-lg px-4 py-2 font-semibold text-gray-900 shadow-sm"><Award className="size-4 text-brand-light" />{t.tier.replace("{tier}", tiers[customer.tier as keyof typeof tiers])}</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="mt-6 text-gray-500">{t.searchFirst}</p>
          )}
        </section>
      </div>

      <form
        ref={form}
        onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); startTransition(() => action(data)); }}
        className="rounded-2xl bg-gray-50/80 px-8 py-8 shadow-[0_8px_30px_rgba(0,50,125,0.06)]"
      >
        <h2 className="flex items-center gap-4 text-base text-gray-900"><span className={step}>3</span>{t.transactionDetails}</h2>
        <input type="hidden" name="customer" value={customer?.id ?? ""} />

        <label className="mt-6 block text-xs font-semibold uppercase tracking-[0.12em] text-gray-700">{t.selectBranch}
          <span className="relative mt-3 block">
            <Store className="absolute start-4 top-1/2 size-5 -translate-y-1/2 text-gray-700" />
            <select name="branch" required defaultValue="" className="w-full appearance-none rounded-xl bg-white py-4 pe-4 ps-12 text-base normal-case tracking-normal text-gray-900 shadow-sm outline-none">
              <option value="" disabled>{t.branchPlaceholder}</option>
              {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
          </span>
        </label>

        <label className="mt-6 block text-xs font-semibold uppercase tracking-[0.12em] text-gray-700">{t.purchaseAmount}
          <span className="mt-3 flex items-center gap-2 rounded-xl bg-white px-6 py-6 shadow-sm" dir="ltr">
            <span className="text-4xl font-bold text-blue-300">$</span>
            <input name="amount" type="number" required min="0.01" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00"
              className="w-full bg-transparent text-5xl font-bold tracking-normal text-brand placeholder:text-brand outline-none" />
          </span>
        </label>
        <p className="mt-3 text-sm italic text-gray-700">{t.exchange.replace("{rate}", String(rate))}</p>

        <label className="mt-6 block text-xs font-semibold uppercase tracking-[0.12em] text-gray-700">{t.voucher}
          <span className="relative mt-3 block">
            <Ticket className="absolute start-4 top-1/2 size-5 -translate-y-1/2 text-gray-600" />
            <input name="voucher_code" value={voucher} onChange={(e) => setVoucher(e.target.value.toUpperCase())} placeholder={t.voucherPlaceholder}
              className="w-full rounded-xl bg-white py-4 pe-4 ps-12 text-base normal-case tracking-normal text-gray-900 placeholder:text-gray-500 shadow-sm outline-none" dir="ltr" />
          </span>
          <span className="mt-2 block text-sm font-normal normal-case tracking-normal text-gray-600">{t.voucherHint}</span>
        </label>

        <div className="mt-8 flex items-center justify-between rounded-xl border border-blue-200 bg-[#e3e8f7] px-6 py-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-brand-light">{t.pointsToEarn}</p>
            <p className="mt-1 text-2xl font-bold text-brand" dir="ltr">+ {num(points)} {pointsLabel}</p>
          </div>
          <span className="flex size-14 items-center justify-center rounded-xl bg-brand-light text-white shadow-md"><PlusCircle className="size-7" /></span>
        </div>

        <label className="mt-8 block text-xs font-semibold uppercase tracking-[0.12em] text-gray-700">{t.notes}
          <textarea name="notes" rows={4} placeholder={t.notesPlaceholder} className="mt-3 w-full resize-none rounded-xl bg-white px-6 py-5 text-base normal-case tracking-normal text-gray-900 shadow-sm outline-none" />
        </label>

        {state?.errors?.map((e) => <p key={e} role="alert" className="mt-4 text-sm text-red-600">{e}</p>)}
        {state?.ok && !customer && (
          <p role="status" className="mt-4 rounded-xl bg-green-50 px-4 py-3 text-sm text-green-700">
            {t.success.replace("{order}", `#${state.ok.order}`).replace("{points}", num(state.ok.points)).replace("{balance}", num(state.ok.balance))}
            {Number(state.ok.discount) > 0 && " " + t.voucherApplied.replace("{discount}", `$${state.ok.discount}`).replace("{due}", `$${state.ok.amount_due}`)}
          </p>
        )}

        <div className="mt-8 border-t border-gray-200 pt-8">
          <button type="submit" disabled={pending || !customer?.is_active}
            className="flex w-full items-center gap-4 rounded-xl bg-gradient-to-b from-brand-light to-brand px-6 py-6 text-lg font-semibold text-white shadow-lg disabled:opacity-50">
            <Tag className="size-5 shrink-0" /><span className="flex-1 text-center">{pending ? t.submitting : t.submit}</span>
          </button>
          <button type="button" onClick={() => reset()} className="mt-5 w-full text-center text-base text-gray-700">{t.cancel}</button>
        </div>
      </form>
    </div>
  );
}
