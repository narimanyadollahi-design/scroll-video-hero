"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import content from "@/content.json";
import { useLang } from "@/lib/lang";
import type { HeroWord } from "@/lib/types";

gsap.registerPlugin(ScrollTrigger);

const words = (content.hero as unknown as { words: HeroWord[] }).words;

/** Kinetic-type hero: giant words take the stage one after another as the page scrolls.
 *  No generated media needed, so it is the fast path when there is no time or budget for video. */
export default function HeroType() {
  const { t } = useLang();
  const sectionRef = useRef<HTMLElement>(null);
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);
  const bgRef = useRef<HTMLDivElement>(null);
  const barRef = useRef<HTMLDivElement>(null);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  useEffect(() => {
    if (reduced) return;
    const section = sectionRef.current;
    if (!section) return;
    let target = 0, current = 0, raf = 0;
    const n = words.length;

    const paint = (p: number) => {
      const pos = p * (n - 1);
      words.forEach((_, i) => {
        const el = itemRefs.current[i];
        if (!el) return;
        const d = pos - i; // signed distance in "word units"
        const a = Math.abs(d);
        const op = Math.max(0, 1 - a * 1.6);
        const scale = 1 + d * -0.35 + (d > 0 ? 0.25 : 0);
        el.style.opacity = String(op);
        el.style.transform = `translate3d(0, ${d * -14}vh, 0) scale(${Math.max(0.6, scale)})`;
        el.style.filter = `blur(${Math.min(14, a * 10)}px)`;
      });
      if (bgRef.current) bgRef.current.style.opacity = String(0.35 + 0.5 * Math.sin(p * Math.PI));
      if (barRef.current) barRef.current.style.transform = `scaleX(${p})`;
    };

    const st = ScrollTrigger.create({
      trigger: section, start: "top top", end: "bottom bottom",
      onUpdate: (s) => { target = s.progress; },
    });
    const loop = () => {
      current += (target - current) * 0.12;
      if (Math.abs(target - current) < 0.0005) current = target;
      paint(current);
      raf = requestAnimationFrame(loop);
    };
    paint(0);
    raf = requestAnimationFrame(loop);
    return () => { cancelAnimationFrame(raf); st.kill(); };
  }, [reduced]);

  if (reduced) {
    return (
      <section id="top" className="relative flex min-h-screen flex-col items-center justify-center gap-10 px-6 py-32 text-center">
        {words.map((w, i) => (
          <div key={i}>
            <p className="font-display text-5xl font-light text-ink md:text-8xl">{t(w.text)}</p>
            {w.sub && <p className="mt-3 text-ink/60">{t(w.sub)}</p>}
          </div>
        ))}
      </section>
    );
  }

  return (
    <section id="top" ref={sectionRef} style={{ height: `${words.length * 100}vh` }} className="relative">
      <div className="sticky top-0 h-screen w-full overflow-hidden bg-bg">
        <div
          ref={bgRef}
          className="absolute inset-0"
          style={{ background: "radial-gradient(ellipse at 50% 60%, var(--accent), var(--accent-deep) 45%, transparent 75%)", opacity: 0.35 }}
        />
        <div className="pointer-events-none absolute inset-0 vignette" />
        {words.map((w, i) => (
          <div
            key={i}
            ref={(el) => { itemRefs.current[i] = el; }}
            style={{ opacity: i === 0 ? 1 : 0 }}
            className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center will-change-transform"
          >
            <p className="font-display text-[15vw] font-light leading-none tracking-tight text-ink md:text-[11vw]">{t(w.text)}</p>
            {w.sub && <p className="mt-6 max-w-xl text-base text-ink/70 md:text-xl">{t(w.sub)}</p>}
          </div>
        ))}
        <div className="absolute inset-x-0 bottom-0 h-px bg-white/10">
          <div ref={barRef} className="h-full origin-left bg-highlight" style={{ transform: "scaleX(0)" }} />
        </div>
      </div>
    </section>
  );
}
