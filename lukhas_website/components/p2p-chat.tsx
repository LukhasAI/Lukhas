"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import QRGEnvelope from "./qrg-envelope";

type Tier = 1|2|3|4|5;
const LIMITS: Record<Tier, { messages:number; maxFileMB:number; crypto:boolean }> = {
  1:{ messages:100, maxFileMB:5,  crypto:false },
  2:{ messages:300, maxFileMB:25, crypto:false },
  3:{ messages:800, maxFileMB:100,crypto:false },
  4:{ messages:5000,maxFileMB:500,crypto:true  },
  5:{ messages: Infinity, maxFileMB:Infinity, crypto:true }
};

type Msg = { id:string; from:string; text:string; ts:number; attachment?:{ name:string; sizeMB:number }; confidential?:boolean };

export default function P2PChat({ threadId }: { threadId:string }) {
  const tier = Number(localStorage?.getItem("lukhas:tier")||1) as Tier;
  const limits = LIMITS[tier];
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [text, setText] = useState("");
  const [over, setOver] = useState<Msg|null>(null);
  const wrapRef = useRef<HTMLDivElement|null>(null);

  function send(confidential=false){
    if (countToday(msgs) >= (isFinite(limits.messages)? limits.messages: 1e9)) return alert("Message limit reached for your tier.");
    const m:Msg = { id:Math.random().toString(36).slice(2), from:"me", text, ts:Date.now(), confidential };
    setMsgs(v=>[...v, m]); setText("");
  }

  function attach(file:File){
    const sizeMB = +(file.size/1_000_000).toFixed(1);
    if (sizeMB > limits.maxFileMB) return alert(`Attachment exceeds your ${limits.maxFileMB}MB limit`);
    const m:Msg = { id:Math.random().toString(36).slice(2), from:"me", text:`[Attachment] ${file.name}`, ts:Date.now(), attachment:{ name:file.name, sizeMB } };
    setMsgs(v=>[...v, m]);
  }

  useEffect(()=>{ wrapRef.current?.scrollTo({ top: 1e9 }); }, [msgs.length]);

  return (
    <div style={{ display:"grid", gridTemplateRows:"auto 1fr auto", height:"100%" }}>
      <header style={{ padding:"10px 12px", borderBottom:"1px solid var(--line)" }}>
        <strong style={{ fontSize:14 }}>Studio chat</strong>
        <span style={{ fontSize:12, opacity:.6, marginLeft:8 }}>Tier {tier} · {isFinite(limits.messages)? `${limits.messages}/day` : "unlimited"}</span>
      </header>
      <div ref={wrapRef} style={{ overflow:"auto", padding:12, position:"relative" }}>
        {msgs.map(m => (
          <div key={m.id}
               onMouseEnter={()=>setOver(m)} onMouseLeave={()=>setOver(null)}
               style={{ margin:"8px 0", display:"flex", justifyContent:m.from==="me"?"flex-end":"flex-start" }}>
            <div style={{
              maxWidth:420, padding: m.confidential ? "0" : "10px 12px", borderRadius:12,
              background: m.confidential ? "transparent" : (m.from==="me"?"rgba(59,130,246,.15)":"rgba(148,163,184,.12)"),
              border: m.confidential ? "none" : "1px solid var(--line2)", position:"relative"
            }}>
              {m.confidential ? (
                <QRGEnvelope
                  filename={m.attachment?.name || "confidential-message.txt"}
                  sizeMB={m.attachment?.sizeMB || 0.001}
                  level="confidential"
                  onOpen={async () => {
                    // TODO: Implement real E2EE decryption
                    return m.text; // Return the actual message content
                  }}
                />
              ) : (
                <>
                  <div style={{ fontSize:13, lineHeight:1.35, whiteSpace:"pre-wrap" }}>{m.text}</div>
                  {m.attachment && <div style={{ fontSize:12, opacity:.8, marginTop:6 }}>{m.attachment.name} · {m.attachment.sizeMB}MB</div>}
                </>
              )}

              {/* hover-to-expand preview overlay - only for non-confidential messages */}
              {!m.confidential && over?.id===m.id && (
                <div style={{
                  position:"fixed", inset:0, background:"rgba(0,0,0,.35)", display:"grid", placeItems:"center", zIndex:999
                }}>
                  <div style={{ width:640, maxWidth:"90vw", border:"1px solid var(--line)", borderRadius:16, background:"var(--panel)", boxShadow:"var(--shadow-2)", padding:16 }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                      <strong>Preview</strong>
                      <button onClick={()=>setOver(null)} style={btn()}>Close</button>
                    </div>
                    <p style={{ opacity:.9, lineHeight:1.45 }}>{m.text}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      <footer style={{ display:"flex", gap:8, padding:10, borderTop:"1px solid var(--line)" }}>
        <input value={text} onChange={(e)=>setText(e.target.value)} placeholder="Message…" style={input()} />
        <label style={btn()}>Attach
          <input type="file" hidden onChange={(e)=>{ const f=e.target.files?.[0]; if(f) attach(f); }} />
        </label>
        <button onClick={()=>send(false)} style={btn()}>Send</button>
        <button onClick={()=>send(true)} style={{ ...btn(), borderColor:"#a78bfa" }} title="QRG-protect (Tier 4/5 only)" disabled={!limits.crypto}>Send · QRG</button>
      </footer>
    </div>
  );
}
function countToday(v:Msg[]){ const d=new Date(); d.setHours(0,0,0,0); return v.filter(x=>x.ts>=+d).length; }
const input = ()=>({ flex:1, padding:"10px 12px", borderRadius:12, border:"1px solid var(--line2)", background:"#0f131a", color:"var(--text)" } as const);
const btn = ()=>({ padding:"8px 10px", borderRadius:10, border:"1px solid var(--line2)", background:"transparent", color:"var(--text)", cursor:"pointer" } as const);
