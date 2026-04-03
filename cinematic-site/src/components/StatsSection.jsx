import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import CinematicSection from "./CinematicSection";

function AnimatedCounter({ value, suffix = "", duration = 2 }) {
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
      {count}
      {suffix}
    </span>
  );
}

const stats = [
  { value: "60", suffix: "fps", label: "Smooth Animation" },
  { value: "95", suffix: "+", label: "Performance Score" },
  { value: "3", suffix: "s", label: "Load Time" },
  { value: "100", suffix: "%", label: "Code-Driven" },
];

export default function StatsSection() {
  return (
    <section className="relative overflow-hidden border-y border-white/5 py-24">
      {/* Background line accent */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-0 top-0 h-full w-px bg-gradient-to-b from-transparent via-[#c9a55c]/20 to-transparent" />
        <div className="absolute right-0 top-0 h-full w-px bg-gradient-to-b from-transparent via-[#c9a55c]/20 to-transparent" />
      </div>

      <div className="mx-auto grid max-w-5xl grid-cols-2 gap-12 px-6 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <CinematicSection key={stat.label} delay={index * 0.1}>
            <div className="text-center">
              <div className="mb-2 text-4xl font-extralight tracking-tight text-white sm:text-5xl">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  duration={1.5}
                />
              </div>
              <div className="text-sm uppercase tracking-[0.2em] text-white/40">
                {stat.label}
              </div>
            </div>
          </CinematicSection>
        ))}
      </div>
    </section>
  );
}
