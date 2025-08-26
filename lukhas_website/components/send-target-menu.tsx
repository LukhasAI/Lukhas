"use client";
import { useEffect, useRef } from "react";

export type SendTarget = "agent" | "email" | "sms" | "notes" | "editor";

export default function SendTargetMenu({
  open,
  onClose,
  onSelect,
  x = 0,
  y = 0,
}: {
  open: boolean;
  onClose: () => void;
  onSelect: (t: SendTarget) => void;
  x?: number;
  y?: number;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!ref.current) return;
      if (!ref.current.contains(e.target as Node)) onClose();
    };
    window.addEventListener("mousedown", onDown);
    return () => window.removeEventListener("mousedown", onDown);
  }, [open, onClose]);
  if (!open) return null;
  const items: { id: SendTarget; label: string }[] = [
    { id: "agent", label: "Agent" },
    { id: "email", label: "Email" },
    { id: "sms", label: "Text message" },
    { id: "notes", label: "Notes" },
    { id: "editor", label: "Text editor" },
  ];
  return (
    <div
      ref={ref}
      role="menu"
      aria-label="Send target"
      style={{
        position: "fixed",
        left: x,
        top: y,
        background: "#0f1117",
        border: "1px solid #1f2328",
        borderRadius: 12,
        padding: 6,
        zIndex: 1000,
        boxShadow: "0 6px 24px rgba(0,0,0,0.35)",
        minWidth: 180,
      }}
    >
      {items.map((it) => (
        <button
          key={it.id}
          role="menuitem"
          onClick={() => { onSelect(it.id); onClose(); }}
          style={{
            width: "100%",
            textAlign: "left",
            padding: "10px 12px",
            borderRadius: 8,
            border: "none",
            background: "transparent",
            color: "#e6e6e6",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = "rgba(59,130,246,0.10)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = "transparent";
          }}
        >
          {it.label}
        </button>
      ))}
    </div>
  );
}
