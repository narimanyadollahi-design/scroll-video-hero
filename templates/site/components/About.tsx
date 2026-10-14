"use client";

import { motion } from "framer-motion";
import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { AboutContent } from "@/lib/types";

export default function About() {
  const { t } = useLang();
  const a = content.about as unknown as AboutContent;
  const stats = a.stats ?? [];
  return (
    <section id="about" className="bg-bg px-6 py-28 md:px-10 md:py-36">
      <div className="mx-auto grid max-w-7xl gap-16 md:grid-cols-2">
        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="font-display text-4xl font-light leading-tight text-ink md:text-6xl"
        >
          {t(a.title)}
        </motion.h2>
        <div>
          <p className="text-base leading-8 text-ink/70 md:text-lg">{t(a.body)}</p>
          {stats.length > 0 && (
            <dl className="mt-12 grid grid-cols-3 gap-6 border-t border-white/10 pt-8">
              {stats.map((s, i) => (
                <div key={i}>
                  <dt className="font-display text-4xl text-highlight">{s.value}</dt>
                  <dd className="smallcaps mt-2 text-[10px] text-ink/50">{t(s.label)}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      </div>
    </section>
  );
}
