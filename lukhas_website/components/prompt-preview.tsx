"use client";
import React from "react";

export default function PromptPreview({
  model, system, user, onClose,
}: { model: string; system: string; user: string; onClose: () => void }) {
  return (
    <div role="dialog" aria-label="Prompt preview"
      style={{
        position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
        display: "grid", placeItems: "center", zIndex: 1100
      }}
      onClick={onClose}
    >
      <div onClick={(e) => e.stopPropagation()}
        style={{
          width: 760, maxWidth: "92vw",
          background: "#0f1117", color: "#e6e6e6",
          border: "1px solid #1f2328", borderRadius: 16,
          boxShadow: "0 18px 60px rgba(0,0,0,.55)",
          display: "grid", gap: 12, padding: 16
        }}
      >
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <strong style={{ fontSize: 14 }}>Prompt preview · {model}</strong>
          <button onClick={onClose} style={btn()}>Close</button>
        </header>
        <section style={box()}>
          <div style={label()}>System</div>
          <pre style={pre()} dangerouslySetInnerHTML={{ __html: system }} />
        </section>
        <section style={box()}>
          <div style={label()}>User</div>
          <pre style={pre()} dangerouslySetInnerHTML={{ __html: user }} />
        </section>
        <footer style={{ fontSize: 12, opacity: .75 }}>
          Redactions highlighted. Hold <kbd>Alt</kbd> on a command to see this preview.
        </footer>
      </div>
    </div>
  );
}
const btn = () => ({ padding:"6px 10px", borderRadius:10, border:"1px solid #1f2328", background:"transparent", color:"#e6e6e6", cursor:"pointer" } as const);
const box = () => ({ border:"1px solid #1f2328", borderRadius:12, padding:12, background:"#0b0d12" } as const);
const label = () => ({ fontSize:12, opacity:.75, marginBottom:6 } as const);
const pre = () => ({ margin:0, whiteSpace:"pre-wrap", lineHeight:1.35 } as const);
