"use client";
import { useState } from "react";

export type CardKind = "validation" | "storyboard" | "draft" | "text";
export type ResultCardData = {
  id: string;
  kind: CardKind;
  title: string;
  body: string;
  model?: string;
  meta?: Record<string, any>;
  ts?: number;
};

export default function ResultCard({ data }: { data: ResultCardData }) {
  const [expanded, setExpanded] = useState(false);
  const ts = data.ts ? new Date(data.ts).toLocaleTimeString() : "";
  return (
    <article
      role="group"
      aria-label={`${data.kind} card`}
      style={{
        width: 520,
        minHeight: 260,
        border: "1px solid var(--line)",
        borderRadius: 14,
        background: "rgba(16,20,29,0.66)",
        color: "var(--text)",
        padding: 16,
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
        gap: 10,
        boxShadow: "var(--shadow-1)"
      }}
    >
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            aria-hidden
            style={{
              display: "inline-block",
              width: 8,
              height: 8,
              borderRadius: 999,
              background:
                data.kind === "validation" ? "#22c55e" :
                data.kind === "storyboard" ? "#a78bfa" :
                data.kind === "draft" ? "#3b82f6" : "#94a3b8",
            }}
          />
          <strong style={{ fontSize: 14 }}>{data.title}</strong>
        </div>
        <small style={{ opacity: 0.6 }}>{data.model ? `via ${data.model}` : ""} {ts ? `· ${ts}` : ""}</small>
      </header>

      <main style={{ whiteSpace: "pre-wrap", lineHeight: 1.45, opacity: 0.95, overflow: "auto" }}>
        {renderBody(data)}
      </main>

      <footer style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button
          onClick={() => {
            navigator.clipboard?.writeText(data.body).catch(() => {});
          }}
          title="Copy"
          style={btn()}
        >
          Copy
        </button>
        <button onClick={() => setExpanded((v) => !v)} title="Expand" style={btn()}>
          {expanded ? "Collapse" : "Expand"}
        </button>
      </footer>
    </article>
  );
}

function btn() {
  return {
    padding: "8px 10px",
    borderRadius: 10,
    border: "1px solid #2a2f37",
    background: "transparent",
    color: "#e6e6e6",
    cursor: "pointer",
  } as const;
}

function renderBody(data: ResultCardData) {
  if (data.kind === "validation") {
    return (
      <div>
        <p style={{ marginBottom: 8 }}>{data.body}</p>
        {Array.isArray(data.meta?.issues) && data.meta!.issues.length > 0 && (
          <ul style={{ marginTop: 10, paddingLeft: 18, opacity: 0.9 }}>
            {data.meta!.issues.map((s: string, i: number) => <li key={i}>{s}</li>)}
          </ul>
        )}
      </div>
    );
  }
  if (data.kind === "storyboard") {
    const scenes: string[] = data.meta?.scenes || [];
    return (
      <div style={{ display: "grid", gap: 8 }}>
        <p>{data.body}</p>
        {scenes.length > 0 && (
          <ol style={{ paddingLeft: 18, opacity: 0.9 }}>
            {scenes.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        )}
      </div>
    );
  }
  // draft/text default
  return <p>{data.body}</p>;
}
