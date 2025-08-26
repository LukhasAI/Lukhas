"use client";
import { useState } from "react";
import LayoutSettings from "@/app/settings/layout/page";
import PrivacySettings from "@/components/settings/privacy";
import ConnectorsSettings from "@/components/settings/connectors";
import WalletSettings from "@/components/settings/wallet";

export default function SettingsTabs() {
  const tabs = ["Layout", "Privacy & Consent", "Connectors", "Wallet & Tokens"] as const;
  const [i, setI] = useState(0);

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
        {tabs.map((t, idx) => (
          <button
            key={t}
            onClick={() => setI(idx)}
            style={{
              padding: "6px 10px",
              border: "1px solid var(--line)",
              borderRadius: 999,
              background: i === idx ? "rgba(91,138,255,.15)" : "transparent",
              color: "var(--text)",
              cursor: "pointer"
            }}
          >
            {t}
          </button>
        ))}
      </div>
      {i === 0 && <LayoutSettings />}
      {i === 1 && <PrivacySettings />}
      {i === 2 && <ConnectorsSettings />}
      {i === 3 && <WalletSettings />}
    </div>
  );
}
