// components/marketing/NeuralBackground.tsx
"use client"

import React, { useEffect, useRef, useState } from "react";

type Mode = "svg" | "canvas" | "webgl";

function pickMode(): Mode {
  if (typeof window === 'undefined') return "svg";

  const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  // @ts-ignore - deviceMemory is not in standard types yet
  const mem = (navigator as any).deviceMemory ?? 4;
  const cores = navigator.hardwareConcurrency ?? 4;
  // @ts-ignore - connection.saveData is not in standard types yet
  const batterySaver = (navigator as any).connection?.saveData === true;

  if (reduce || batterySaver) return "svg";
  if (mem >= 8 && cores >= 8) return "webgl";
  return "canvas";
}

export default function NeuralBackground() {
  const [mode, setMode] = useState<Mode>("svg");
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    setMode(pickMode());
  }, []);

  useEffect(() => {
    if (mode === "canvas" && canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      if (!ctx) return;
      let raf = 0;
      const W = (canvasRef.current.width = window.innerWidth * (window.devicePixelRatio || 1));
      const H = (canvasRef.current.height = window.innerHeight * (window.devicePixelRatio || 1));

      // Scale canvas for high DPI
      canvasRef.current.style.width = window.innerWidth + 'px';
      canvasRef.current.style.height = window.innerHeight + 'px';
      ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

      const pts = Array.from({ length: 60 }, () => ({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4
      }));

      const loop = () => {
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        ctx.globalAlpha = 0.6;
        ctx.strokeStyle = "rgba(180,200,255,0.25)";

        // Update and draw particles
        pts.forEach(p => {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0 || p.x > window.innerWidth) p.vx *= -1;
          if (p.y < 0 || p.y > window.innerHeight) p.vy *= -1;
        });

        // Draw connections
        for (let i = 0; i < pts.length; i++){
          for (let j = i + 1; j < pts.length; j++){
            const dx = pts[i].x - pts[j].x;
            const dy = pts[i].y - pts[j].y;
            const d = Math.hypot(dx, dy);
            if (d < 140){
              ctx.beginPath();
              ctx.moveTo(pts[i].x, pts[i].y);
              ctx.lineTo(pts[j].x, pts[j].y);
              ctx.stroke();
            }
          }
        }
        raf = requestAnimationFrame(loop);
      };
      raf = requestAnimationFrame(loop);
      return () => cancelAnimationFrame(raf);
    }
  }, [mode]);

  if (mode === "svg") {
    return (
      <svg
        aria-hidden="true"
        role="img"
        className="fixed inset-0 -z-10 w-full h-full"
      >
        <defs>
          <radialGradient id="neural-gradient" cx="50%" cy="50%">
            <stop offset="0%" stopColor="rgba(59,130,246,0.15)" />
            <stop offset="50%" stopColor="rgba(37,99,235,0.1)" />
            <stop offset="100%" stopColor="rgba(15,23,42,0.95)" />
          </radialGradient>
          <pattern id="neural-grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(59,130,246,0.1)" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#neural-gradient)" />
        <rect width="100%" height="100%" fill="url(#neural-grid)" opacity="0.3" />
        {/* Static neural network lines for SVG mode */}
        <g stroke="rgba(180,200,255,0.2)" strokeWidth="0.5" fill="none">
          <path d="M 0,100 Q 200,50 400,100 T 800,100" />
          <path d="M 0,200 Q 300,150 600,200 T 1200,200" />
          <path d="M 0,300 Q 250,250 500,300 T 1000,300" />
        </g>
      </svg>
    );
  }

  if (mode === "canvas") {
    return <canvas ref={canvasRef} className="fixed inset-0 -z-10 w-full h-full" />;
  }

  // WebGL mode - placeholder for future implementation
  return <div id="neural-webgl" className="fixed inset-0 -z-10 w-full h-full bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800" />;
}
