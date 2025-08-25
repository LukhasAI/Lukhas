"use client";
import React from "react";
import { getTier } from "./layout-prefs";

export type WidgetMeta = {
  id: "conversations"|"delivery"|"trading"|"terminal";
  title: string; 
  minTier: 1|2|3|4|5;
  node: React.ReactNode;
  action?: { label: string; onClick: ()=>void };
};

function Clamp({children}:{children:React.ReactNode}){ 
  return <p style={{opacity:.85, display:"-webkit-box", WebkitLineClamp:2, WebkitBoxOrient:"vertical", overflow:"hidden"}}>{children}</p>; 
}

export const Widgets: WidgetMeta[] = [
  { 
    id: "conversations", 
    title: "Past conversations", 
    minTier: 1, 
    node: <Clamp>Recent threads (stub)</Clamp>, 
    action: { label: "Open", onClick() { location.href = "/studio"; } } 
  },
  { 
    id: "delivery", 
    title: "Delivery tracker", 
    minTier: 1, 
    node: <Clamp>Uber-style tracking (stub)</Clamp>, 
    action: { label: "Track", onClick() { alert("Open tracker"); } } 
  },
  { 
    id: "trading", 
    title: "Trading view", 
    minTier: 2, 
    node: <Clamp>Mini charts (stub)</Clamp>, 
    action: { label: "Open", onClick() { alert("Open charts"); } } 
  },
  { id: "terminal", title: "Terminal", minTier: 4, node: <MiniTerminal/> },
];

export function visibleWidgets(ids: string[]) {
  const tier = getTier();
  return ids.map(id => Widgets.find(w=>w.id===id)).filter(Boolean).filter((w:any)=>tier>=w.minTier) as WidgetMeta[];
}

function MiniTerminal(){
  const [log, setLog] = React.useState<string[]>(["lukhas% echo hello","hello"]);
  const [cmd, setCmd] = React.useState("");
  
  function executeCommand() {
    if (!cmd.trim()) return;
    
    const newCmd = `lukhas% ${cmd}`;
    let output = "";
    
    // Simple command simulation
    if (cmd === "clear") {
      setLog([]);
      setCmd("");
      return;
    } else if (cmd.startsWith("echo ")) {
      output = cmd.slice(5);
    } else if (cmd === "help") {
      output = "Available: echo, clear, ls, pwd, whoami";
    } else if (cmd === "ls") {
      output = "studio.tsx  components/  packages/  .env.local";
    } else if (cmd === "pwd") {
      output = "/Users/lukhas/studio";
    } else if (cmd === "whoami") {
      output = "lukhas-user";
    } else {
      output = `${cmd}: command not found`;
    }
    
    setLog(v => [...v, newCmd, output]);
    setCmd("");
  }
  
  return (
    <div>
      <div style={{fontFamily:"ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace", fontSize:12, border:"1px solid var(--line2)", borderRadius:10, padding:8, height:140, overflow:"auto", background:"#0b0d12"}}>
        {log.map((l,i)=><div key={i} style={{color: i % 2 === 0 ? "#60a5fa" : "var(--text)"}}>{l}</div>)}
      </div>
      <div style={{display:"flex", gap:6, marginTop:6}}>
        <input 
          value={cmd} 
          onChange={e=>setCmd(e.target.value)}
          onKeyDown={e => e.key === "Enter" && executeCommand()}
          placeholder="type a command…" 
          style={{flex:1, border:"1px solid var(--line2)", borderRadius:8, background:"#0f131a", color:"var(--text)", padding:"6px 8px"}}
        />
        <button onClick={executeCommand} style={btn()}>Run</button>
      </div>
    </div>
  );
}

const btn = ()=>({ padding:"6px 10px", border:"1px solid var(--line2)", borderRadius:8, background:"transparent", color:"var(--text)", cursor:"pointer"} as const);