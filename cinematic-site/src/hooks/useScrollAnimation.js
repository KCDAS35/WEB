import { useRef, useState, useEffect, useCallback } from "react";

/**
 * Custom hook that tracks an element's scroll progress through the viewport
 * and triggers animation states based on configurable thresholds.
 *
 * Returns: { ref, scrollProgress, isInView, hasEntered }
 *   - ref: attach to the target element
 *   - scrollProgress: 0-1 value of how far through the viewport the element is
 *   - isInView: whether the element is currently visible
 *   - hasEntered: stays true once the element has entered (for one-shot animations)
 */
export default function useScrollAnimation({
  threshold = 0.15,
  rootMargin = "0px 0px -10% 0px",
} = {}) {
  const ref = useRef(null);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isInView, setIsInView] = useState(false);
  const [hasEntered, setHasEntered] = useState(false);

  // IntersectionObserver for in-view detection
  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const inView = entry.isIntersecting;
        setIsInView(inView);
        if (inView) setHasEntered(true);
      },
      { threshold, rootMargin }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  // Scroll-based progress calculation
  const updateProgress = useCallback(() => {
    const el = ref.current;
    if (!el) return;

    const rect = el.getBoundingClientRect();
    const windowHeight = window.innerHeight;

    // 0 = element just entering bottom, 1 = element leaving top
    const progress = Math.min(
      Math.max((windowHeight - rect.top) / (windowHeight + rect.height), 0),
      1
    );
    setScrollProgress(progress);
  }, []);

  useEffect(() => {
    const handleScroll = () => requestAnimationFrame(updateProgress);
    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll(); // initial calculation
    return () => window.removeEventListener("scroll", handleScroll);
  }, [updateProgress]);

  return { ref, scrollProgress, isInView, hasEntered };
}
