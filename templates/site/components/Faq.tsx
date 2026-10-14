"use client";

import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { FaqItem, L10n } from "@/lib/types";

export default function Faq() {
  const { t } = useLang();
  const f = (content as unknown as { faq: { title: L10n; items: FaqItem[] } }).faq;
  return (
    <section className="bg-bg px-6 py-24 md:px-10 md:py-32">
      <div className="mx-auto max-w-3xl">
        <h2 className="font-display text-4xl font-light text-ink md:text-5xl">{t(f.title)}</h2>
        <div className="mt-12 divide-y divide-white/10 border-y border-white/10">
          {f.items.map((it, i) => (
            <details key={i} className="group py-6">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-6 text-lg text-ink">
                {t(it.q)}
                <span aria-hidden className="text-highlight transition-transform duration-500 group-open:rotate-45">+</span>
              </summary>
              <p className="mt-4 max-w-2xl leading-8 text-ink/65">{t(it.a)}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
