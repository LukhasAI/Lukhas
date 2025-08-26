"use client";
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import { PROVIDERS, type Provider, getDefaultModel } from "@lukhas/models/registry";

type FallbackMode = "latency_then_quality" | "quality_then_latency" | "off";
type ModelState = { current: Provider; setCurrent: (p: Provider) => void; fallback: FallbackMode; setFallback: (f: FallbackMode) => void; providers: Provider[]; threadKey: string; };
const Ctx = createContext<ModelState | null>(null);
export function useModel() {
  const v = useContext(Ctx); if (!v) throw new Error("useModel must be inside <ModelProvider>");
  return v;
}

export function getThreadKey(pathname: string) {
  // Sticky per thread: /studio/[threadId]? -> that segment; else "default"
  const parts = pathname.split("/").filter(Boolean);
  const ix = parts.indexOf("studio");
  return ix >= 0 && parts[ix + 1] ? `studio:${parts[ix + 1]}` : "studio:default";
}

export function ModelProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const threadKey = useMemo(() => getThreadKey(pathname ?? "/studio"), [pathname]);
  const storageKey = `lukhas:model:${threadKey}`;
  const fbKey = `lukhas:model:fallback`;

  const [current, setCurrent] = useState<Provider>(getDefaultModel());
  const [fallback, setFallback] = useState<FallbackMode>("latency_then_quality");

  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      const rawFb = localStorage.getItem(fbKey);
      if (raw) {
        const parsed = JSON.parse(raw) as Provider;
        if (parsed?.id && PROVIDERS.some(p => p.id === parsed.id)) setCurrent(parsed);
      }
      if (rawFb === "latency_then_quality" || rawFb === "quality_then_latency" || rawFb === "off") setFallback(rawFb);
    } catch {}
  }, [storageKey, fbKey]);

  useEffect(() => {
    try { localStorage.setItem(storageKey, JSON.stringify(current)); } catch {}
  }, [current, storageKey]);

  useEffect(() => {
    try { localStorage.setItem(fbKey, fallback); } catch {}
  }, [fallback, fbKey]);

  const value = useMemo<ModelState>(() => ({
    current, setCurrent, fallback, setFallback, providers: PROVIDERS, threadKey
  }), [current, fallback, threadKey]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
