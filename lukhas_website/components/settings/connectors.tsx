"use client";

export default function ConnectorsSettings() {
  const items = [
    { id: "gmail", label: "Gmail" },
    { id: "drive", label: "Google Drive" },
    { id: "tradingview", label: "TradingView" },
    { id: "slack", label: "Slack" },
  ];

  return (
    <section>
      <h2 className="t-18">Connectors</h2>
      <ul style={{ marginTop: 8, display: "grid", gap: 8 }}>
        {items.map(i => (
          <li 
            key={i.id} 
            style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center", 
              border: "1px solid var(--line)", 
              borderRadius: 12, 
              padding: "8px 10px" 
            }}
          >
            <span className="t-13">{i.label}</span>
            <button 
              style={{
                border: "1px solid var(--line)", 
                background: "transparent", 
                color: "var(--text)", 
                borderRadius: 8, 
                padding: "6px 10px",
                cursor: "pointer"
              }}
            >
              Connect
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}