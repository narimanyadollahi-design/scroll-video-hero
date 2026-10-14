"use client";

import content from "@/content.json";
import { useLang } from "@/lib/lang";

type Credit = { by: string; url?: string; pitch?: Record<string, string> };

export default function Footer() {
  const { t } = useLang();
  const year = new Date().getFullYear();
  const credit = (content as unknown as { credit?: Credit }).credit;
  return (
    <footer className="border-t border-white/10 bg-bg px-6 py-16 md:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-10 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="font-display text-3xl tracking-[0.3em] text-ink">{content.brand.name}</p>
          <p className="mt-2 text-sm text-ink/50">{t(content.brand.descriptor)}</p>
          <div className="mt-6 h-px w-24 bg-gradient-to-r from-highlight to-transparent" />
        </div>
        <div className="flex flex-col gap-4 md:items-end">
          {credit?.url && credit.pitch && (
            <a
              href={credit.url}
              target="_blank"
              rel="noopener noreferrer"
              className="smallcaps border-b border-highlight/50 pb-1 text-xs text-highlight transition hover:border-highlight"
            >
              {t(credit.pitch)} →
            </a>
          )}
          <p className="text-xs text-ink/40">
            © {year} {content.brand.name}
            {credit?.by ? ` · Crafted by ${credit.by}` : ""}
          </p>
        </div>
      </div>
    </footer>
  );
}
