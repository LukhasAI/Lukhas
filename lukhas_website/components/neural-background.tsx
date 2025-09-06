"use client";
import { useEffect, useRef } from "react";

type Mode = "landing" | "studio" | "showcase";

export default function NeuralBackground({ mode = "landing" }: { mode?: Mode }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    const saveData = (navigator as any).connection?.saveData === true;
    const mem = (navigator as any).deviceMemory || 4;
    const cores = navigator.hardwareConcurrency || 4;
    if (reduce || saveData || mem < 4 || cores < 4) return;

    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // intensity by mode
    const COUNT = mode === "landing" ? 70 : mode === "showcase" ? 80 : 40;
    const THRESH = mode === "landing" ? 140 : mode === "showcase" ? 150 : 110;

    const particles = Array.from({ length: COUNT }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
    }));

    let raf = 0;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.globalAlpha = 0.6;
      ctx.strokeStyle = "rgba(180,200,255,0.25)";
      particles.forEach((p) => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      });
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d = Math.hypot(dx, dy);
          if (d < THRESH) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, [mode]);

  return (
    <div
      aria-hidden
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 0,
        pointerEvents: "none",
        background:
          "radial-gradient(60% 60% at 50% 50%, rgba(58,100,255,0.08), rgba(10,12,20,0.9))",
      }}
    >
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
