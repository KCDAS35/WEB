import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { useState } from "react";

const navItems = [
  { label: "Home", href: "#" },
  { label: "Jyotish", href: "#jyotish" },
  { label: "Teachings", href: "#teachings" },
  { label: "About", href: "#about" },
  { label: "Contact", href: "#contact" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setScrolled(latest > 50);
  });

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.3, duration: 0.8 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "border-b border-[#c9a23e]/10 bg-[#070b15]/90 backdrop-blur-md"
          : "bg-transparent"
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        {/* Brand */}
        <a href="#" className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="KCDAS"
            className="h-8 w-8 object-contain"
          />
          <div className="hidden sm:block">
            <span className="block font-heading text-xs uppercase tracking-[0.2em] text-[#c9a23e]">
              Bhagwat Yogi Pundit K.C. Das
            </span>
            <span className="block text-[9px] uppercase tracking-[0.15em] text-[#e8e0d0]/30">
              Astrologer &middot; Life Coach &middot; Spiritual Healer
            </span>
          </div>
        </a>

        {/* Nav links */}
        <div className="hidden items-center gap-8 md:flex">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="font-heading text-[11px] uppercase tracking-[0.2em] text-[#e8e0d0]/50 transition-colors hover:text-[#c9a23e]"
            >
              {item.label}
            </a>
          ))}
        </div>

        {/* CTA */}
        <a
          href="#portal"
          className="rounded border border-[#c9a23e]/30 px-4 py-2 font-heading text-[10px] uppercase tracking-[0.2em] text-[#c9a23e] transition-all hover:border-[#c9a23e]/60 hover:shadow-[0_0_15px_rgba(201,162,62,0.15)]"
        >
          Enter Portal
        </a>
      </div>
    </motion.nav>
  );
}
