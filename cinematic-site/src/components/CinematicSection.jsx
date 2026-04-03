import { motion } from "framer-motion";
import useScrollAnimation from "../hooks/useScrollAnimation";

/**
 * A reusable section that animates its children into view
 * with cinematic fade/slide transitions driven by scroll.
 */
export default function CinematicSection({
  children,
  className = "",
  direction = "up",
  delay = 0,
  id,
}) {
  const { ref, hasEntered } = useScrollAnimation({ threshold: 0.15 });

  const directionOffsets = {
    up: { y: 60, x: 0 },
    down: { y: -60, x: 0 },
    left: { x: 80, y: 0 },
    right: { x: -80, y: 0 },
  };

  const offset = directionOffsets[direction] || directionOffsets.up;

  return (
    <motion.section
      id={id}
      ref={ref}
      initial={{ opacity: 0, ...offset }}
      animate={
        hasEntered
          ? { opacity: 1, x: 0, y: 0 }
          : { opacity: 0, ...offset }
      }
      transition={{
        duration: 0.9,
        delay,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
      className={className}
    >
      {children}
    </motion.section>
  );
}
