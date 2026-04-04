import { motion } from "framer-motion";

export default function Footer() {
  return (
    <footer id="contact" className="relative border-t border-[#c9a23e]/10 py-16">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col items-center gap-8 sm:flex-row sm:justify-between">
          {/* Brand */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center sm:text-left"
          >
            <span className="block font-heading text-sm uppercase tracking-[0.3em] text-[#c9a23e]/60">
              Bhagwat Yogi Pundit K.C. Das
            </span>
            <span className="mt-1 block text-[10px] uppercase tracking-[0.15em] text-[#e8e0d0]/25">
              Jagat Sampurna Integral Yogi Samai
            </span>
          </motion.div>

          {/* Nav */}
          <motion.nav
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex gap-8"
          >
            {["Home", "Jyotish", "Teachings", "About"].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="font-heading text-[11px] uppercase tracking-[0.15em] text-[#e8e0d0]/30 transition-colors hover:text-[#c9a23e]"
              >
                {item}
              </a>
            ))}
          </motion.nav>
        </div>

        {/* Bottom */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-12 border-t border-[#c9a23e]/5 pt-8 text-center"
        >
          <p className="text-glow-gold font-heading text-xs tracking-[0.4em] text-[#c9a23e]/40">
            OM TAT SAT
          </p>
          <p className="mt-3 font-body text-[10px] tracking-wide text-[#e8e0d0]/15">
            &copy; {new Date().getFullYear()} Coach KCDAS. Sacred wisdom, eternal light.
          </p>
        </motion.div>
      </div>
    </footer>
  );
}
