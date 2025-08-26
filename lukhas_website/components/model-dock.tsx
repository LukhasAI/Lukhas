"use client";
import { useState, useMemo, useEffect } from "react";
import { useModel } from "@/components/model-context";
import { suggestNextHops, executeHop } from "@lukhas/orchestrator/handover";
import { Diamond, Circle, List, Square } from "lucide-react";
import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";

type Item = { id:string; label:string; svg:(active:boolean)=>JSX.Element; skill?:string; status?:string };
const MODELS: Item[] = [
  { id:"lukhas-core", label:"LUKHΛS", svg: (a)=>iconL(a), status: "online" },
  { id:"openai:gpt-5-pro", label:"GPT-5", svg: (a)=>iconO(a), skill:"validate.facts", status: "online" },
  { id:"perplexity:sonar", label:"Sonar", svg: (a)=>iconP(a), skill:"web.research", status: "limited" },
  { id:"sora:video", label:"Sora", svg: (a)=>iconS(a), skill:"video.generate", status: "beta" },
];

export default function ModelDock({ capsule }: { capsule?: ContextCapsule }) {
  const { current, setCurrent } = useModel();
  const [dragOver, setDragOver] = useState<string|null>(null);
  const [pulse, setPulse] = useState<string|null>(null);
  const items = useMemo(()=>MODELS,[]);

  function getStatusColor(status?: string) {
    switch(status) {
      case "online": return "#22c55e";
      case "limited": return "#f59e0b";
      case "beta": return "#a78bfa";
      case "offline": return "#64748b";
      default: return "#9aa4b2";
    }
  }

  async function handoff(to:string, skill?:string) {
    if (!capsule) return;
    setPulse(to);
    const goals = skill ? [skill as any] : [];
    const hops = goals.length ? await suggestNextHops(goals, capsule) : [{ to, skill:"prompt.optimize" as any }];
    if (!hops[0]) return;
    await executeHop(hops[0], capsule); // TODO: surface result card if desired
    setTimeout(() => setPulse(null), 2000);
  }

  return (
    <nav aria-label="Models" style={{ display:"grid", gap:12, padding:10 }}>
      {items.map((m)=>{
        const isActive = current.id === m.id;
        const isPulsing = pulse === m.id;
        const isDragOver = dragOver === m.id;

        return (
          <div key={m.id} style={{ position: "relative" }}>
            <button
              title={`${m.label} ${m.status ? `(${m.status})` : ""}`}
              onClick={()=> setCurrent({ id:m.id, label:m.label })}
              onDragOver={(e)=>{ e.preventDefault(); setDragOver(m.id); }}
              onDragLeave={()=> setDragOver(null)}
              onDrop={(e)=>{ e.preventDefault(); setDragOver(null); handoff(m.id, m.skill); }}
              style={{
                width:44,height:44,borderRadius:12,display:"grid",placeItems:"center",
                border:`2px solid ${isActive ? "#60a5fa" : isDragOver ? "#3b82f6" : "var(--line)"}`,
                background: isActive ? "rgba(96,165,250,0.1)" : "transparent",
                cursor:"pointer",
                transform: isPulsing ? "scale(1.05)" : "scale(1)",
                transition: "all 0.2s ease",
                boxShadow: isActive ? "0 0 12px rgba(96,165,250,0.3)" : "none"
              }}
            >
              {m.svg(isActive)}
            </button>
            {/* Status indicator dot */}
            <div
              style={{
                position: "absolute",
                top: -2,
                right: -2,
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: getStatusColor(m.status),
                border: "2px solid var(--bg)",
                boxShadow: `0 0 4px ${getStatusColor(m.status)}`,
              }}
            />
            {/* Active pulse ring */}
            {isPulsing && (
              <div
                style={{
                  position: "absolute",
                  inset: -4,
                  borderRadius: 16,
                  border: "2px solid #60a5fa",
                  opacity: 0.6,
                  animation: "pulse 1s infinite",
                }}
              />
            )}
          </div>
        );
      })}
    </nav>
  );
}

/* Lucide icon functions */
function iconL(a:boolean){ return <Diamond size={18} color={a?"#60a5fa":"#9aa4b2"} /> }
function iconO(a:boolean){ return <Circle size={18} color={a?"#60a5fa":"#9aa4b2"} /> }
function iconP(a:boolean){ return <List size={18} color={a?"#60a5fa":"#9aa4b2"} /> }
function iconS(a:boolean){ return <Square size={18} color={a?"#60a5fa":"#9aa4b2"} /> }
