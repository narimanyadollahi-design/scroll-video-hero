"use client";

import { createContext, useCallback, useContext, useEffect, useState, ReactNode } from "react";
import content from "@/content.json";

export type Lang = string;
export type L10n = Record<string, string>;

type Ctx = { lang: Lang; setLang: (l: Lang) => void; t: (v?: L10n | string | null) => string; languages: string[] };

const LangContext = createContext<Ctx | null>(null);
const RTL = new Set(["fa", "ar", "he", "ur"]);

export function LangProvider({ children }: { children: ReactNode }) {
  const languages: string[] = content.languages;
  const [lang, setLangState] = useState<Lang>(content.default_lang);

  const apply = useCallback((l: Lang) => {
    document.documentElement.lang = l;
    document.documentElement.dir = RTL.has(l) ? "rtl" : "ltr";
  }, []);

  useEffect(() => {
    let saved: string | null = null;
    try { saved = localStorage.getItem("lang"); } catch {}
    const next = saved && languages.includes(saved) ? saved : content.default_lang;
    setLangState(next);
    apply(next);
  }, [apply, languages]);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    apply(l);
    try { localStorage.setItem("lang", l); } catch {}
  }, [apply]);

  const t = useCallback((v?: L10n | string | null) => {
    if (!v) return "";
    if (typeof v === "string") return v;
    return v[lang] ?? v[content.default_lang] ?? Object.values(v)[0] ?? "";
  }, [lang]);

  return <LangContext.Provider value={{ lang, setLang, t, languages }}>{children}</LangContext.Provider>;
}

export function useLang() {
  const c = useContext(LangContext);
  if (!c) throw new Error("useLang must be used inside LangProvider");
  return c;
}
