

// 📂 FILE: dashboard/logs.js
// 📜 PURPOSE: View symbolic session + audit logs

import { useEffect, useState } from "react";

export default function LogsDashboard() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/logs/sessions")
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch session logs");
        return res.json();
      })
      .then(setLogs)
      .catch(err => setError(err.message));
  }, []);

  if (error) return <div style={{ padding: "2em", color: "red" }}>⚠️ {error}</div>;
  if (!logs || logs.length === 0) return <div style={{ padding: "2em" }}>🔄 No logs found yet...</div>;

  return (
    <div style={{ padding: "2em", fontFamily: "sans-serif" }}>
      <h2>📜 Session Logs</h2>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: "0.5em", borderBottom: "1px solid #ccc" }}>Timestamp</th>
            <th style={{ textAlign: "left", padding: "0.5em", borderBottom: "1px solid #ccc" }}>User ID</th>
            <th style={{ textAlign: "left", padding: "0.5em", borderBottom: "1px solid #ccc" }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => (
            <tr key={i}>
              <td style={{ padding: "0.5em" }}>{log.timestamp}</td>
              <td style={{ padding: "0.5em" }}>{log.user_id}</td>
              <td style={{ padding: "0.5em" }}>{log.action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
