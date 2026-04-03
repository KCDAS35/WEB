import { useRef, useState, useEffect, useCallback } from "react";

/**
 * Custom hook to manage video playback state and synchronize
 * with scroll position for scroll-driven video experiences.
 *
 * Modes:
 *  - "autoplay": normal looping playback
 *  - "scroll": scrub video position based on scroll progress (0–1)
 */
export default function useVideoPlayback({ mode = "autoplay" } = {}) {
  const videoRef = useRef(null);
  const [playbackState, setPlaybackState] = useState({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    progress: 0,
    isReady: false,
  });

  // Update state from video events
  const handleTimeUpdate = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    setPlaybackState((prev) => ({
      ...prev,
      currentTime: video.currentTime,
      progress: video.duration ? video.currentTime / video.duration : 0,
    }));
  }, []);

  const handleLoadedMetadata = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    setPlaybackState((prev) => ({
      ...prev,
      duration: video.duration,
      isReady: true,
    }));
  }, []);

  const handlePlay = useCallback(() => {
    setPlaybackState((prev) => ({ ...prev, isPlaying: true }));
  }, []);

  const handlePause = useCallback(() => {
    setPlaybackState((prev) => ({ ...prev, isPlaying: false }));
  }, []);

  // Attach event listeners
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("loadedmetadata", handleLoadedMetadata);
    video.addEventListener("play", handlePlay);
    video.addEventListener("pause", handlePause);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
      video.removeEventListener("play", handlePlay);
      video.removeEventListener("pause", handlePause);
    };
  }, [handleTimeUpdate, handleLoadedMetadata, handlePlay, handlePause]);

  // Scroll-driven scrubbing
  const scrubTo = useCallback(
    (progress) => {
      const video = videoRef.current;
      if (!video || !playbackState.isReady) return;
      const clampedProgress = Math.min(Math.max(progress, 0), 1);
      video.currentTime = clampedProgress * video.duration;
    },
    [playbackState.isReady]
  );

  // Play/pause controls
  const play = useCallback(() => {
    videoRef.current?.play().catch(() => {});
  }, []);

  const pause = useCallback(() => {
    videoRef.current?.pause();
  }, []);

  const toggle = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.paused ? play() : pause();
  }, [play, pause]);

  return {
    videoRef,
    playbackState,
    scrubTo,
    play,
    pause,
    toggle,
  };
}
