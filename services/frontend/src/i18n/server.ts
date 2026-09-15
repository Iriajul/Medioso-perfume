import { cookies } from "next/headers";
import { dictionaries, LANGS, type Lang } from "./dictionaries";

export async function getLang(): Promise<Lang> {
  const value = (await cookies()).get("lang")?.value;
  return LANGS.includes(value as Lang) ? (value as Lang) : "en";
}

export async function getDictionary() {
  return dictionaries[await getLang()];
}
