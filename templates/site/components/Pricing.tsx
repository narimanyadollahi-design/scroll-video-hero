"use client";

import { motion } from "framer-motion";
import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { L10n, PricingTier } from "@/lib/types";

export default function Pricing() {
  const { t } = useLang();
  const p = (content as unknown as { pricing: { eyebrow: L10n; title: L10n; tiers: PricingTier[] } }).pricing;
  return (
    <section id="pricing" className="bg-bg px-6 py-28 md:px-10 md:py-36">
      <div className="mx-auto max-w-6xl">
        <p className="smallcaps text-xs text-accent">{t(p.eyebrow)}</p>
        <h2 className="mt-4 max-w-3xl font-display text-4xl font-light text-ink md:text-6xl">{t(p.title)}</h2>
        <div className={`mt-16 grid gap-6 ${p.tiers.length === 2 ? "md:grid-cols-2" : p.tiers.length === 4 ? "md:grid-cols-4" : "md:grid-cols-3"}`}>
          {p.tiers.map((tier, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: "easeOut", delay: i * 0.1 }}
              className={`flex flex-col rounded-sm border p-8 ${tier.highlight ? "border-highlight bg-surface" : "border-white/10 bg-surface/60"}`}
            >
              <h3 className="font-display text-2xl text-ink">{t(tier.name)}</h3>
              <p className="mt-6 font-display text-4xl text-highlight">{t(tier.price)}</p>
              {tier.note && <p className="mt-1 text-xs text-ink/50">{t(tier.note)}</p>}
              <ul className="mt-8 flex-1 space-y-3 text-sm text-ink/70">
                {tier.features.map((f, j) => (
                  <li key={j} className="flex gap-3"><span aria-hidden className="text-highlight">✓</span><span>{t(f)}</span></li>
                ))}
              </ul>
              <a
                href={tier.href}
                className={`smallcaps mt-10 block border px-6 py-3 text-center text-xs transition duration-500 ${
                  tier.highlight ? "border-highlight bg-highlight text-black hover:bg-transparent hover:text-highlight" : "border-white/20 text-ink hover:border-highlight hover:text-highlight"
                }`}
              >
                {t(tier.cta)}
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
