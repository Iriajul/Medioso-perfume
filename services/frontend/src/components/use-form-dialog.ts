"use client";

import { startTransition, useActionState, useRef, type FormEvent } from "react";
import type { SaveState } from "@/lib/session";

const UPLOAD_FAILED = "Unable to save. If you attached an image, make sure it is 10MB or smaller.";

/**
 * Shared behaviour for the add/edit modals: a native <dialog>, a form that
 * keeps its input when a save fails, and closing + resetting on success.
 */
export function useFormDialog(save: (prev: SaveState, formData: FormData) => Promise<SaveState>, onReset?: () => void) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  const close = () => {
    dialogRef.current?.close();
    formRef.current?.reset();
    onReset?.();
  };

  const [state, action, pending] = useActionState(async (prev: SaveState, formData: FormData): Promise<SaveState> => {
    // A request rejected before reaching the server action (e.g. 413 body too large) throws here.
    const result: SaveState = await save(prev, formData).catch(() => ({ errors: [UPLOAD_FAILED] }));
    if (result?.ok) close();
    return result;
  }, undefined);

  // onSubmit (not <form action>) so React doesn't reset the form on a failed save.
  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    startTransition(() => action(data));
  };

  return { dialogRef, formRef, open: () => dialogRef.current?.showModal(), close, state, pending, onSubmit };
}
