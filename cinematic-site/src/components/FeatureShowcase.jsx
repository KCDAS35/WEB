import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import CinematicSection from "./CinematicSection";

const services = [
  {
    title: "Vedic Astrology",
    subtitle: "Jyotish Shastra",
    description:
      "Unlock the celestial map of your destiny through ancient Vedic astrological wisdom. Birth chart analysis, planetary transits, and cosmic timing guidance.",
    icon: "M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z",
  },
  {
    title: "Spiritual Healing",
    subtitle: "Pranic Wisdom",
    description:
      "Experience profound energy healing rooted in ancient traditions. Chakra balancing, aura cleansing, and karmic healing for body, mind, and soul.",
    icon: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 2c1.93 0 3.68.78 4.95 2.05l-1.41 1.41A5.96 5.96 0 0012 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6c0-1.1-.3-2.14-.83-3.03l1.43-1.43A7.96 7.96 0 0120 12c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8zm0 6a2 2 0 110 4 2 2 0 010-4z",
  },
  {
    title: "Life Coaching",
    subtitle: "Dharmic Path",
    description:
      "Navigate life's crossroads with wisdom-guided coaching. Align your purpose, overcome obstacles, and walk your authentic dharmic path with clarity.",
    icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  },
  {
    title: "Integral Yoga",
    subtitle: "Sampurna Yoga",
    description:
      "A holistic path integrating body, mind, and spirit. Ancient yogic practices adapted for modern seekers, uniting all aspects of your being.",
    icon: "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
  },
  {
    title: "Sacred Rituals",
    subtitle: "Puja & Havan",
    description:
      "Traditional Vedic ceremonies and sacred fire rituals performed with ancient mantras for protection, prosperity, and spiritual elevation.",
    icon: "M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z",
  },
  {
    title: "Cosmic Guidance",
    subtitle: "Nakshatra Wisdom",
    description:
      "Navigate the cosmic currents with personalized guidance rooted in nakshatra wisdom, muhurta selection, and celestial alignment readings.",
    icon: "M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z",
  },
];

function ServiceCard({ service, index }) {
  return (
    <CinematicSection
      direction={index % 2 === 0 ? "left" : "right"}
      delay={index * 0.12}
      className="group"
    >
      <div className="relative h-full overflow-hidden rounded-xl border border-white/5 bg-[#0c1221]/60 p-8 backdrop-blur-sm transition-all duration-500 hover:border-[#c9a23e]/20 hover:bg-[#0c1221]/80">
        {/* Hover glow */}
        <div className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition-opacity duration-500 group-hover:opacity-100">
          <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#c9a23e]/8 via-transparent to-transparent" />
        </div>

        <div className="relative z-10">
          {/* Icon */}
          <div className="mb-5 inline-flex rounded-lg border border-[#c9a23e]/15 bg-[#c9a23e]/5 p-3">
            <svg
              className="h-6 w-6 text-[#c9a23e]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d={service.icon}
              />
            </svg>
          </div>

          {/* Subtitle */}
          <p className="mb-1 font-heading text-[10px] uppercase tracking-[0.3em] text-[#c9a23e]/50">
            {service.subtitle}
          </p>

          <h3 className="mb-3 font-heading text-xl tracking-wide text-white">
            {service.title}
          </h3>

          <p className="font-body text-sm leading-relaxed text-[#e8e0d0]/40">
            {service.description}
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

  const backgroundY = useTransform(scrollYProgress, [0, 1], [0, -80]);

  return (
    <section ref={containerRef} id="teachings" className="relative py-32">
      {/* Background glow */}
      <motion.div
        style={{ y: backgroundY }}
        className="pointer-events-none absolute left-1/2 top-1/2 h-[700px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#c9a23e]/[0.02] blur-[150px]"
      />

      <div className="relative mx-auto max-w-6xl px-6">
        {/* Section heading */}
        <CinematicSection className="mb-20 text-center">
          <p className="mb-4 font-heading text-xs uppercase tracking-[0.4em] text-[#c9a23e]/70">
            Sacred Offerings
          </p>
          <h2 className="text-cinematic font-heading text-4xl font-light tracking-wide text-white sm:text-5xl">
            Paths of Illumination
          </h2>
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.2, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="mx-auto mt-6 h-px w-24 origin-center bg-gradient-to-r from-transparent via-[#c9a23e]/50 to-transparent"
          />
        </CinematicSection>

        {/* Services grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service, index) => (
            <ServiceCard key={service.title} service={service} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
