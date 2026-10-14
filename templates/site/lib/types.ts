export type L10n = Record<string, string>;

export interface AboutContent {
  title: L10n;
  body: L10n;
  stats?: { value: string; label: L10n }[];
}

export interface OfferingItem {
  name: L10n;
  blurb: L10n;
  tag?: L10n;
}

export interface OfferingsContent {
  eyebrow: L10n;
  title: L10n;
  items: OfferingItem[];
}

export interface PricingTier {
  name: L10n;
  price: L10n;
  note?: L10n;
  features: L10n[];
  highlight?: boolean;
  cta: L10n;
  href: string;
}

export interface Testimonial {
  quote: L10n;
  name: string;
  role?: L10n;
  source?: string;
}

export interface FaqItem {
  q: L10n;
  a: L10n;
}

export interface Channel {
  label: L10n;
  href: string;
}

export interface HeroWord {
  text: L10n;
  sub?: L10n;
}
