// 📂 FILE: dashboard/compliance.js
// 🛡️ PURPOSE: View symbolic compliance status from backend

import { useEffect, useState } from "react";

export default function ComplianceDashboard() {
  const [compliance, setCompliance] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/compliance/status")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch compliance data");
        return res.json();
      })
      .then(setCompliance)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div style={{ padding: "2em", color: "red" }}>⚠️ {error}</div>;
  if (!compliance || Object.keys(compliance).length === 0)
    return <div style={{ padding: "2em" }}>🔄 Loading compliance matrix...</div>;

  return (
    <div style={{ padding: "2em", fontFamily: "sans-serif" }}>
      <h2>🛡️ LucasID Compliance Matrix</h2>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "0.5em" }}>Framework</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "0.5em" }}>Status</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "0.5em" }}>Description</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(compliance).map(([key, value]) => (
            <tr key={key}>
              <td style={{ padding: "0.5em", fontWeight: "bold" }}>{key}</td>
              <td style={{ padding: "0.5em" }}>{value.status}</td>
              <td style={{ padding: "0.5em", color: "#666" }}>{value.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
