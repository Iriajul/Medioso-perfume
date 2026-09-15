import type { Metadata } from "next";
import { Inter, Noto_Sans_Arabic, Noto_Sans_Hebrew } from "next/font/google";
import { RTL } from "@/i18n/dictionaries";
import { getLang } from "@/i18n/server";
import "./globals.css";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });
const arabic = Noto_Sans_Arabic({ variable: "--font-arabic", subsets: ["arabic"], preload: false });
const hebrew = Noto_Sans_Hebrew({ variable: "--font-hebrew", subsets: ["hebrew"], preload: false });

export const metadata: Metadata = {
  title: "Mad Perfume Admin",
  description: "Mad Perfume admin dashboard",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const lang = await getLang();
  return (
    <html
      lang={lang}
      dir={RTL.includes(lang) ? "rtl" : "ltr"}
      className={`${inter.variable} ${arabic.variable} ${hebrew.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
