import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import CinematicSection from "./CinematicSection";

const features = [
  {
    title: "Video-to-Code",
    description:
      "Transform visual assets into production-ready components with AI-assisted workflows.",
    icon: "M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z",
  },
  {
    title: "Cinematic Motion",
    description:
      "Scroll-synchronized animations that bring depth and narrative to every interaction.",
    icon: "M7 4V20M17 4V20M3 8H7M17 8H21M3 12H21M3 16H7M17 16H21M4 20H20C20.5523 20 21 19.5523 21 19V5C21 4.44772 20.5523 4 20 4H4C3.44772 4 3 4.44772 3 5V19C3 19.5523 3.44772 20 4 20Z",
  },
  {
    title: "Peak Performance",
    description:
      "Optimized assets, lazy loading, and hardware-accelerated compositing for buttery 60fps.",
    icon: "M13 10V3L4 14h7v7l9-11h-7z",
  },
];

function FeatureCard({ feature, index }) {
  return (
    <CinematicSection
      direction={index % 2 === 0 ? "left" : "right"}
      delay={index * 0.15}
      className="group"
    >
      <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur-sm transition-all duration-500 hover:border-[#c9a55c]/20 hover:bg-white/[0.04]">
        {/* Glow effect on hover */}
        <div className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100">
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#c9a55c]/10 via-transparent to-transparent" />
        </div>

        <div className="relative z-10">
          {/* Icon */}
          <div className="mb-6 inline-flex rounded-xl border border-white/10 bg-white/5 p-3">
            <svg
              className="h-6 w-6 text-[#c9a55c]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d={feature.icon}
              />
            </svg>
          </div>

          <h3 className="mb-3 text-xl font-light tracking-wide text-white">
            {feature.title}
          </h3>
          <p className="text-sm leading-relaxed text-white/50">
            {feature.description}
          </p>
        </div>
      </div>
    </CinematicSection>
  );
}

export default function FeatureShowcase() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const backgroundY = useTransform(scrollYProgress, [0, 1], [0, -100]);

  return (
    <section ref={containerRef} className="relative py-32">
      {/* Background accent */}
      <motion.div
        style={{ y: backgroundY }}
        className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#c9a55c]/[0.03] blur-[120px]"
      />

      <div className="relative mx-auto max-w-6xl px-6">
        {/* Section heading */}
        <CinematicSection className="mb-20 text-center">
          <p className="mb-4 text-sm uppercase tracking-[0.3em] text-[#c9a55c]">
            Features
          </p>
          <h2 className="text-cinematic text-4xl font-extralight tracking-wide text-white sm:text-5xl">
            Built for the Screen
          </h2>
        </CinematicSection>

        {/* Feature grid */}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
