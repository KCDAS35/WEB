import { motion, useTransform, useScroll } from "framer-motion";
import { useRef } from "react";

/**
 * Text element that moves at a different rate than scroll,
 * creating a parallax depth effect.
 */
export default function ParallaxText({
  children,
  speed = 0.3,
  className = "",
  as: Tag = "div",
}) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, speed * -200]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);

  return (
    <motion.div ref={ref} style={{ y, opacity }} className={className}>
      <Tag>{children}</Tag>
    </motion.div>
  );
}
