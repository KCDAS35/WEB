import { motion } from "framer-motion";

export default function Footer() {
  return (
    <footer className="relative border-t border-white/5 py-16">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col items-center gap-8 sm:flex-row sm:justify-between">
          {/* Logo / brand */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <span className="text-lg font-extralight tracking-[0.3em] text-white/60">
              CINEMATIC
            </span>
          </motion.div>

          {/* Navigation */}
          <motion.nav
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex gap-8"
          >
            {["Features", "Showreel", "About"].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-sm tracking-wide text-white/40 transition-colors hover:text-[#c9a55c]"
              >
                {item}
              </a>
            ))}
          </motion.nav>
        </div>

        {/* Bottom line */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-12 border-t border-white/5 pt-8 text-center"
        >
          <p className="text-xs tracking-wide text-white/25">
            Crafted with code. Powered by vision.
          </p>
        </motion.div>
      </div>
    </footer>
  );
}
