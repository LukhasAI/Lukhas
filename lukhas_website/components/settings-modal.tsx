"use client";
import { useEffect } from "react";

export default function SettingsModal({ onClose, children }:{ onClose:()=>void; children:React.ReactNode }){
  useEffect(()=>{
    const onKey=(e:KeyboardEvent)=>{ if(e.key==="Escape") onClose(); };
    window.addEventListener("keydown",onKey);
    return ()=>window.removeEventListener("keydown",onKey);
  },[onClose]);

  return (
    <div
      role="dialog"
      aria-label="Settings"
      onClick={onClose}
      style={{
        position:"fixed",
        inset:0,
        background:"rgba(0,0,0,.45)",
        zIndex:1100,
        display:"grid",
        placeItems:"center"
      }}
    >
      <div
        onClick={e=>e.stopPropagation()}
        className="glass"
        style={{
          width: 920,
          maxWidth:"92vw",
          maxHeight:"86vh",
          overflow:"auto",
          padding:16
        }}
      >
        <header style={{
          display:"flex",
          justifyContent:"space-between",
          alignItems:"center",
          marginBottom:16
        }}>
          <strong style={{fontSize:18, fontWeight:600}}>Settings</strong>
          <button
            onClick={onClose}
            style={{
              border:"1px solid var(--line)",
              background:"transparent",
              color:"var(--text)",
              borderRadius:8,
              padding:"8px 12px",
              cursor:"pointer"
            }}
          >
            Close
          </button>
        </header>
        {children}
      </div>
    </div>
  );
}
