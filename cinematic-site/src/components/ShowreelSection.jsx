import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import CinematicSection from "./CinematicSection";

export default function ShowreelSection() {
  const sectionRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.85, 1]);
  const borderRadius = useTransform(scrollYProgress, [0, 0.5], [40, 16]);
  const opacity = useTransform(scrollYProgress, [0, 0.3], [0, 1]);

  return (
    <section ref={sectionRef} className="relative px-6 py-32">
      <div className="mx-auto max-w-5xl">
        <CinematicSection className="mb-16 text-center">
          <p className="mb-4 text-sm uppercase tracking-[0.3em] text-[#c9a55c]">
            Showreel
          </p>
          <h2 className="text-cinematic text-4xl font-extralight tracking-wide text-white sm:text-5xl">
            See It in Motion
          </h2>
        </CinematicSection>

        {/* Video showcase card */}
        <motion.div
          style={{ scale, borderRadius, opacity }}
          className="relative mx-auto aspect-video max-w-4xl overflow-hidden border border-white/10 bg-gradient-to-br from-white/[0.03] to-transparent"
        >
          {/* Placeholder for video content */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              {/* Play button */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="group mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full border border-white/20 bg-white/5 backdrop-blur-sm transition-colors hover:border-[#c9a55c]/40 hover:bg-white/10"
              >
                <svg
                  className="ml-1 h-8 w-8 text-white/80 transition-colors group-hover:text-[#c9a55c]"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              </motion.button>
              <p className="text-sm tracking-widest text-white/40">
                PLAY SHOWREEL
              </p>
            </div>
          </div>

          {/* Animated gradient background */}
          <motion.div
            animate={{
              background: [
                "radial-gradient(ellipse at 20% 50%, #1a1a2e 0%, #0a0a0f 70%)",
                "radial-gradient(ellipse at 80% 50%, #1a1a2e 0%, #0a0a0f 70%)",
                "radial-gradient(ellipse at 50% 80%, #1a1a2e 0%, #0a0a0f 70%)",
                "radial-gradient(ellipse at 20% 50%, #1a1a2e 0%, #0a0a0f 70%)",
              ],
            }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 -z-10"
          />
        </motion.div>
      </div>
    </section>
  );
}
