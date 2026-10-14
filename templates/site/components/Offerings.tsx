"use client";

import { motion } from "framer-motion";
import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { OfferingsContent } from "@/lib/types";

export default function Offerings() {
  const { t } = useLang();
  const o = content.offerings as unknown as OfferingsContent;
  return (
    <section id="collection" className="relative bg-bg px-6 py-28 md:px-10 md:py-40">
      <div className="mx-auto max-w-7xl">
        <p className="smallcaps text-xs text-accent">{t(o.eyebrow)}</p>
        <h2 className="mt-4 max-w-3xl font-display text-4xl font-light text-ink md:text-6xl">{t(o.title)}</h2>
        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {o.items.map((item, i) => (
            <motion.article
              key={i}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.9, ease: "easeOut", delay: i * 0.12 }}
              whileHover={{ scale: 1.02 }}
              className="group relative overflow-hidden rounded-sm border border-white/10 bg-surface p-8 transition-shadow duration-700 hover:border-highlight/60 hover:shadow-[0_0_40px_-10px_var(--highlight)]"
            >
              <div
                className="absolute -right-10 -top-10 h-40 w-40 rounded-full opacity-40 blur-3xl transition-opacity duration-700 group-hover:opacity-70"
                style={{ background: "radial-gradient(circle, var(--accent), transparent 70%)" }}
              />
              <span className="font-display text-5xl font-light text-highlight/70">{String(i + 1).padStart(2, "0")}</span>
              <h3 className="mt-10 font-display text-2xl text-ink md:text-3xl">{t(item.name)}</h3>
              <p className="mt-4 text-sm leading-7 text-ink/65">{t(item.blurb)}</p>
              {item.tag && (
                <span className="smallcaps mt-8 inline-block rounded-full border border-highlight/30 bg-white/5 px-3 py-1 text-[10px] text-highlight backdrop-blur">
                  {t(item.tag)}
                </span>
              )}
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}
