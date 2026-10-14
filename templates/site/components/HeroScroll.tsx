"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import content from "@/content.json";
import theme from "@/theme.json";

gsap.registerPlugin(ScrollTrigger);

type Layers = {
  paragraph: { pre: string; bold: string };
  headline: string[];
  cta: string;
  big: string;
  footerTag: string;
  columns: { title: string; text: string }[];
  card: { title: string; button: string; href: string };
};
type Caption = { from: number; to: number; text: string };
type Range = [number, number];
type Timing = {
  paraFade: Range; headOut: Range; headFade: Range; ctaFade: Range;
  bigIn: Range; bigShow: Range; bigWords: Range; bigOut: Range; bigHide: Range;
  colsIn: Range; colsOut: Range; colsHide: Range; card: Range;
};

const HERO = content.hero as unknown as { preset?: "layers" | "captions"; layers: Layers; captions?: Caption[]; timing?: Partial<Timing> };
const PRESET = HERO.preset ?? "layers";
const L = HERO.layers;
const CAPTIONS = HERO.captions ?? [];

// Fractions of the hero scroll (0..1). Override any of them in content.json -> hero.timing to match a reference.
const T: Timing = {
  paraFade: [0.10, 0.26], headOut: [0.14, 0.36], headFade: [0.26, 0.38], ctaFade: [0.12, 0.24],
  bigIn: [0.34, 0.50], bigShow: [0.34, 0.42], bigWords: [0.44, 0.64], bigOut: [0.78, 0.92], bigHide: [0.84, 0.92],
  colsIn: [0.56, 0.68], colsOut: [0.78, 0.92], colsHide: [0.84, 0.92], card: [0.84, 0.97],
  ...(HERO.timing ?? {}),
};
const BIG_WORDS = (L?.big ?? "").split(" ");
const FADE = 0.035;

// 0..1 ramp between a and b with ease-in-out
const ramp = (p: number, [a, b]: Range) => {
  const x = Math.min(1, Math.max(0, (p - a) / (b - a)));
  return x * x * (3 - 2 * x);
};
const captionOpacity = (p: number, c: Caption) =>
  Math.min(Math.min(1, Math.max(0, (p - c.from) / FADE)), Math.min(1, Math.max(0, (c.to - p) / FADE)));

function Arrow() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M1 7h11M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="square" />
    </svg>
  );
}

export default function HeroScroll() {
  const sectionRef = useRef<HTMLElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const paraRef = useRef<HTMLDivElement>(null);
  const headRef = useRef<HTMLHeadingElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const bigRef = useRef<HTMLDivElement>(null);
  const wordRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const colsRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const capRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [reduced, setReduced] = useState(false);
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const small = window.matchMedia("(max-width: 768px)").matches;
    setSrc(small ? "/hero-mobile.mp4" : "/hero.mp4");
  }, []);

  useEffect(() => {
    if (reduced || !src) return;
    const video = videoRef.current;
    const section = sectionRef.current;
    if (!video || !section) return;

    let target = 0;
    let current = 0;
    let raf = 0;
    let ready = false;
    const n = BIG_WORDS.length;

    const paintLayers = (p: number) => {
      const out = ramp(p, T.headOut);
      if (headRef.current) {
        headRef.current.style.transform = `translate3d(0, ${(-out * 78).toFixed(2)}vh, 0)`;
        headRef.current.style.opacity = String(1 - ramp(p, T.headFade));
      }
      if (paraRef.current) {
        paraRef.current.style.transform = `translate3d(0, ${(-out * 52).toFixed(2)}vh, 0)`;
        paraRef.current.style.opacity = String(1 - ramp(p, T.paraFade));
      }
      if (ctaRef.current) {
        ctaRef.current.style.transform = `translate3d(0, ${(-out * 30).toFixed(2)}vh, 0)`;
        ctaRef.current.style.opacity = String(1 - ramp(p, T.ctaFade));
      }
      const bigIn = ramp(p, T.bigIn);
      const bigOut = ramp(p, T.bigOut);
      if (bigRef.current) {
        bigRef.current.style.transform = `translate3d(0, ${((1 - bigIn) * 72 - bigOut * 80).toFixed(2)}vh, 0)`;
        bigRef.current.style.opacity = String(ramp(p, T.bigShow) * (1 - ramp(p, T.bigHide)));
      }
      const [w0, w1] = T.bigWords;
      for (let i = 0; i < n; i++) {
        const el = wordRefs.current[i];
        if (!el) continue;
        const a = w0 + (i / n) * (w1 - w0);
        el.style.opacity = String(0.16 + 0.84 * ramp(p, [a, a + 0.05]));
      }
      if (colsRef.current) {
        const cIn = ramp(p, T.colsIn);
        colsRef.current.style.transform = `translate3d(0, ${((1 - cIn) * 10 - ramp(p, T.colsOut) * 80).toFixed(2)}vh, 0)`;
        colsRef.current.style.opacity = String(cIn * (1 - ramp(p, T.colsHide)));
      }
      if (cardRef.current) {
        cardRef.current.style.transform = `translate3d(0, ${((1 - ramp(p, T.card)) * 115).toFixed(2)}%, 0)`;
      }
    };

    const paintCaptions = (p: number) => {
      CAPTIONS.forEach((c, i) => {
        const el = capRefs.current[i];
        if (!el) return;
        const op = captionOpacity(p, c);
        el.style.opacity = String(op);
        el.style.transform = `translateY(${(1 - op) * 18}px)`;
      });
    };

    const paint = PRESET === "captions" ? paintCaptions : paintLayers;

    const unlock = () => {
      // iOS Safari only allows seeking after a user gesture has touched the element.
      video.play().then(() => video.pause()).catch(() => {});
      window.removeEventListener("touchstart", unlock);
      window.removeEventListener("pointerdown", unlock);
    };
    window.addEventListener("touchstart", unlock, { passive: true });
    window.addEventListener("pointerdown", unlock, { passive: true });

    const onMeta = () => { ready = true; };
    if (video.readyState >= 1) ready = true;
    video.addEventListener("loadedmetadata", onMeta);
    video.load();

    const st = ScrollTrigger.create({
      trigger: section,
      start: "top top",
      end: "bottom bottom",
      scrub: false,
      onUpdate: (self) => { target = self.progress; },
    });

    const loop = () => {
      current += (target - current) * 0.14;
      if (Math.abs(target - current) < 0.0005) current = target;
      paint(current);
      if (ready && video.duration) {
        const time = current * video.duration;
        if (Math.abs(video.currentTime - time) > 1 / 45 && !video.seeking) {
          const v = video as HTMLVideoElement & { fastSeek?: (t: number) => void };
          if (typeof v.fastSeek === "function") v.fastSeek(time);
          else video.currentTime = time;
        }
      }
      raf = requestAnimationFrame(loop);
    };
    paint(0);
    raf = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(raf);
      st.kill();
      video.removeEventListener("loadedmetadata", onMeta);
      window.removeEventListener("touchstart", unlock);
      window.removeEventListener("pointerdown", unlock);
    };
  }, [reduced, src]);

  if (reduced) {
    return (
      <section id="top" className="relative min-h-screen overflow-hidden">
        <img src="/hero-poster.jpg" alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-black/55" />
        <div className="relative z-10 mx-auto flex min-h-screen max-w-3xl flex-col justify-end gap-8 px-6 py-32">
          {PRESET === "captions" ? (
            CAPTIONS.map((c, i) => <p key={i} className="font-display text-3xl font-light text-ink md:text-5xl">{c.text}</p>)
          ) : (
            <>
              <p className="max-w-md text-sm text-ink/80">{L.paragraph.pre} <strong className="font-semibold text-ink">{L.paragraph.bold}</strong></p>
              <h1 className="font-display text-5xl leading-[1.05] text-ink">{L.headline.join(" ")}</h1>
              <p className="font-display text-2xl text-ink">{L.big}</p>
            </>
          )}
        </div>
      </section>
    );
  }

  return (
    <section id="top" ref={sectionRef} style={{ height: `${theme.scroll_height_vh}vh` }} className="relative">
      <div className="sticky top-0 h-screen w-full overflow-hidden bg-black">
        <video
          ref={videoRef}
          key={src ?? "none"}
          src={src ?? undefined}
          poster="/hero-poster.jpg"
          muted
          playsInline
          preload="auto"
          className="absolute inset-0 h-full w-full object-cover"
          aria-hidden="true"
        />
        {/* soft scrims keep the type readable over bright frames, without a visible vignette */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[38vh] bg-gradient-to-b from-black/55 to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-[55vh] bg-gradient-to-t from-black/60 to-transparent" />

        {PRESET === "captions" ? (
          CAPTIONS.map((c, i) => (
            <div
              key={i}
              ref={(el) => { capRefs.current[i] = el; }}
              style={{ opacity: 0 }}
              className="pointer-events-none absolute inset-0 flex items-end justify-center px-6 pb-[14vh] text-center md:pb-[12vh]"
            >
              <p className="max-w-3xl font-display text-3xl font-light leading-tight text-ink drop-shadow-[0_2px_24px_rgba(0,0,0,0.65)] md:text-6xl">{c.text}</p>
            </div>
          ))
        ) : (
          <>
            {/* top-right paragraph */}
            <div ref={paraRef} className="pointer-events-none absolute right-[4vw] top-[22vh] w-[min(92vw,34rem)] text-right will-change-transform md:top-[24vh] md:w-[min(42vw,38rem)]">
              <p className="font-display text-[clamp(0.85rem,1.08vw,1.05rem)] leading-[1.45] text-ink/75">
                {L.paragraph.pre} <strong className="font-semibold text-ink">{L.paragraph.bold}</strong>
              </p>
            </div>

            {/* headline, bottom-left */}
            <h1
              ref={headRef}
              className="pointer-events-none absolute bottom-[8vh] left-[4vw] font-display text-[clamp(2.1rem,4.7vw,5.4rem)] font-normal leading-[1.04] tracking-[-0.015em] text-ink will-change-transform md:bottom-[7vh]"
            >
              {L.headline.map((line, i) => (
                <span key={i} className="block">{line}</span>
              ))}
            </h1>

            {/* cta, bottom-right */}
            <div ref={ctaRef} className="absolute bottom-[8vh] right-[4vw] hidden will-change-transform md:bottom-[7vh] md:flex">
              <a href="#collection" className="flex h-[3.4rem] items-center bg-black/55 px-8 text-[0.68rem] uppercase tracking-[0.16em] text-ink backdrop-blur-sm transition hover:bg-black/75">
                {L.cta}
              </a>
              <a href="#collection" aria-label={L.cta} className="flex h-[3.4rem] w-[3.4rem] items-center justify-center border-l border-white/15 bg-black/55 text-ink backdrop-blur-sm transition hover:bg-black/75">
                <Arrow />
              </a>
            </div>

            {/* big statement with word-by-word reveal */}
            <div ref={bigRef} style={{ opacity: 0 }} className="pointer-events-none absolute inset-x-[4vw] bottom-[26vh] will-change-transform md:bottom-[24vh]">
              <p className="max-w-[92%] font-display text-[clamp(1.3rem,3.7vw,4.3rem)] leading-[1.1] tracking-[-0.01em] text-ink">
                {BIG_WORDS.map((w, i) => (
                  <span key={i} ref={(el) => { wordRefs.current[i] = el; }} style={{ opacity: 0.16 }} className="inline-block pr-[0.26em]">{w}</span>
                ))}
              </p>
            </div>

            {/* small columns */}
            <div ref={colsRef} style={{ opacity: 0 }} className="pointer-events-none absolute inset-x-[4vw] bottom-[4vh] grid grid-cols-2 gap-4 will-change-transform md:bottom-[6vh] md:grid-cols-[1.1fr_1fr_1fr] md:gap-10">
              <div className="hidden md:block">
                <p className="font-display text-xl tracking-[0.3em] text-ink">{content.brand.name}</p>
                <p className="mt-3 text-[0.62rem] uppercase tracking-[0.2em] text-ink/55">{L.footerTag}</p>
              </div>
              {L.columns.map((c, i) => (
                <div key={i}>
                  <p className="font-display text-[clamp(0.95rem,1.15vw,1.15rem)] font-medium leading-snug text-ink">{c.title}</p>
                  <p className="mt-2 max-w-[24rem] font-display text-[clamp(0.72rem,0.8vw,0.85rem)] leading-[1.55] text-ink/65">{c.text}</p>
                </div>
              ))}
            </div>

            {/* closing card */}
            <div ref={cardRef} style={{ transform: "translate3d(0,115%,0)" }} className="absolute inset-x-[3vw] bottom-0 will-change-transform">
              <div className="flex flex-col items-start justify-between gap-5 bg-[#1a1916]/95 px-[4vw] py-[4vh] backdrop-blur-sm md:flex-row md:items-center">
                <h2 className="font-display text-[clamp(1.5rem,3vw,3.4rem)] leading-[1.08] tracking-[-0.01em] text-ink">{L.card.title}</h2>
                <a href={L.card.href} className="flex h-[3.4rem] shrink-0 items-center gap-3 bg-ink px-8 text-[0.68rem] uppercase tracking-[0.16em] text-black transition hover:bg-highlight">
                  {L.card.button} <Arrow />
                </a>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
