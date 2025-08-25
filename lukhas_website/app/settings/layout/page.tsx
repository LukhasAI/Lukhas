"use client";
import { useEffect, useState } from "react";
import { BarPlacement, BarDepth, loadPrefs, savePrefs } from "@/components/layout-prefs";

export default function LayoutSettings(){
  const [p, setP] = useState(loadPrefs());
  
  useEffect(()=>{ 
    savePrefs(p); 
  }, [p]);
  
  return (
    <main style={{ padding:20, maxWidth:800, margin:"0 auto" }}>
      <h1 style={{ fontSize:24, marginBottom:20, fontWeight:600 }}>Layout Settings</h1>
      
      <section style={box()}>
        <label style={{ fontSize:16, fontWeight:500, display:"block", marginBottom:8 }}>Bar placement</label>
        <p style={{ fontSize:14, opacity:0.8, marginBottom:12 }}>Choose where your widget rails appear</p>
        <div style={{display:"flex", gap:8, flexWrap:"wrap"}}>
          {(["left-right","right-left","top-bottom","bottom-top"] as BarPlacement[]).map(v=>(
            <button 
              key={v} 
              onClick={()=>setP({...p, placement:v})} 
              style={chip(p.placement===v)}
            >
              {v.replace("-"," → ")}
            </button>
          ))}
        </div>
      </section>
      
      <section style={box()}>
        <label style={{ fontSize:16, fontWeight:500, display:"block", marginBottom:8 }}>Bar depth</label>
        <p style={{ fontSize:14, opacity:0.8, marginBottom:12 }}>Control the height/width of widget rails</p>
        <div style={{display:"flex", gap:8}}>
          {(["full","half"] as BarDepth[]).map(v=>(
            <button 
              key={v} 
              onClick={()=>setP({...p, depth:v})} 
              style={chip(p.depth===v)}
            >
              {v === "full" ? "Full height" : "Compact (50%)"}
            </button>
          ))}
        </div>
      </section>
      
      <section style={box()}>
        <label style={{ fontSize:16, fontWeight:500, display:"block", marginBottom:8 }}>Meta-adaptive rails</label>
        <p style={{fontSize:14, opacity:.8, marginBottom:12, lineHeight:1.5}}>
          Let Studio rearrange widgets based on your (local, consented) usage patterns. 
          All data stays on your device - no tracking or analytics are sent to our servers.
        </p>
        <button 
          onClick={()=>setP({...p, metaAdaptive: !p.metaAdaptive})} 
          style={{...chip(p.metaAdaptive), fontSize:14}}
        >
          {p.metaAdaptive ? "✓ Enabled" : "Disabled"}
        </button>
        {p.metaAdaptive && (
          <div style={{ marginTop:8, padding:10, background:"rgba(59,130,246,0.1)", borderRadius:8, fontSize:12, opacity:0.9 }}>
            <strong>Privacy note:</strong> Usage data is stored locally in your browser only. You can clear it anytime via browser settings.
          </div>
        )}
      </section>
      
      <section style={box()}>
        <label style={{ fontSize:16, fontWeight:500, display:"block", marginBottom:8 }}>Current Configuration</label>
        <div style={{ fontSize:14, opacity:0.8, fontFamily:"ui-monospace, monospace" }}>
          <div>Placement: <strong>{p.placement}</strong></div>
          <div>Depth: <strong>{p.depth}</strong></div>
          <div>Meta-adaptive: <strong>{p.metaAdaptive ? "on" : "off"}</strong></div>
        </div>
      </section>
      
      <div style={{ marginTop:24, padding:16, border:"1px solid var(--line2)", borderRadius:12, background:"rgba(251,191,36,0.05)" }}>
        <h3 style={{ fontSize:14, fontWeight:600, marginBottom:8 }}>🚀 Tier 4+ Features</h3>
        <p style={{ fontSize:13, opacity:0.9, lineHeight:1.4 }}>
          Upgrade to Tier 4 or higher to unlock drag-and-drop widget reordering, terminal widget, 
          and advanced customization options.
        </p>
      </div>
    </main>
  );
}

const box = ()=>({ 
  border:"1px solid var(--line)", 
  borderRadius:16, 
  padding:20, 
  marginBottom:16, 
  background:"var(--panel)"
} as const);

const chip = (on:boolean)=>({ 
  padding:"8px 16px", 
  border:"1px solid var(--line)", 
  borderRadius:999, 
  background:on?"rgba(59,130,246,.15)":"transparent", 
  color:"var(--text)", 
  cursor:"pointer",
  fontSize:14,
  fontWeight: on ? 500 : 400,
  transition: "all 0.2s ease"
} as const);