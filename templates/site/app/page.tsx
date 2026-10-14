import Navbar from "@/components/Navbar";
import HeroScroll from "@/components/HeroScroll";
import HeroType from "@/components/HeroType";
import Offerings from "@/components/Offerings";
import About from "@/components/About";
import Pricing from "@/components/Pricing";
import Testimonials from "@/components/Testimonials";
import Faq from "@/components/Faq";
import CtaBand from "@/components/CtaBand";
import Footer from "@/components/Footer";
import CustomCursor from "@/components/CustomCursor";
import content from "@/content.json";

const registry: Record<string, () => React.ReactElement> = {
  offerings: () => <Offerings />,
  about: () => <About />,
  pricing: () => <Pricing />,
  testimonials: () => <Testimonials />,
  faq: () => <Faq />,
  cta: () => <CtaBand />,
};

export default function Page() {
  const order = ((content as unknown as { sections?: string[] }).sections ?? ["offerings", "about", "cta"]);
  const heroMode = (content.hero as unknown as { mode?: string }).mode ?? "video";
  return (
    <main>
      <Navbar />
      {heroMode === "type" ? <HeroType /> : <HeroScroll />}
      {order.map((k) => {
        const r = registry[k];
        return r ? <div key={k}>{r()}</div> : null;
      })}
      <Footer />
      <CustomCursor />
      <div className="grain" aria-hidden="true" />
    </main>
  );
}
