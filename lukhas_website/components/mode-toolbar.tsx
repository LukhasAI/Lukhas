"use client";
import { useMode } from "./mode-context";
import { Send, Calendar, Link, Italic, Bold, Underline, List, CheckSquare, Play, Sparkles } from "lucide-react";

const btn = { 
  padding: "6px 10px", 
  border: "1px solid var(--line)", 
  background: "transparent", 
  color: "var(--text)", 
  borderRadius: 8, 
  cursor: "pointer" 
} as const;

export default function ModeToolbar() {
  const { mode } = useMode();
  
  if (mode === "email") return (
    <div style={{ display: "flex", gap: 8 }}>
      <button style={btn} title="Send"><Send size={14} /></button>
      <button style={btn} title="Schedule"><Calendar size={14} /></button>
      <button style={btn} title="Attach"><Link size={14} /></button>
    </div>
  );
  
  if (mode === "doc") return (
    <div style={{ display: "flex", gap: 8 }}>
      <button style={btn} title="Bold"><Bold size={14} /></button>
      <button style={btn} title="Italic"><Italic size={14} /></button>
      <button style={btn} title="Underline"><Underline size={14} /></button>
      <button style={btn} title="List"><List size={14} /></button>
    </div>
  );
  
  if (mode === "code") return (
    <div style={{ display: "flex", gap: 8 }}>
      <button style={btn} title="Run tests"><CheckSquare size={14} /></button>
      <button style={btn} title="Preview"><Play size={14} /></button>
    </div>
  );
  
  if (mode === "message") return (
    <div style={{ display: "flex", gap: 8 }}>
      <button style={btn} title="Suggest reply"><Sparkles size={14} /></button>
    </div>
  );
  
  return null;
}