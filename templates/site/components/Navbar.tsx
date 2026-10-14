"use client";

import { useEffect, useState } from "react";
import content from "@/content.json";

type Layers = { nav: string[]; navButton: string };
const L = (content.hero as unknown as { layers: Layers }).layers;
const LOGO = (content.brand as unknown as { logo?: string }).logo; // e.g. "/logo.png" (optional; falls back to the brand name)
const TARGETS = ["#collection", "#about", "#about", "#contact"];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 40);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);

  return (
    <header className={`fixed inset-x-0 top-0 z-50 transition-all duration-700 ease-out ${scrolled ? "bg-black/35 backdrop-blur-md" : "bg-transparent"}`}>
      <div className="flex items-center justify-between px-[4vw] py-5">
        <a href="#top" aria-label={content.brand.name} className="block">
          {LOGO ? (
            <img src={LOGO} alt={content.brand.name} className="h-[1.55rem] w-auto md:h-[2.1rem]" />
          ) : (
            <span className="font-display text-[clamp(1.2rem,1.9vw,1.9rem)] tracking-[0.34em] text-ink">{content.brand.name}</span>
          )}
        </a>
        <div className="flex items-stretch">
          <nav className="hidden items-center gap-9 bg-black/40 px-8 backdrop-blur-sm md:flex">
            {L.nav.map((label, i) => (
              <a key={label} href={TARGETS[i] ?? "#top"} className="text-[0.62rem] uppercase tracking-[0.18em] text-ink/70 transition hover:text-ink">
                {label}
              </a>
            ))}
          </nav>
          <a href="#contact" className="flex h-11 items-center bg-ink px-6 text-[0.62rem] font-medium uppercase tracking-[0.16em] text-black transition hover:bg-highlight">
            {L.navButton}
          </a>
        </div>
      </div>
    </header>
  );
}
