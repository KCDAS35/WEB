import HeroSection from "./components/HeroSection";
import FeatureShowcase from "./components/FeatureShowcase";
import ShowreelSection from "./components/ShowreelSection";
import StatsSection from "./components/StatsSection";
import ParallaxText from "./components/ParallaxText";
import Footer from "./components/Footer";
import "./index.css";

export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Hero — full-screen cinematic intro */}
      <HeroSection
        title="CINEMATIC"
        subtitle="A visual experience crafted in code"
      />

      {/* Parallax divider quote */}
      <div className="py-32">
        <ParallaxText
          speed={0.5}
          className="mx-auto max-w-3xl px-6 text-center"
        >
          <p className="text-2xl font-extralight leading-relaxed tracking-wide text-white/50 sm:text-3xl">
            &ldquo;Where every pixel tells a story and every scroll reveals a
            new chapter.&rdquo;
          </p>
        </ParallaxText>
      </div>

      {/* Features */}
      <FeatureShowcase />

      {/* Stats */}
      <StatsSection />

      {/* Showreel */}
      <ShowreelSection />

      {/* Parallax closing */}
      <div className="py-32">
        <ParallaxText
          speed={0.3}
          className="mx-auto max-w-2xl px-6 text-center"
        >
          <p className="text-xl font-extralight tracking-widest text-white/30">
            DESIGNED FOR THE SCREEN. BUILT WITH CODE.
          </p>
        </ParallaxText>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}
