"use client";
import { useEffect, useState } from "react";

type TabId = "email" | "social" | "dm";
type Item = { id: string; from?: string; handle?: string; text: string; ts: string; unread?: boolean; source: TabId };

const MOCK: Item[] = [
  { id: "e1", source: "email", from: "Ari · partner@brand.com", text: "Sponsorship brief (NIAS opt-in terms)", ts: "10:24", unread: true },
  { id: "s1", source: "social", handle: "@visual_minds", text: "Loved your Lucas canvas demo!", ts: "09:40", unread: true },
  { id: "d1", source: "dm", handle: "@sam", text: "Ship the demo with tokens next week?", ts: "Yesterday" },
  { id: "e2", source: "email", from: "Ops · noreply@stripe.com", text: "Payout received — 50/50 split confirmed", ts: "Yesterday" },
  { id: "s2", source: "social", handle: "@creator_xyz", text: "Collab on storyboard pack?", ts: "Mon" },
];

export default function UnifiedInbox() {
  const enabled = (process.env.NEXT_PUBLIC_COMMUNICATIONS_HUB ?? "true") !== "false";
  const [tab, setTab] = useState<TabId>("email");
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => { if (enabled) setItems(MOCK); }, [enabled]);
  if (!enabled) return <p style={{ opacity: 0.6 }}>Communications Hub disabled.</p>;

  const filtered = items.filter(i => i.source === tab);
  const counts = {
    email: items.filter(i => i.source === "email" && i.unread).length,
    social: items.filter(i => i.source === "social" && i.unread).length,
    dm: items.filter(i => i.source === "dm" && i.unread).length,
  };

  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 8 }}>
        <TabBtn active={tab === "email"} onClick={() => setTab("email")} label={`Email${counts.email ? ` (${counts.email})` : ""}`} />
        <TabBtn active={tab === "social"} onClick={() => setTab("social")} label={`Social${counts.social ? ` (${counts.social})` : ""}`} />
        <TabBtn active={tab === "dm"} onClick={() => setTab("dm")} label={`DMs${counts.dm ? ` (${counts.dm})` : ""}`} />
      </div>
      <div style={{ display: "grid", gap: 6 }}>
        {filtered.length === 0 && <p style={{ opacity: 0.6 }}>Nothing here (yet).</p>}
        {filtered.map(i => (
          <div key={i.id} style={{
            border: "1px solid #1f2328",
            borderRadius: 10,
            padding: 10,
            background: i.unread ? "rgba(59,130,246,0.10)" : "transparent",
            display: "grid",
            gap: 4,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
              <strong style={{ fontSize: 12 }}>{i.from || i.handle || "Unknown"}</strong>
              <span style={{ fontSize: 11, opacity: 0.7 }}>{i.ts}</span>
            </div>
            <div style={{ fontSize: 13, opacity: 0.85 }}>{i.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TabBtn({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "6px 10px",
        borderRadius: 10,
        border: `1px solid ${active ? "#3b82f6" : "#1f2328"}`,
        background: active ? "rgba(59,130,246,0.10)" : "transparent",
        color: "#e6e6e6",
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
}