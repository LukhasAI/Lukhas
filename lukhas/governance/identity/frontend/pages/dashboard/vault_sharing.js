// 📂 FILE: dashboard/vault_sharing.js
// 🤝 PURPOSE: Manage symbolic trusted vault sharing between LucasID users

import { useState } from "react";

export default function VaultSharingDashboard() {
  const [status, setStatus] = useState("");
  const [grantorId, setGrantorId] = useState("");
  const [granteeId, setGranteeId] = useState("");
  const [shareType, setShareType] = useState("full_access");
  const [vaultReference, setVaultReference] = useState("");

  const initiateShare = async () => {
    setStatus("🤝 Initiating symbolic vault share...");
    try {
      const response = await fetch("/api/personal_vault/share", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          grantor_id: grantorId,
          grantee_id: granteeId,
          share_type: shareType,
          vault_reference: vaultReference
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Failed to share vault.");
      setStatus(`✅ Share Initiated: ${JSON.stringify(data.details)}`);
    } catch (err) {
      setStatus(`❌ ${err.message}`);
    }
  };

  return (
    <div style={{ padding: "2em", fontFamily: "sans-serif" }}>
      <h2>🤝 Symbolic Vault Sharing</h2>

      <label>
        Grantor ID:
        <input
          type="text"
          value={grantorId}
          onChange={(e) => setGrantorId(e.target.value)}
          style={{ width: "100%", padding: "0.5em", marginTop: "0.5em" }}
        />
      </label><br/><br/>

      <label>
        Grantee ID:
        <input
          type="text"
          value={granteeId}
          onChange={(e) => setGranteeId(e.target.value)}
          style={{ width: "100%", padding: "0.5em", marginTop: "0.5em" }}
        />
      </label><br/><br/>

      <label>
        Share Type:
        <select
          value={shareType}
          onChange={(e) => setShareType(e.target.value)}
          style={{ width: "100%", padding: "0.5em", marginTop: "0.5em" }}
        >
          <option value="full_access">Full Access</option>
          <option value="partial">Partial Access</option>
          <option value="locked">Locked Symbolic Backup</option>
        </select>
      </label><br/><br/>

      <label>
        Vault Reference:
        <input
          type="text"
          value={vaultReference}
          onChange={(e) => setVaultReference(e.target.value)}
          placeholder="e.g. VAULT_123456.enc"
          style={{ width: "100%", padding: "0.5em", marginTop: "0.5em" }}
        />
      </label><br/><br/>

      <button onClick={initiateShare} style={{ padding: "0.75em 1.5em" }}>
        🌉 Share Vault
      </button>

      <p style={{ marginTop: "2em", color: "#666" }}>{status}</p>
    </div>
  );
}
