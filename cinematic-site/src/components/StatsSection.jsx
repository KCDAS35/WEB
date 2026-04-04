import { useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import CinematicSection from "./CinematicSection";

function AnimatedCounter({ value, suffix = "", prefix = "", duration = 2 }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;

    let start = 0;
    const end = parseInt(value, 10);
    const stepTime = (duration * 1000) / end;
    const timer = setInterval(() => {
      start += 1;
      setCount(start);
      if (start >= end) clearInterval(timer);
    }, Math.max(stepTime, 16));

    return () => clearInterval(timer);
  }, [isInView, value, duration]);

  return (
    <span ref={ref}>
      {prefix}
      {count}
      {suffix}
    </span>
  );
}

const stats = [
  { value: "25", suffix: "+", label: "Years of Practice" },
  { value: "10", suffix: "K+", label: "Lives Transformed" },
  { value: "108", suffix: "", label: "Sacred Teachings" },
  { value: "12", suffix: "", label: "Cosmic Houses" },
];

export default function StatsSection() {
  return (
    <section className="relative overflow-hidden border-y border-[#c9a23e]/10 py-24">
      {/* Side accents */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-0 top-0 h-full w-px bg-gradient-to-b from-transparent via-[#c9a23e]/15 to-transparent" />
        <div className="absolute right-0 top-0 h-full w-px bg-gradient-to-b from-transparent via-[#c9a23e]/15 to-transparent" />
      </div>

      <div className="mx-auto grid max-w-5xl grid-cols-2 gap-12 px-6 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <CinematicSection key={stat.label} delay={index * 0.1}>
            <div className="text-center">
              <div className="text-glow-gold mb-2 font-heading text-4xl tracking-tight text-[#c9a23e] sm:text-5xl">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  duration={1.5}
                />
              </div>
              <div className="font-heading text-[10px] uppercase tracking-[0.25em] text-[#e8e0d0]/30">
                {stat.label}
              </div>
            </div>
          </CinematicSection>
        ))}
      </div>
    </section>
  );
}
