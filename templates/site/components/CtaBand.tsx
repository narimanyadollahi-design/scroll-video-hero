"use client";

import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { Channel } from "@/lib/types";

export default function CtaBand() {
  const { t } = useLang();
  const c = content.cta;
  const channels = ((c as unknown as { channels?: Channel[] }).channels ?? []);
  return (
    <section id="contact" className="relative overflow-hidden bg-bg px-6 py-32 text-center md:py-44">
      <div
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{ background: "radial-gradient(ellipse at 50% 100%, var(--accent-deep), transparent 65%)" }}
      />
      <div className="relative mx-auto max-w-3xl">
        <h2 className="font-display text-4xl font-light text-ink md:text-6xl">{t(c.title)}</h2>
        <p className="mx-auto mt-6 max-w-xl text-base leading-8 text-ink/70">{t(c.body)}</p>
        <a
          href={c.href}
          className="smallcaps mt-12 inline-block border border-highlight px-10 py-4 text-xs text-highlight transition duration-700 ease-out hover:bg-highlight hover:text-black"
        >
          {t(c.button)}
        </a>
        {channels.length > 0 && (
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
            {channels.map((ch, i) => (
              <a key={i} href={ch.href} target="_blank" rel="noopener noreferrer" className="text-sm text-ink/60 underline-offset-8 transition hover:text-highlight hover:underline">
                {t(ch.label)}
              </a>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
