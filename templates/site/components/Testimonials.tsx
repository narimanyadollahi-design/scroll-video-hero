"use client";

import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { L10n, Testimonial } from "@/lib/types";

export default function Testimonials() {
  const { t } = useLang();
  const c = content as unknown as { concept: boolean; testimonials: { title: L10n; items: Testimonial[] } };
  return (
    <section className="bg-bg px-6 py-28 md:px-10 md:py-36">
      <div className="mx-auto max-w-6xl">
        <h2 className="font-display text-4xl font-light text-ink md:text-5xl">{t(c.testimonials.title)}</h2>
        {c.concept && (
          <p className="smallcaps mt-3 text-[10px] text-ink/40">Illustrative · not real customers</p>
        )}
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {c.testimonials.items.map((it, i) => (
            <figure key={i} className="rounded-sm border border-white/10 bg-surface/60 p-8">
              <blockquote className="font-display text-xl leading-relaxed text-ink">“{t(it.quote)}”</blockquote>
              <figcaption className="mt-6 text-sm text-ink/60">
                <span className="text-ink">{it.name}</span>
                {it.role && <span> · {t(it.role)}</span>}
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
