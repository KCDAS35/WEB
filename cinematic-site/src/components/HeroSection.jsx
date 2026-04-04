import { motion } from "framer-motion";
import { useState } from "react";

const letterVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: 1.2 + i * 0.06,
      duration: 0.7,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  }),
};

export default function HeroSection() {
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
  });

  const titleLine1 = "Discover Your";
  const titleLine2 = "Celestial Blueprint";

  const handleSubmit = (e) => {
    e.preventDefault();
    // Portal entry logic
  };

  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-6 py-20">
      {/* Logo emblem */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.5, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="mb-8"
        style={{ animation: "float 6s ease-in-out infinite" }}
      >
        <div className="relative">
          {/* Glow behind logo */}
          <div
            className="absolute inset-0 blur-3xl"
            style={{
              background:
                "radial-gradient(circle, rgba(201,162,62,0.15) 0%, transparent 70%)",
              transform: "scale(1.5)",
            }}
          />
          <img
            src="/logo.png"
            alt="Jagat Sampurna Integral Yogi Samai"
            className="relative h-48 w-48 object-contain sm:h-56 sm:w-56 md:h-64 md:w-64"
          />
        </div>
      </motion.div>

      {/* Subtitle above title */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 1 }}
        className="mb-4 font-heading text-xs uppercase tracking-[0.4em] text-[#c9a23e]/70 sm:text-sm"
      >
        Jyotish &middot; The Science of Light
      </motion.p>

      {/* Animated title */}
      <div className="mb-2 text-center">
        <h1 className="text-cinematic font-heading">
          <span className="flex justify-center overflow-hidden">
            {titleLine1.split("").map((letter, i) => (
              <motion.span
                key={`l1-${i}`}
                custom={i}
                variants={letterVariants}
                initial="hidden"
                animate="visible"
                className="inline-block text-3xl font-light tracking-[0.15em] text-[#e8e0d0] sm:text-4xl md:text-5xl"
              >
                {letter === " " ? "\u00A0" : letter}
              </motion.span>
            ))}
          </span>
          <span className="mt-1 flex justify-center overflow-hidden sm:mt-2">
            {titleLine2.split("").map((letter, i) => (
              <motion.span
                key={`l2-${i}`}
                custom={i + titleLine1.length}
                variants={letterVariants}
                initial="hidden"
                animate="visible"
                className="inline-block text-4xl font-normal tracking-[0.12em] text-white sm:text-5xl md:text-6xl lg:text-7xl"
              >
                {letter === " " ? "\u00A0" : letter}
              </motion.span>
            ))}
          </span>
        </h1>
      </div>

      {/* Accent line */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{
          delay: 2.8,
          duration: 1.2,
          ease: [0.25, 0.46, 0.45, 0.94],
        }}
        className="mb-4 h-px w-40 origin-center bg-gradient-to-r from-transparent via-[#c9a23e] to-transparent"
      />

      {/* Sub-tagline */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 3.0, duration: 0.8 }}
        className="mb-12 font-body text-sm italic tracking-widest text-[#e8e0d0]/40 sm:text-base"
      >
        your path of sacred wisdom awaits
      </motion.p>

      {/* Portal Form */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 3.3, duration: 1 }}
        className="w-full max-w-sm"
      >
        <div
          className="relative overflow-hidden rounded-lg border border-[#c9a23e]/15 bg-[#0c1221]/80 p-8 backdrop-blur-md"
          style={{ animation: "pulse-glow 4s ease-in-out infinite" }}
        >
          {/* Form glow accent */}
          <div className="pointer-events-none absolute -top-20 left-1/2 h-40 w-40 -translate-x-1/2 rounded-full bg-[#c9a23e]/5 blur-3xl" />

          <h2 className="text-glow-gold relative mb-6 text-center font-heading text-lg uppercase tracking-[0.25em] text-[#c9a23e]">
            Begin Your Journey
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1 block font-heading text-[10px] uppercase tracking-[0.2em] text-[#e8e0d0]/40">
                Full Name
              </label>
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) =>
                  setFormData({ ...formData, fullName: e.target.value })
                }
                className="portal-input w-full rounded px-4 py-2.5 font-body text-sm"
                placeholder="Enter your name"
              />
            </div>
            <div>
              <label className="mb-1 block font-heading text-[10px] uppercase tracking-[0.2em] text-[#e8e0d0]/40">
                Email Address
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="portal-input w-full rounded px-4 py-2.5 font-body text-sm"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label className="mb-1 block font-heading text-[10px] uppercase tracking-[0.2em] text-[#e8e0d0]/40">
                Create Password
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="portal-input w-full rounded px-4 py-2.5 font-body text-sm"
                placeholder="Create a password"
              />
            </div>

            <motion.button
              type="submit"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="mt-2 w-full rounded bg-gradient-to-r from-[#a07c2e] via-[#c9a23e] to-[#a07c2e] px-6 py-3 font-heading text-xs uppercase tracking-[0.3em] text-[#070b15] transition-all hover:shadow-[0_0_30px_rgba(201,162,62,0.3)]"
            >
              Enter the Portal
            </motion.button>
          </form>

          <p className="mt-4 text-center font-body text-xs text-[#e8e0d0]/30">
            Already registered?{" "}
            <a
              href="#"
              className="text-[#c9a23e]/60 underline transition-colors hover:text-[#c9a23e]"
            >
              Sign In
            </a>
          </p>
        </div>
      </motion.div>

      {/* Om Tat Sat */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 4.0, duration: 1 }}
        className="text-glow-gold mt-10 font-heading text-sm tracking-[0.4em] text-[#c9a23e]/60"
      >
        OM TAT SAT
      </motion.p>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 4.5, duration: 0.8 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          className="flex flex-col items-center gap-2"
        >
          <svg
            width="16"
            height="24"
            viewBox="0 0 16 24"
            className="text-[#c9a23e]/30"
          >
            <rect
              x="1"
              y="1"
              width="14"
              height="22"
              rx="7"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
            />
            <motion.circle
              cx="8"
              cy="8"
              r="2"
              fill="currentColor"
              animate={{ cy: [7, 15, 7] }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </svg>
        </motion.div>
      </motion.div>
    </section>
  );
}
