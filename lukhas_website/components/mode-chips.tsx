"use client";
import { useMode } from "./mode-context";
import { Mail, FileText, Code2, MessageSquare } from "lucide-react";

const items = [
  { id: "email", label: "Email", Icon: Mail },
  { id: "doc", label: "Doc", Icon: FileText },
  { id: "code", label: "Code", Icon: Code2 },
  { id: "message", label: "Message", Icon: MessageSquare },
] as const;

export default function ModeChips() {
  const { mode, setMode } = useMode();

  return (
    <div style={{ display: "flex", gap: 8 }}>
      {items.map(({ id, label, Icon }) => (
        <button
          key={id}
          onClick={() => setMode(id as any)}
          title={label}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "6px 10px",
            border: "1px solid var(--line)",
            borderRadius: 999,
            background: mode === id ? "rgba(91,138,255,.15)" : "transparent",
            color: "var(--text)",
            cursor: "pointer"
          }}
        >
          <Icon size={14} />
          <span className="t-13">{label}</span>
        </button>
      ))}
    </div>
  );
}
