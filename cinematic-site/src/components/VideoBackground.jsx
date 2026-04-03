import { useRef, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * Full-screen cinematic video background with lazy loading,
 * fallback image, and film-grain overlay.
 */
export default function VideoBackground({
  videoSrc,
  fallbackImage,
  posterImage,
  className = "",
}) {
  const videoRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  const handleCanPlay = useCallback(() => {
    setIsLoaded(true);
    videoRef.current?.play().catch(() => {});
  }, []);

  const handleError = useCallback(() => {
    setHasError(true);
  }, []);

  return (
    <div
      className={`absolute inset-0 overflow-hidden ${className}`}
      aria-hidden="true"
    >
      {/* Fallback / Poster image */}
      <AnimatePresence>
        {(!isLoaded || hasError) && (
          <motion.img
            key="fallback"
            src={fallbackImage || posterImage}
            alt=""
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 1.2 } }}
            className="absolute inset-0 h-full w-full object-cover"
            loading="eager"
          />
        )}
      </AnimatePresence>

      {/* Video element */}
      {!hasError && videoSrc && (
        <video
          ref={videoRef}
          muted
          loop
          playsInline
          preload="auto"
          poster={posterImage}
          onCanPlayThrough={handleCanPlay}
          onError={handleError}
          className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-1000 ${
            isLoaded ? "opacity-100" : "opacity-0"
          }`}
        >
          <source src={videoSrc} type="video/mp4" />
        </video>
      )}

      {/* Cinematic overlay gradient */}
      <div className="cinematic-overlay absolute inset-0" />

      {/* Vignette */}
      <div className="cinematic-vignette absolute inset-0" />

      {/* Film grain */}
      <div className="film-grain absolute inset-0" />
    </div>
  );
}
