"use client";
import { useEffect, useState } from "react";

export default function CMP() {
  const [show, setShow] = useState(false);
  
  useEffect(() => {
    const v = localStorage.getItem("lukhas:consent");
    if (!v) setShow(true);
  }, []);
  
  if (!show) return null;
  
  return (
    <div style={{ 
      position: "fixed", bottom: 16, left: 16, right: 16, background: "#0f1117",
      border: "1px solid #1f2328", padding: 12, borderRadius: 12, zIndex: 100 
    }}>
      <strong>Cookie & Sponsorship Preferences</strong>
      <p style={{ opacity: 0.8 }}>Choose Essential Mode (no sponsors/analytics) or Opt-in to NIAS for rewards.</p>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button 
          onClick={() => { 
            localStorage.setItem("lukhas:consent", JSON.stringify({ essential: true })); 
            setShow(false); 
          }}
          style={{
            backgroundColor: "#374151",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          Essential Mode
        </button>
        <button 
          onClick={() => { 
            localStorage.setItem("lukhas:consent", JSON.stringify({ sponsors: true, analytics: true })); 
            setShow(false); 
          }}
          style={{
            backgroundColor: "#059669",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          Opt-in (earn rewards)
        </button>
      </div>
    </div>
  );
}