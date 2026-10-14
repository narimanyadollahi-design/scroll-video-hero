import type { Metadata } from "next";
import "./globals.css";
import content from "@/content.json";
import theme from "@/theme.json";
import { LangProvider } from "@/lib/lang";

const RTL = new Set(["fa", "ar", "he", "ur"]);

export const metadata: Metadata = {
  title: `${content.brand.name} — ${content.brand.descriptor[content.default_lang as "en"] ?? ""}`,
  description: (content.brand.tagline as Record<string, string>)[content.default_lang] ?? "",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const lang = content.default_lang;
  return (
    <html lang={lang} dir={RTL.has(lang) ? "rtl" : "ltr"}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {theme.fonts_url ? <link rel="stylesheet" href={theme.fonts_url} /> : null}
        <link rel="preload" as="image" href="/hero-poster.jpg" />
      </head>
      <body
        style={
          {
            "--font-display": `'${theme.display_font}'`,
            "--font-body": `'${theme.body_font}'`,
            "--font-fa": `'${theme.fa_font}'`,
            "--bg": theme.bg,
            "--surface": theme.surface,
            "--accent": theme.accent,
            "--accent-deep": theme.accent_deep,
            "--highlight": theme.highlight,
            "--ink": theme.text,
          } as React.CSSProperties
        }
        className="bg-bg font-body text-ink antialiased"
      >
        <LangProvider>{children}</LangProvider>
      </body>
    </html>
  );
}
