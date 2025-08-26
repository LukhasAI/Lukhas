"use client";

export default function WalletSettings() {
  const tier = typeof window !== 'undefined'
    ? Number(localStorage.getItem("lukhas:tier") || 1)
    : 1;

  return (
    <section>
      <h2 className="t-18">Wallet & Tokens</h2>
      <div className="t-13" style={{ marginTop: 8 }}>
        Tier: {tier}
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
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
          View WΛLLET
        </button>
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
          Export keys
        </button>
      </div>
    </section>
  );
}
