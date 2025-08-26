"use client";
import React from "react";
import { getTier, widgetOrderKey } from "./layout-prefs";
import { visibleWidgets } from "./widget-registry";

export default function WidgetRail({ side, defaults, half }: { side: "left"|"right"|"top"|"bottom"; defaults: string[]; half?: boolean }) {
  const key = widgetOrderKey(side);
  const [order, setOrder] = React.useState<string[]>(() => {
    if (typeof window === 'undefined') return []; // SSR fallback
    try {
      const stored = localStorage?.getItem(key);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const tier = getTier();
  const canDrag = tier >= 4;
  const ids = (order.length ? order : defaults);
  const ws = visibleWidgets(ids);

  function save(o:string[]){
    if (typeof window === 'undefined') return; // SSR guard
    try {
      localStorage?.setItem(key, JSON.stringify(o));
    } catch {}
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>, to: string){
    const from = e.dataTransfer.getData("text/plain");
    if(!from) return;

    const next = ids.filter(x=>x!==from);
    const idx = next.indexOf(to);
    next.splice(idx<0?next.length:idx, 0, from);

    setOrder(next);
    save(next);
  }

  // Meta-adaptive usage tracking
  function trackUsage(widgetId: string) {
    if (typeof window === 'undefined') return; // SSR guard
    try {
      const prefsStored = localStorage?.getItem("lukhas:prefs");
      if (prefsStored) {
        const prefs = JSON.parse(prefsStored);
        if (prefs.metaAdaptive) {
          const k = `lukhas:usage:${side}:${widgetId}`;
          const n = Number(localStorage?.getItem(k)||0)+1;
          localStorage?.setItem(k,String(n));
        }
      }
    } catch {}
  }

  return (
    <div style={{
      display:"grid", gap:10, padding:10,
      borderRight: side==="left"?"1px solid var(--line)":undefined,
      borderLeft: side==="right"?"1px solid var(--line)":undefined,
      borderBottom: side==="top"?"1px solid var(--line)":undefined,
      borderTop: side==="bottom"?"1px solid var(--line)":undefined,
      height: half ? "50vh" : "auto",
      overflow:"auto"
    }}>
      {ws.map(w=>(
        <section key={w.id}
          onMouseEnter={() => trackUsage(w.id)}
          draggable={canDrag}
          onDragStart={(e)=>{ e.dataTransfer.setData("text/plain", w.id); }}
          onDragOver={(e)=>e.preventDefault()}
          onDrop={(e)=>onDrop(e,w.id)}
          title={canDrag? "Drag to reorder" : "Upgrade to Tier 4 for full customization"}
          style={{
            border:"1px solid var(--line2)",
            borderRadius:12,
            padding:10,
            background:"var(--panel)",
            opacity: canDrag ? 1 : .85,
            cursor: canDrag ? "grab" : "default",
            transition: "all 0.2s ease"
          }}
        >
          <header style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:6}}>
            <strong className="t-13" style={{opacity:.9}}>{w.title}</strong>
            <div style={{display:"flex", gap:8, alignItems:"center"}}>
              {!canDrag && <span className="t-11" style={{opacity:.6}}>🔒</span>}
              {w.action && (
                <button
                  onClick={w.action.onClick}
                  style={{
                    padding:"4px 8px",
                    border:"1px solid var(--line)",
                    borderRadius:8,
                    background:"transparent",
                    color:"var(--text)",
                    cursor:"pointer"
                  }}
                >
                  {w.action.label}
                </button>
              )}
            </div>
          </header>
          <div>{w.node}</div>
        </section>
      ))}
      {ws.length===0 && <div className="t-13" style={{opacity:.7, padding:10, textAlign:"center"}}>Drag widgets here (Tier 4+), or enable Meta-adaptive in Settings.</div>}
    </div>
  );
}
