import { useMemo } from "react";

export default function Starfield({ count = 150 }) {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      size: Math.random() * 2.5 + 0.5,
      duration: `${Math.random() * 4 + 2}s`,
      delay: `${Math.random() * 5}s`,
      minOpacity: Math.random() * 0.15 + 0.05,
      maxOpacity: Math.random() * 0.6 + 0.3,
      color:
        Math.random() > 0.85
          ? `hsl(${40 + Math.random() * 20}, 70%, 70%)`  // gold-tinted stars
          : Math.random() > 0.7
          ? `hsl(${200 + Math.random() * 40}, 50%, 75%)` // blue-tinted stars
          : "white",
    }));
  }, [count]);

  return (
    <div className="starfield" aria-hidden="true">
      {stars.map((star) => (
        <div
          key={star.id}
          className="star"
          style={{
            left: star.left,
            top: star.top,
            width: `${star.size}px`,
            height: `${star.size}px`,
            background: star.color,
            "--duration": star.duration,
            "--delay": star.delay,
            "--min-opacity": star.minOpacity,
            "--max-opacity": star.maxOpacity,
          }}
        />
      ))}

      {/* Larger ambient glow spots */}
      <div
        className="absolute rounded-full"
        style={{
          width: "400px",
          height: "400px",
          left: "15%",
          top: "20%",
          background:
            "radial-gradient(circle, rgba(30,58,110,0.08) 0%, transparent 70%)",
        }}
      />
      <div
        className="absolute rounded-full"
        style={{
          width: "500px",
          height: "500px",
          right: "10%",
          top: "50%",
          background:
            "radial-gradient(circle, rgba(74,32,128,0.06) 0%, transparent 70%)",
        }}
      />
      <div
        className="absolute rounded-full"
        style={{
          width: "300px",
          height: "300px",
          left: "50%",
          bottom: "10%",
          background:
            "radial-gradient(circle, rgba(201,162,62,0.04) 0%, transparent 70%)",
        }}
      />
    </div>
  );
}
