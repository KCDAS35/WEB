import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import FeatureShowcase from "./components/FeatureShowcase";
import ShowreelSection from "./components/ShowreelSection";
import StatsSection from "./components/StatsSection";
import ParallaxText from "./components/ParallaxText";
import Footer from "./components/Footer";
import Starfield from "./components/Starfield";
import "./index.css";

export default function App() {
  return (
    <div className="relative min-h-screen bg-[#070b15] font-body text-[#e8e0d0]">
      {/* Fixed starfield background */}
      <Starfield count={180} />

      {/* Navigation */}
      <Navbar />

      {/* Content layer */}
      <div className="relative z-10">
        {/* Hero — full-screen intro with portal */}
        <HeroSection />

        {/* Parallax wisdom quote */}
        <div className="py-24">
          <ParallaxText
            speed={0.4}
            className="mx-auto max-w-3xl px-6 text-center"
          >
            <p className="font-heading text-2xl font-light leading-relaxed tracking-wide text-[#e8e0d0]/30 sm:text-3xl">
              &ldquo;The cosmos is within us. We are made of star-stuff. We are
              a way for the universe to know itself.&rdquo;
            </p>
          </ParallaxText>
        </div>

        {/* Jyotish showcase */}
        <ShowreelSection />

        {/* Stats */}
        <StatsSection />

        {/* Sacred offerings / services */}
        <FeatureShowcase />

        {/* Closing mantra */}
        <div className="py-24">
          <ParallaxText
            speed={0.3}
            className="mx-auto max-w-2xl px-6 text-center"
          >
            <p className="text-glow-gold font-heading text-xl tracking-[0.3em] text-[#c9a23e]/30">
              LOKAH SAMASTAH SUKHINO BHAVANTU
            </p>
            <p className="mt-3 font-body text-sm italic text-[#e8e0d0]/20">
              May all beings everywhere be happy and free
            </p>
          </ParallaxText>
        </div>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}
