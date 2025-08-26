"use client";
import { useEffect, useRef } from "react";
import { usePalette } from "./palette-context";

export default function TopHotspot() {
  const pal = usePalette();
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const onEnter = () => pal.openMini();
    const onLeave = () => pal.close();
    el.addEventListener("mouseenter", onEnter);
    el.addEventListener("mouseleave", onLeave);
    return () => { el.removeEventListener("mouseenter", onEnter); el.removeEventListener("mouseleave", onLeave); };
  }, [pal]);
  return (
    <div
      ref={ref}
      aria-hidden
      style={{
        position: "fixed",
        left: "50%", transform: "translateX(-50%)",
        top: 0,
        width: 380,
        height: 8,             // tiny hover strip
        zIndex: 999,
      }}
    />
  );
}
