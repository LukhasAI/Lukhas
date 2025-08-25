"use client";
import { useEffect, useRef, useState } from "react";
import type { ResultCardData } from "./result-card";
import ResultCard from "./result-card";

export default function CanvasCarousel({
  cards,
  onIndex,
}: {
  cards: ResultCardData[];
  onIndex?: (i: number) => void;
}) {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") { snapTo(index + 1); }
      if (e.key === "ArrowLeft") { snapTo(index - 1); }
    };
    el.addEventListener("keydown", onKey);
    return () => el.removeEventListener("keydown", onKey);
  }, [index]);

  useEffect(() => { onIndex?.(index); }, [index, onIndex]);

  function snapTo(i: number) {
    const el = wrapRef.current; if (!el) return;
    const clamped = Math.max(0, Math.min(cards.length - 1, i));
    setIndex(clamped);
    const child = el.children[clamped] as HTMLElement | undefined;
    child?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
  }

  // Trackpad friendly: native horizontal scroll with scroll-snap
  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div
        ref={wrapRef}
        tabIndex={0}
        role="listbox"
        aria-label="Canvas carousel"
        style={{
          display: "grid",
          gridAutoFlow: "column",
          gap: 12,
          overflowX: "auto",
          padding: "6px 2px",
          scrollSnapType: "x mandatory",
          scrollbarWidth: "none" as any,
          msOverflowStyle: "none",
        }}
        onScroll={(e) => {
          // update index using nearest snap child
          const el = e.currentTarget;
          const x = el.scrollLeft + el.clientWidth / 2;
          let nearest = 0, best = Infinity;
          Array.from(el.children).forEach((c, i) => {
            const r = (c as HTMLElement).offsetLeft + (c as HTMLElement).offsetWidth / 2;
            const d = Math.abs(r - x);
            if (d < best) { best = d; nearest = i; }
          });
          if (nearest !== index) setIndex(nearest);
        }}
      >
        {cards.map((c) => (
          <div
            key={c.id}
            role="option"
            aria-selected={false}
            style={{
              scrollSnapAlign: "center",
              scrollSnapStop: "always",
              padding: "6px 4px",
            }}
          >
            <ResultCard data={c} />
          </div>
        ))}
      </div>
      <Dots count={cards.length} index={index} onPick={(i) => snapTo(i)} />
    </div>
  );
}

function Dots({ count, index, onPick }: { count: number; index: number; onPick: (i: number) => void }) {
  if (count <= 1) return null;
  return (
    <div style={{ display: "flex", gap: 6, justifyContent: "center", paddingTop: 2 }}>
      {Array.from({ length: count }).map((_, i) => (
        <button
          key={i}
          aria-label={`Go to item ${i + 1}`}
          onClick={() => onPick(i)}
          style={{
            width: i === index ? 22 : 10,
            height: 8,
            borderRadius: 999,
            border: "1px solid #2a2f37",
            background: i === index ? "rgba(59,130,246,0.20)" : "transparent",
            cursor: "pointer",
          }}
        />
      ))}
    </div>
  );
}