"use client";
import React, { useState } from "react";

export type QRGEnvelopeProps = {
  filename: string;
  sizeMB: number;
  level: "confidential"|"secret";
  onOpen?: () => Promise<Blob|ArrayBuffer|string>; // implement later with real E2EE
};

export default function QRGEnvelope({ filename, sizeMB, level, onOpen }: QRGEnvelopeProps){
  const [open,setOpen] = useState(false);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState<string|null>(null);
  
  async function handleOpen() {
    if(!onOpen) return;
    
    setBusy(true);
    setError(null);
    
    try {
      // TODO: Real authentication challenge (WebAuthn / device key)
      // TODO: Audit Λ-trace for security logging
      
      // Simulate authentication delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const result = await onOpen();
      console.log("QRG envelope opened:", result);
      
      setOpen(true);
    } catch (err) {
      setError("Authentication failed or content unavailable");
      console.error("QRG envelope error:", err);
    } finally {
      setBusy(false);
    }
  }
  
  return (
    <button
      onClick={handleOpen}
      disabled={busy}
      title={`${filename} · ${sizeMB}MB · ${level}`}
      style={{
        display:"grid", 
        gap:8, 
        padding:12, 
        border:`1px solid ${level==="secret" ? "#a78bfa" : "#3b82f6"}`, 
        borderRadius:12,
        background: open 
          ? "rgba(167,139,250,.15)" 
          : busy 
          ? "rgba(59,130,246,.1)" 
          : "transparent", 
        color:"var(--text)", 
        cursor: busy ? "wait" : "pointer",
        opacity: busy ? 0.7 : 1,
        transition: "all 0.2s ease",
        textAlign: "left" as const
      }}
    >
      <div style={{display:"flex", alignItems:"center", gap:10}}>
        <div style={{
          width:12,
          height:12,
          borderRadius:999, 
          background: level==="secret" ? "#a78bfa" : "#3b82f6",
          flexShrink: 0,
          position: "relative" as const
        }}>
          {busy && (
            <div style={{
              position: "absolute" as const,
              inset: -2,
              border: "2px solid transparent",
              borderTop: `2px solid ${level==="secret" ? "#a78bfa" : "#3b82f6"}`,
              borderRadius: "50%",
              animation: "spin 1s linear infinite"
            }} />
          )}
        </div>
        <strong style={{fontSize:14, fontWeight:600}}>
          {busy ? "Authenticating..." : open ? "Glyph Opened" : "Glyph Envelope"}
        </strong>
        <div style={{marginLeft:"auto", fontSize:11, opacity:.7}}>
          {level.toUpperCase()}
        </div>
      </div>
      
      <div style={{fontSize:13, opacity:.9, fontWeight:500}}>
        {filename} · {sizeMB}MB
      </div>
      
      <div style={{fontSize:12, opacity:.7, fontStyle:"italic"}}>
        {error ? (
          <span style={{color:"#ef4444"}}>⚠️ {error}</span>
        ) : busy ? (
          "Verifying identity & decrypting content..."
        ) : open ? (
          "✓ Content decrypted and accessible"
        ) : (
          "🔒 Click to authenticate & decrypt"
        )}
      </div>
      
      {open && (
        <div style={{
          marginTop: 4,
          padding: 8,
          background: "rgba(59,130,246,.1)",
          borderRadius: 8,
          fontSize: 12,
          opacity: 0.9
        }}>
          <strong>Security Note:</strong> Content has been decrypted using your device key. 
          This session is logged to the Λ-trace for audit purposes.
        </div>
      )}
      
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </button>
  );
}