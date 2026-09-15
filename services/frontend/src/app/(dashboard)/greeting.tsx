"use client";

import { useSyncExternalStore } from "react";
import type { Dictionary } from "@/i18n/dictionaries";

const noop = () => () => {};

// Uses the admin's local clock: empty on the server, filled in after hydration.
export default function Greeting({ t }: { t: Dictionary["greeting"] }) {
  const hour = useSyncExternalStore(noop, () => new Date().getHours(), () => null);
  if (hour === null) return null;
  return <>{hour < 12 ? t.morning : hour < 18 ? t.afternoon : t.evening}</>;
}
