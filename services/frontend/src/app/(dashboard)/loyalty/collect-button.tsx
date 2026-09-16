"use client";

import { useState, useTransition } from "react";
import { collectRedemption } from "./actions";

export default function CollectButton({ id, label, saving, errorText }: {
  id: number; label: string; saving: string; errorText: string;
}) {
  const [pending, start] = useTransition();
  const [failed, setFailed] = useState(false);

  return (
    <>
      <button
        type="button"
        disabled={pending}
        onClick={() => start(async () => setFailed(!(await collectRedemption(id))))}
        className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-light disabled:opacity-60"
      >
        {pending ? saving : label}
      </button>
      {failed && <span role="alert" className="mt-1 block text-sm text-red-600">{errorText}</span>}
    </>
  );
}
