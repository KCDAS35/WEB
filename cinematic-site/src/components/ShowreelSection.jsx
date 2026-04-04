import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import CinematicSection from "./CinematicSection";

export default function ShowreelSection() {
  const sectionRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.88, 1]);
  const opacity = useTransform(scrollYProgress, [0, 0.3], [0, 1]);

  return (
    <section ref={sectionRef} id="jyotish" className="relative px-6 py-32">
      <div className="mx-auto max-w-5xl">
        <CinematicSection className="mb-16 text-center">
          <p className="mb-4 font-heading text-xs uppercase tracking-[0.4em] text-[#c9a23e]/70">
            The Ancient Science
          </p>
          <h2 className="text-cinematic font-heading text-4xl font-light tracking-wide text-white sm:text-5xl">
            Jyotish Vidya
          </h2>
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.2, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="mx-auto mt-6 h-px w-24 origin-center bg-gradient-to-r from-transparent via-[#c9a23e]/50 to-transparent"
          />
        </CinematicSection>

        {/* Cosmic showcase */}
        <motion.div
          style={{ scale, opacity }}
          className="relative mx-auto aspect-video max-w-4xl overflow-hidden rounded-2xl border border-[#c9a23e]/10 bg-gradient-to-br from-[#0c1221] to-[#070b15]"
        >
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center px-8">
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="group mb-8 inline-flex h-20 w-20 items-center justify-center rounded-full border border-[#c9a23e]/20 bg-[#c9a23e]/5 backdrop-blur-sm transition-colors hover:border-[#c9a23e]/40 hover:bg-[#c9a23e]/10 cursor-pointer"
              >
                <svg
                  className="ml-1 h-8 w-8 text-[#c9a23e]/70 transition-colors group-hover:text-[#c9a23e]"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              </motion.div>
              <p className="mb-2 font-heading text-sm uppercase tracking-[0.3em] text-[#c9a23e]/40">
                Watch the Vision
              </p>
              <p className="font-body text-sm text-[#e8e0d0]/25 max-w-md mx-auto">
                Explore the ancient science of light and discover how the celestial bodies shape your destiny
              </p>
            </div>
          </div>

          {/* Animated cosmic background */}
          <motion.div
            animate={{
              background: [
                "radial-gradient(ellipse at 20% 50%, #0f1a30 0%, #070b15 70%)",
                "radial-gradient(ellipse at 80% 30%, #150f30 0%, #070b15 70%)",
                "radial-gradient(ellipse at 50% 80%, #0f1a30 0%, #070b15 70%)",
                "radial-gradient(ellipse at 20% 50%, #0f1a30 0%, #070b15 70%)",
              ],
            }}
            transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 -z-10"
          />
        </motion.div>
      </div>
    </section>
  );
}
