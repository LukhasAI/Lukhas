"use client";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import ComposerActions from "./composer-actions";

interface ComposerActionsPortalProps {
  show: boolean;
  position: { x: number; y: number };
  onAction: (action: string) => void;
}

export default function ComposerActionsPortal({ 
  show, 
  position, 
  onAction 
}: ComposerActionsPortalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !show) return null;

  return createPortal(
    <div
      style={{
        position: "fixed",
        left: position.x,
        top: position.y,
        zIndex: "var(--z-overlay)",
        pointerEvents: "auto",
      }}
    >
      <ComposerActions onAction={onAction} />
    </div>,
    document.body
  );
}