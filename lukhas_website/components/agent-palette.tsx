"use client";
import { useEffect, useMemo, useState } from "react";
import { registry, type Command } from "@lukhas/agent-commands/index";
import { usePalette } from "./palette-context";
import PromptPreview from "./prompt-preview";
import { toProviderPrompt } from "@lukhas/orchestrator/promptAdapter";
import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";

type Entry = { id: string; title: string; hint?: string; cmd: Command };
const MAX_RECENTS = 8;

// ---------- ranking & preview helpers ----------
function scopeKey(scope: "thread"|"all"|"org", capsule?: ContextCapsule) {
  if (scope==="thread" && capsule?.threadId) return `thread:${capsule.threadId}`;
  if (scope==="org") return "org:lukhas"; // placeholder until org id exists
  return "all";
}
function getStats(scope: "thread"|"all"|"org", capsule?: ContextCapsule): Record<string, number> {
  try { return JSON.parse(localStorage.getItem("lukhas:cmdstats."+scopeKey(scope,capsule)) || "{}"); } catch { return {}; }
}
function bumpStat(scope: "thread"|"all"|"org", capsule: ContextCapsule|undefined, id: string) {
  try {
    const key = "lukhas:cmdstats."+scopeKey(scope, capsule);
    const cur = getStats(scope, capsule);
    cur[id] = (cur[id]||0)+1;
    localStorage.setItem(key, JSON.stringify(cur));
  } catch {}
}
function rankByStats(items: Entry[], scope: "thread"|"all"|"org", capsule?: ContextCapsule) {
  const s = getStats(scope, capsule);
  return [...items].sort((a,b) => (s[b.id]||0) - (s[a.id]||0));
}
function redact(html: string) {
  // lightweight highlight: emails, urls, long numbers
  return html
    .replace(/([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})/gi, '<mark style="background:rgba(244,63,94,.25)">$1</mark>')
    .replace(/(https?:\/\/\S+)/gi, '<mark style="background:rgba(234,179,8,.25)">$1</mark>')
    .replace(/\b(\d{5,})\b/g, '<mark style="background:rgba(16,185,129,.25)">$1</mark>');
}
function buildPreview(cmdId: string, capsule?: ContextCapsule) {
  if (!capsule) return null;
  // map command -> (model, skill)
  const map: Record<string, { model: any; skill: any }> = {
    "validate": { model: "openai:gpt-5-pro", skill: "validate.facts" },
    "storyboard": { model: "openai:gpt-5-pro", skill: "video.summarize" },
    "gen-video": { model: "sora:video", skill: "video.generate" },
    "optimize-prompts": { model: "lukhas-core", skill: "prompt.optimize" },
    "write-email": { model: "lukhas-core", skill: "write.email" },
  };
  const m = map[cmdId]; if (!m) return null;
  const p = toProviderPrompt(m.model, m.skill, capsule);
  return { model: m.model, system: redact(escapeHtml(p.system)), user: redact(escapeHtml(p.user)) };
}
function escapeHtml(s: string) {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

export default function AgentPalette() {
  const pal = usePalette();
  const [recents, setRecents] = useState<Entry[]>([]);
  const commands = useMemo(() => registry().map(c => ({ id: c.id, title: c.title, hint: c.hint, cmd: c })), []);
  const featured = commands.filter(c => c.cmd.featured);
  const [preview, setPreview] = useState<{model:string; system:string; user:string} | null>(null);

  useEffect(() => {
    const onExec = async (e: any) => {
      const q = String(e.detail?.q || "").toLowerCase();
      const match = commands.find(c => c.title.toLowerCase().includes(q) || c.id.includes(q));
      if (match) await run(match);
    };
    document.addEventListener("lukhas:palette-exec", onExec as any);
    return () => document.removeEventListener("lukhas:palette-exec", onExec as any);
  }, [commands]);

  useEffect(() => {
    const onToggle = () => {
      // thread consent toggle bridge
      const ev = new CustomEvent("lukhas:consent-toggle-request");
      document.dispatchEvent(ev);
    };
    document.addEventListener("lukhas:toggle-consent" as any, onToggle);
    return () => document.removeEventListener("lukhas:toggle-consent" as any, onToggle);
  }, []);

  async function run(entry: Entry) {
    const t0 = performance.now();
    await entry.cmd.run({
      capsule: pal.capsule,
      emit: (r) => {
        // proxy to thread canvas via event (avoid prop drill)
        const ev = new CustomEvent("lukhas:canvas-add-card", { detail: r });
        document.dispatchEvent(ev);
      }
    });
    const t1 = performance.now();
    const ms = Math.round(t1 - t0);
    // est. cost (very rough demo): $0.02 per 1k tokens equivalent per 10s
    const cost = (ms/10000)*0.02;
    try {
      localStorage.setItem("lukhas:lastCmdMeta", JSON.stringify({ id: entry.id, ms, cost }));
    } catch {}
    bumpStat(pal.scope, pal.capsule, entry.id);
    setRecents((prev) => {
      const existing = prev.filter(p => p.id !== entry.id);
      return [entry, ...existing].slice(0, MAX_RECENTS);
    });
    pal.close();
  }

  const ranked = rankByStats(commands, pal.scope, pal.capsule);
  const list = pal.mode === "mini"
    ? (pal.query ? filter(commands, pal.query) : ranked.slice(0, 6))
    : (pal.query ? filter(commands, pal.query) : dedupe([...recents, ...ranked, ...featured, ...commands]).slice(0, 24));

  if (pal.mode === "closed") return null;

  return (
    <div
      role="dialog"
      aria-label="Command palette"
      style={{
        position: "fixed",
        left: "50%", transform: "translateX(-50%)",
        top: pal.mode === "mini" ? 12 : 24,
        width: pal.mode === "mini" ? 520 : 720,
        zIndex: 1000,
        background: "#0f1117",
        border: "1px solid #1f2328",
        borderRadius: 14,
        boxShadow: "0 6px 24px rgba(0,0,0,0.35)",
        overflow: "hidden"
      }}
    >
      {/* header / search */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 12px", borderBottom: "1px solid #1f2328" }}>
        <span style={{ fontSize: 12, opacity: 0.75 }}>⌘K</span>
        <input
          autoFocus
          placeholder="Type a command…"
          value={pal.query}
          onChange={(e) => pal.setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const first = list[0]; if (first) run(first);
            }
            if (e.key === "Escape") pal.close();
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); pal.close(); }
          }}
          style={{
            flex: 1, border: "1px solid #1f2328", background: "#0b0d12",
            color: "#e6e6e6", borderRadius: 10, padding: "8px 10px", fontSize: 14
          }}
        />
        {pal.mode === "mini" && (
          <button onClick={() => pal.openFull()} style={btn()}>More ▸</button>
        )}
      </div>
      {/* scope chips */}
      <div style={{ display:"flex", gap:8, padding:"8px 10px", borderBottom:"1px solid #1f2328" }}>
        {(["thread","all","org"] as const).map(s => (
          <button key={s}
            onClick={() => pal.setScope(s)}
            style={{
              padding:"4px 8px", borderRadius:999, border:"1px solid #1f2328",
              background: pal.scope===s ? "rgba(59,130,246,0.15)" : "transparent", color:"#e6e6e6", fontSize:12, cursor:"pointer"
            }}
          >{s==="thread"?"This thread": s==="all"?"All threads":"My org"}</button>
        ))}
      </div>
      {/* results */}
      <div style={{ maxHeight: pal.mode === "mini" ? 220 : 420, overflowY: "auto", padding: 6, display: "grid", gap: 6 }}>
        {list.map((e) => (
          <button key={e.id}
            onMouseDown={(ev) => {
              if (ev.altKey) {
                const p = buildPreview(e.cmd.id as any, pal.capsule);
                if (p) setPreview(p);
                ev.preventDefault(); ev.stopPropagation();
              }
            }}
            onClick={() => run(e)}
            style={{
              textAlign: "left", padding: "10px 12px", borderRadius: 10,
              border: "1px solid #1f2328", background: "transparent", color: "#e6e6e6", cursor: "pointer"
            }}
            onMouseEnter={(ev) => ((ev.currentTarget as HTMLButtonElement).style.background = "rgba(59,130,246,0.10)")}
            onMouseLeave={(ev) => ((ev.currentTarget as HTMLButtonElement).style.background = "transparent")}
          >
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"baseline" }}>
              <div style={{ fontSize: 14 }}>{e.title}</div>
              {/* show last meta if matches */}
              <span className="t-11" style={{opacity:.7}}>
                {(() => {
                  try {
                    const m = JSON.parse(localStorage.getItem("lukhas:lastCmdMeta")||"{}");
                    if (m.id===e.id) return `${m.ms}ms · ~$${m.cost.toFixed(3)}`;
                  } catch {}
                  return "";
                })()}
              </span>
            </div>
            {e.hint && <div className="t-11" style={{ opacity: 0.75 }}>{e.hint}</div>}
          </button>
        ))}
        {list.length === 0 && <div style={{ fontSize: 12, opacity: 0.7, padding: 8 }}>No commands found.</div>}
      </div>
      {!!preview && <PromptPreview {...preview} onClose={() => setPreview(null)} />}
    </div>
  );
}

function filter(items: Entry[], q: string) {
  const s = q.toLowerCase();
  return items.filter(i => i.title.toLowerCase().includes(s) || i.id.includes(s));
}
function dedupe(items: Entry[]) {
  const seen = new Set<string>(); const out: Entry[] = [];
  for (const i of items) { if (!seen.has(i.id)) { seen.add(i.id); out.push(i); } }
  return out;
}
function btn() {
  return { padding: "6px 10px", borderRadius: 10, border: "1px solid #1f2328", background: "transparent", color: "#e6e6e6", cursor: "pointer" } as const;
}