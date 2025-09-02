"use client";
import { useState } from "react";

interface ComposerActionsProps {
  onAction: (action: string) => void;
}

export default function ComposerActions({ onAction }: ComposerActionsProps) {
  const [hovered, setHovered] = useState<string | null>(null);

  const actions = [
    { id: "email", icon: "✉️", label: "Compose Email", desc: "Draft a professional email" },
    { id: "research", icon: "🔍", label: "Research", desc: "Deep research with citations" },
    { id: "code", icon: "💻", label: "Code", desc: "Generate or debug code" },
    { id: "creative", icon: "🎨", label: "Creative", desc: "Creative writing & brainstorming" },
    { id: "analysis", icon: "📊", label: "Analyze", desc: "Data analysis & insights" },
    { id: "summary", icon: "📝", label: "Summarize", desc: "Condense information" },
  ];

  return (
    <div
      className="composer-actions-overlay panel"
      style={{
        display: "flex",
        gap: 6,
        padding: "8px 12px",
        backdropFilter: "saturate(140%) blur(18px)",
        borderRadius: "var(--radius-md)",
        boxShadow: "var(--shadow-1)",
      }}
    >
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => onAction(action.id)}
          onMouseEnter={() => setHovered(action.id)}
          onMouseLeave={() => setHovered(null)}
          title={action.desc}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "6px 10px",
            border: "1px solid var(--line2)",
            background: hovered === action.id ? "var(--panel-heavy)" : "transparent",
            borderRadius: "var(--radius-sm)",
            cursor: "pointer",
            fontSize: 12,
            color: "var(--text)",
            transition: "background 0.15s ease",
          }}
        >
          <span style={{ fontSize: 14 }}>{action.icon}</span>
          <span style={{ whiteSpace: "nowrap" }}>{action.label}</span>
        </button>
      ))}
    </div>
  );
}
