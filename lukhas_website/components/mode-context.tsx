"use client";
import React, { createContext, useContext, useMemo, useState } from "react";

export type Mode = "agent" | "email" | "doc" | "code" | "message";

type Ctx = {
  mode: Mode;
  setMode: (m: Mode) => void;
};

const M = createContext<Ctx | null>(null);

export function useMode() {
  const v = useContext(M);
  if (!v) throw new Error("ModeProvider missing");
  return v;
}

export function ModeProvider({ threadId, children }: { threadId: string; children: React.ReactNode }) {
  const key = `lukhas:mode:${threadId}`;
  const [mode, setModeState] = useState<Mode>(() => {
    if (typeof window === 'undefined') return "agent";
    try {
      return (localStorage.getItem(key) as Mode) || "agent";
    } catch {
      return "agent";
    }
  });

  function setMode(m: Mode) {
    setModeState(m);
    try {
      localStorage.setItem(key, m);
    } catch {}
  }

  const value = useMemo(() => ({ mode, setMode }), [mode]);

  return <M.Provider value={value}>{children}</M.Provider>;
}
