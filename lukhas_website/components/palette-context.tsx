"use client";
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";

type Mode = "closed" | "mini" | "full";
type PaletteCtx = {
  mode: Mode;
  query: string;
  setQuery: (s: string) => void;
  openMini: () => void;
  openFull: () => void;
  close: () => void;
  capsule?: ContextCapsule;
  setCapsule: (c?: ContextCapsule) => void;
  // helpers for chat box routing:
  isIntercepting: boolean; // true when mode !== closed
  executeFromQuery: (q: string) => Promise<void>;
  scope: "thread" | "all" | "org";
  setScope: (s: "thread" | "all" | "org") => void;
};

const Ctx = createContext<PaletteCtx | null>(null);
export function usePalette() {
  const v = useContext(Ctx); if (!v) throw new Error("PaletteProvider missing");
  return v;
}

export function PaletteProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<Mode>("closed");
  const [query, setQuery] = useState("");
  const [capsule, setCapsule] = useState<ContextCapsule | undefined>(undefined);
  const [scope, setScope] = useState<"thread"|"all"|"org">(() => {
    try { return (localStorage.getItem("lukhas:paletteScope") as any) || "thread"; } catch { return "thread"; }
  });
  useEffect(() => { try { localStorage.setItem("lukhas:paletteScope", scope); } catch {} }, [scope]);

  // Listen for capsule bridge events from pages
  useEffect(() => {
    const onCapsule = (e: any) => setCapsule(e.detail as ContextCapsule);
    window.addEventListener("lukhas:capsule", onCapsule as any);
    return () => window.removeEventListener("lukhas:capsule", onCapsule as any);
  }, []);

  const openMini = useCallback(() => setMode("mini"), []);
  const openFull = useCallback(() => setMode("full"), []);
  const close = useCallback(() => { setMode("closed"); setQuery(""); }, []);

  const isIntercepting = mode !== "closed";

  async function executeFromQuery(q: string) {
    const ev = new CustomEvent("lukhas:palette-exec", { detail: { q } });
    document.dispatchEvent(ev);
  }

  const value = useMemo(() => ({
    mode, query, setQuery, openMini, openFull, close, capsule, setCapsule, isIntercepting, executeFromQuery, scope, setScope
  }), [mode, query, capsule, isIntercepting, scope]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
