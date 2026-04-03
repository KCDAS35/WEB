import { motion } from "framer-motion";
import VideoBackground from "./VideoBackground";

const letterVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: 0.8 + i * 0.05,
      duration: 0.6,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  }),
};

const subtitleVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { delay: 2.0, duration: 1.0, ease: "easeOut" },
  },
};

const scrollIndicatorVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { delay: 2.8, duration: 0.8 },
  },
};

export default function HeroSection({ title = "CINEMATIC", subtitle = "A visual experience crafted in code" }) {
  const letters = title.split("");

  return (
    <section className="relative flex h-screen items-center justify-center overflow-hidden">
      {/* Video background — uses placeholder gradient when no video provided */}
      <VideoBackground
        videoSrc=""
        fallbackImage=""
        posterImage=""
      />

      {/* Animated fallback gradient for demo */}
      <div
        className="absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(ellipse at 50% 30%, #1a1a2e 0%, #0a0a0f 60%)",
        }}
      />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center px-6 text-center">
        {/* Animated title — letter by letter */}
        <h1 className="text-cinematic mb-6 flex overflow-hidden font-heading">
          {letters.map((letter, i) => (
            <motion.span
              key={i}
              custom={i}
              variants={letterVariants}
              initial="hidden"
              animate="visible"
              className="inline-block text-6xl font-extralight tracking-[0.3em] text-white sm:text-7xl md:text-8xl lg:text-9xl"
            >
              {letter === " " ? "\u00A0" : letter}
            </motion.span>
          ))}
        </h1>

        {/* Accent line */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 1.8, duration: 1.2, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="mb-8 h-px w-48 origin-center bg-gradient-to-r from-transparent via-[#c9a55c] to-transparent"
        />

        {/* Subtitle */}
        <motion.p
          variants={subtitleVariants}
          initial="hidden"
          animate="visible"
          className="text-cinematic max-w-lg text-lg font-light tracking-widest text-white/70 sm:text-xl"
        >
          {subtitle}
        </motion.p>
      </div>

      {/* Scroll indicator */}
      <motion.div
        variants={scrollIndicatorVariants}
        initial="hidden"
        animate="visible"
        className="absolute bottom-10 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 12, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="flex flex-col items-center gap-2"
        >
          <span className="text-xs uppercase tracking-[0.25em] text-white/40">
            Scroll
          </span>
          <svg
            width="20"
            height="30"
            viewBox="0 0 20 30"
            className="text-white/30"
          >
            <rect
              x="1"
              y="1"
              width="18"
              height="28"
              rx="9"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            />
            <motion.circle
              cx="10"
              cy="10"
              r="3"
              fill="currentColor"
              animate={{ cy: [8, 18, 8] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
          </svg>
        </motion.div>
      </motion.div>
    </section>
  );
}
